from unittest.mock import Mock, patch

import requests
from django.test import SimpleTestCase

from webapp.pages.templatetags.pypi_tags import (
    _normalize_package_name,
    _parse_release,
    package_metadata,
    pypi_info,
)


class PyPIMetadataTests(SimpleTestCase):
    def test_cached_successes_and_failures_skip_http(self):
        for cached in ({"release": "1.2.3"}, {"release": None}):
            with self.subTest(cached=cached):
                with (
                    patch("webapp.pages.templatetags.pypi_tags.cache") as cache,
                    patch("webapp.pages.templatetags.pypi_tags.requests.get") as get,
                ):
                    cache.get.return_value = cached
                    self.assertEqual(package_metadata("Demo_Package"), cached)
                    cache.get.assert_called_once_with("pypi-metadata:demo-package")
                    get.assert_not_called()
                    cache.set.assert_not_called()

    def test_missing_or_invalid_versions_use_failure_cache_lifetime(self):
        for info in ({}, {"version": ""}, {"version": None}, {"version": 123}):
            with self.subTest(info=info):
                response = Mock()
                response.json.return_value = {"info": info}
                with (
                    patch(
                        "webapp.pages.templatetags.pypi_tags.requests.get",
                        return_value=response,
                    ),
                    patch("webapp.pages.templatetags.pypi_tags.cache") as cache,
                ):
                    cache.get.return_value = None
                    self.assertEqual(package_metadata("demo"), {"release": None})
                    cache.set.assert_called_once_with(
                        "pypi-metadata:demo", {"release": None}, 300
                    )

    def test_normalizes_case_and_separators(self):
        self.assertEqual(_normalize_package_name("Demo..__--Package"), "demo-package")

    def test_empty_names_skip_http_and_have_no_pypi_link(self):
        with patch("webapp.pages.templatetags.pypi_tags.requests.get") as get:
            for name in (None, ""):
                with self.subTest(name=name):
                    self.assertEqual(
                        pypi_info(name, "https://example.com/source"),
                        {
                            "release": None,
                            "pypi_url": "",
                            "repository_url": "https://example.com/source",
                        },
                    )
            get.assert_not_called()

    def test_failed_lookup_encodes_name_and_keeps_resource_links(self):
        response = Mock()
        response.raise_for_status.side_effect = requests.HTTPError("Not found")
        with (
            patch(
                "webapp.pages.templatetags.pypi_tags.requests.get",
                return_value=response,
            ) as get,
            patch("webapp.pages.templatetags.pypi_tags.cache") as cache,
        ):
            cache.get.return_value = None
            self.assertEqual(
                pypi_info("Missing/Package?name", "https://example.com/source"),
                {
                    "release": None,
                    "pypi_url": "https://pypi.org/project/Missing%2FPackage%3Fname/",
                    "repository_url": "https://example.com/source",
                },
            )
            get.assert_called_once_with(
                "https://pypi.org/pypi/missing%2Fpackage%3Fname/json", timeout=(2, 3)
            )
            cache.set.assert_called_once_with(
                "pypi-metadata:missing%2Fpackage%3Fname", {"release": None}, 300
            )

    def test_release_date_uses_current_release_files(self):
        for file in (
            {
                "upload_time_iso_8601": "2026-10-24T12:00:00Z",
                "upload_time": "2026-10-23T12:00:00",
            },
            {"upload_time": "2026-10-24T12:00:00"},
        ):
            with self.subTest(file=file):
                self.assertEqual(
                    _parse_release({"info": {"version": "1.2.3"}, "urls": [file]}),
                    {"release": "1.2.3", "release_date": "24 Oct 2026"},
                )

    def test_unusable_optional_file_data_keeps_version_and_success_cache_lifetime(self):
        for optional_data in (
            {},
            {"urls": None},
            {"urls": []},
            {"urls": {"unexpected": "mapping"}},
            {"urls": [None]},
            {"urls": [{}]},
            {"urls": [{"upload_time_iso_8601": "invalid"}]},
            {"urls": [{"upload_time_iso_8601": 123}]},
        ):
            with self.subTest(optional_data=optional_data):
                response = Mock()
                response.json.return_value = {
                    "info": {"version": "1.2.3"},
                    **optional_data,
                }
                with (
                    patch(
                        "webapp.pages.templatetags.pypi_tags.requests.get",
                        return_value=response,
                    ),
                    patch("webapp.pages.templatetags.pypi_tags.cache") as cache,
                ):
                    cache.get.return_value = None
                    self.assertEqual(package_metadata("demo"), {"release": "1.2.3"})
                    cache.set.assert_called_once_with(
                        "pypi-metadata:demo", {"release": "1.2.3"}, 3600
                    )
