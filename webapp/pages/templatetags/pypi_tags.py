import re
from datetime import datetime
from urllib.parse import quote

import requests
from django import template
from django.core.cache import cache

register = template.Library()


def _normalize_package_name(package_name: str | None) -> str | None:
    if not package_name:
        return None
    # PyPI treats case and runs of -, _, or . as equivalent; share one cache key
    # and lookup URL for those names.
    return re.sub(r"[-_.]+", "-", package_name).lower()


def _parse_release(data: dict) -> dict[str, str]:
    """Keep a valid version available even when optional upload data is unusable."""
    version = data["info"]["version"]
    if not isinstance(version, str) or not version:
        raise ValueError("Missing package version")
    metadata = {"release": version}
    files = data.get("urls")
    if not isinstance(files, list) or not files or not isinstance(files[0], dict):
        return metadata
    uploaded = files[0].get("upload_time_iso_8601") or files[0].get("upload_time")
    if isinstance(uploaded, str):
        try:
            metadata["release_date"] = datetime.fromisoformat(uploaded).strftime(
                "%d %b %Y"
            )
        except ValueError:
            pass
    return metadata


def package_metadata(package_name: str | None) -> dict[str, str | None]:
    """Fetch the current release during rendering, caching equivalent names together.

    Empty names and unavailable data return {"release": None}. Bounded timeouts
    limit rendering delays; briefly caching failures avoids retrying on every request.
    """
    name = _normalize_package_name(package_name)
    if name is None:
        return {"release": None}
    name = quote(name, safe="")
    key = f"pypi-metadata:{name}"
    cached = cache.get(key)
    if cached is not None:
        return cached
    metadata = {"release": None}
    try:
        response = requests.get(f"https://pypi.org/pypi/{name}/json", timeout=(2, 3))
        response.raise_for_status()
        metadata = _parse_release(response.json())
    except (
        requests.RequestException,
        ValueError,
        KeyError,
        TypeError,
        IndexError,
        AttributeError,
    ):
        metadata = {"release": None}
    cache.set(key, metadata, 3600 if metadata["release"] else 300)
    return metadata


@register.inclusion_tag("pages/tags/pypi_info.html")
def pypi_info(
    package_name: str | None, repository_url: str = ""
) -> dict[str, str | None]:
    """Keep resource links available even when release metadata is unavailable."""
    metadata = package_metadata(package_name)
    return {
        **metadata,
        "pypi_url": (
            f"https://pypi.org/project/{quote(package_name, safe='')}/"
            if package_name
            else ""
        ),
        "repository_url": repository_url,
    }
