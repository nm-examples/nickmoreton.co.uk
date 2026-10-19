import re
from datetime import datetime

import requests
from django import template
from django.core.cache import cache

register = template.Library()


def package_metadata(package_name):
    if not package_name or not re.fullmatch(
        r"[A-Za-z0-9][A-Za-z0-9._-]{0,254}", package_name
    ):
        return {"release": None}
    name = re.sub(r"[-_.]+", "-", package_name).lower()
    key = f"pypi-metadata:{name}"
    cached = cache.get(key)
    if cached is not None:
        return cached
    metadata = {"release": None}
    try:
        response = requests.get(f"https://pypi.org/pypi/{name}/json", timeout=(2, 3))
        response.raise_for_status()
        data = response.json()
        version = data["info"]["version"]
        if not isinstance(version, str) or not version:
            raise ValueError("Missing package version")
        metadata = {"release": version}
        releases = data.get("releases", {}).get(version, [])
        if releases:
            uploaded = releases[0].get("upload_time_iso_8601") or releases[0].get(
                "upload_time"
            )
            if uploaded:
                metadata["release_date"] = datetime.fromisoformat(uploaded).strftime(
                    "%d %b %Y"
                )
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
def pypi_info(package_name, repository_url=""):
    metadata = package_metadata(package_name)
    valid_name = package_name and re.fullmatch(
        r"[A-Za-z0-9][A-Za-z0-9._-]{0,254}", package_name
    )
    return {
        **metadata,
        "pypi_url": f"https://pypi.org/project/{package_name}/" if valid_name else "",
        "repository_url": repository_url,
    }
