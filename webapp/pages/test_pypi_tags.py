from unittest.mock import Mock, patch

import requests
from django.core.cache import cache
from django.test import SimpleTestCase

from webapp.pages.templatetags.pypi_tags import package_metadata, pypi_info


class PackageMetadataTests(SimpleTestCase):
    def setUp(self):
        cache.clear()

    @patch("webapp.pages.templatetags.pypi_tags.requests.get")
    def test_metadata_is_cached_and_names_are_normalized(self, get):
        get.return_value = Mock(
            json=Mock(
                return_value={
                    "info": {"version": "1.2"},
                    "releases": {"1.2": [{"upload_time": "2026-01-01T10:00:00"}]},
                }
            )
        )
        result = package_metadata("Example_Package")
        self.assertEqual(result, {"release": "1.2", "release_date": "01 Jan 2026"})
        self.assertEqual(package_metadata("example-package"), result)
        get.assert_called_once_with(
            "https://pypi.org/pypi/example-package/json", timeout=(2, 3)
        )

    @patch(
        "webapp.pages.templatetags.pypi_tags.requests.get", side_effect=requests.Timeout
    )
    def test_timeout_is_graceful_and_failure_is_cached(self, get):
        self.assertEqual(package_metadata("example"), {"release": None})
        self.assertEqual(package_metadata("example"), {"release": None})
        self.assertEqual(get.call_count, 1)

    @patch("webapp.pages.templatetags.pypi_tags.requests.get")
    def test_blank_and_invalid_names_do_not_make_requests(self, get):
        for name in ["", None, "../invalid", "https://example.com"]:
            self.assertEqual(package_metadata(name), {"release": None})
        get.assert_not_called()

    @patch("webapp.pages.templatetags.pypi_tags.requests.get")
    def test_missing_releases_do_not_hide_version(self, get):
        get.return_value = Mock(json=Mock(return_value={"info": {"version": "1.0"}}))
        self.assertEqual(package_metadata("example"), {"release": "1.0"})

    @patch("webapp.pages.templatetags.pypi_tags.requests.get")
    def test_malformed_json_and_http_errors_are_graceful(self, get):
        for response in [
            Mock(json=Mock(side_effect=ValueError)),
            Mock(json=Mock(return_value={"info": None})),
            Mock(raise_for_status=Mock(side_effect=requests.HTTPError)),
        ]:
            cache.clear()
            get.return_value = response
            self.assertEqual(package_metadata("example"), {"release": None})

    @patch(
        "webapp.pages.templatetags.pypi_tags.package_metadata",
        return_value={"release": None},
    )
    def test_invalid_name_does_not_produce_a_pypi_link(self, metadata):
        self.assertEqual(pypi_info("../invalid")["pypi_url"], "")
