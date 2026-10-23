"""Protect PyPI metadata decisions with synthetic responses and an isolated cache."""

from unittest.mock import Mock, patch

import requests
from bs4 import BeautifulSoup
from django.core.cache import cache
from django.template import Context, Template
from django.test import SimpleTestCase, override_settings

from webapp.pages.templatetags.pypi_tags import package_metadata, pypi_info


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "pypi-tags-tests",
        }
    }
)
class PyPITagsTests(SimpleTestCase):
    def setUp(self) -> None:
        cache.clear()
        self.addCleanup(cache.clear)
        self.get = self.enterContext(
            patch("webapp.pages.templatetags.pypi_tags.requests.get")
        )
        self.response = Mock(spec=requests.Response)
        self.response.json.return_value = {"info": {"version": "1.2.3"}}
        self.get.return_value = self.response

    def test_invalid_names_return_unavailable_without_a_request(self) -> None:
        for name in (None, "", "../example", "example/name", "example name", "a" * 256):
            with self.subTest(name=name):
                self.assertEqual(package_metadata(name), {"release": None})

        self.get.assert_not_called()

    def test_release_date_prefers_iso_and_accepts_legacy_timestamp(self) -> None:
        examples = (
            (
                "example-iso",
                {
                    "upload_time_iso_8601": "2026-10-20T10:30:00Z",
                    "upload_time": "2026-10-19T10:30:00",
                },
                "20 Oct 2026",
            ),
            (
                "example-legacy",
                {"upload_time": "2026-10-19T10:30:00"},
                "19 Oct 2026",
            ),
        )
        for name, release, expected_date in examples:
            with self.subTest(name=name):
                self.response.json.return_value = {
                    "info": {"version": "1.2.3"},
                    "releases": {"1.2.3": [release]},
                }

                self.assertEqual(
                    package_metadata(name),
                    {"release": "1.2.3", "release_date": expected_date},
                )

    def test_version_is_usable_without_release_date_data(self) -> None:
        self.assertEqual(package_metadata("example-package"), {"release": "1.2.3"})

    def test_equivalent_names_share_hour_cached_metadata(self) -> None:
        with patch(
            "webapp.pages.templatetags.pypi_tags.cache.set", wraps=cache.set
        ) as cache_set:
            for name in ("Example._-Package", "example-package", "EXAMPLE_PACKAGE"):
                with self.subTest(name=name):
                    self.assertEqual(package_metadata(name), {"release": "1.2.3"})

        self.get.assert_called_once_with(
            "https://pypi.org/pypi/example-package/json", timeout=(2, 3)
        )
        cache_set.assert_called_once()
        self.assertEqual(cache_set.call_args.args[2], 3600)

    def test_request_failures_are_cached_for_five_minutes(self) -> None:
        for error in (
            requests.Timeout("Timed out"),
            requests.ConnectionError("Offline"),
        ):
            with self.subTest(error=type(error).__name__):
                cache.clear()
                self.get.reset_mock()
                self.get.side_effect = error
                with patch(
                    "webapp.pages.templatetags.pypi_tags.cache.set", wraps=cache.set
                ) as cache_set:
                    self.assertEqual(
                        package_metadata("example-package"), {"release": None}
                    )
                    self.assertEqual(
                        package_metadata("example-package"), {"release": None}
                    )

                self.get.assert_called_once()
                cache_set.assert_called_once()
                self.assertEqual(cache_set.call_args.args[2], 300)

    def test_http_error_does_not_use_the_response_metadata(self) -> None:
        self.response.raise_for_status.side_effect = requests.HTTPError("Not found")

        self.assertEqual(package_metadata("example-package"), {"release": None})
        self.response.json.assert_not_called()

    def test_invalid_json_returns_unavailable(self) -> None:
        self.response.json.side_effect = requests.exceptions.JSONDecodeError(
            "Expecting value", "not JSON", 0
        )

        self.assertEqual(package_metadata("example-package"), {"release": None})

    def test_malformed_metadata_returns_unavailable(self) -> None:
        examples = (
            None,
            {},
            {"info": None},
            {"info": {"version": ""}},
            {"info": {"version": None}},
            {"info": {"version": 123}},
        )
        for payload in examples:
            with self.subTest(payload=payload):
                cache.clear()
                self.response.json.return_value = payload

                self.assertEqual(package_metadata("example-package"), {"release": None})

    def test_unavailable_metadata_keeps_resource_links_in_the_component(self) -> None:
        self.get.side_effect = requests.Timeout("Timed out")
        html = Template(
            "{% load pypi_tags %}{% pypi_info package_name repository_url %}"
        ).render(
            Context(
                {
                    "package_name": "example-package",
                    "repository_url": "https://github.com/example/project",
                }
            )
        )
        soup = BeautifulSoup(html, "html.parser")

        self.assertIn("Release information is currently unavailable.", soup.get_text())
        self.assertCountEqual(
            [link["href"] for link in soup.find_all("a")],
            [
                "https://github.com/example/project",
                "https://pypi.org/project/example-package/",
            ],
        )

    def test_invalid_name_omits_the_pypi_link_and_keeps_the_repository(self) -> None:
        self.assertEqual(
            pypi_info("../example", "https://github.com/example/project"),
            {
                "release": None,
                "pypi_url": "",
                "repository_url": "https://github.com/example/project",
            },
        )
        self.get.assert_not_called()
