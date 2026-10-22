"""Fetch a complete, commit-pinned snapshot before changing staging records."""

import hashlib
import json
import re
from concurrent.futures import ThreadPoolExecutor

import requests
import yaml
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction
from django.utils import timezone

from .models import PortfolioProject, PortfolioSourceRecord

REPOSITORY = "wagtail/madewithwagtail"
DEVELOPER_PATH = "src/content/developers/nick-moreton"
API_ROOT = f"https://api.github.com/repos/{REPOSITORY}"
RAW_ROOT = f"https://raw.githubusercontent.com/{REPOSITORY}"
TIMEOUT = (3.05, 10)
TEXT_FIELDS = (
    "title",
    "category",
    "description",
    "image_description",
    "website_url",
    "record_url",
)


class SourceError(Exception):
    pass


def get_response(url):
    response = requests.get(
        url,
        timeout=TIMEOUT,
        headers={
            "User-Agent": "nickmoreton-portfolio-import",
            "Accept": "application/vnd.github+json",
        },
    )
    response.raise_for_status()
    return response


def parse_record(markdown, slug, commit_sha, tree_sha):
    parts = markdown.split("---", 2)
    if len(parts) != 3 or parts[0].strip():
        raise SourceError(f"Missing YAML front matter: {slug}.")
    metadata = yaml.safe_load(parts[1])
    if not isinstance(metadata, dict):
        raise SourceError(f"Invalid metadata: {slug}.")
    title = metadata.get("title")
    sectors = metadata.get("sector", [])
    if not isinstance(title, str) or not title.strip():
        raise SourceError(f"Missing title: {slug}.")
    if not isinstance(sectors, list) or any(not isinstance(s, str) for s in sectors):
        raise SourceError(f"Invalid sectors: {slug}.")
    source_path = f"{DEVELOPER_PATH}/{slug}/index.md"
    data = {
        "title": title.strip(),
        "category": " / ".join(s.capitalize() for s in sectors),
        "description": parts[2].strip(),
        "image_description": f"{title} website screenshot from Made with Wagtail",
        "website_url": metadata.get("site_url") or "",
        "record_url": f"https://madewithwagtail.org/developers/nick-moreton/{slug}/",
        "image_url": f"{RAW_ROOT}/{commit_sha}/{DEVELOPER_PATH}/{slug}/{slug}.fill-1200x996.webp",
    }
    # Validate exactly the values the editorial form will receive.
    for field in TEXT_FIELDS:
        PortfolioProject._meta.get_field(field).clean(data[field], None)
    return {
        "source_path": source_path,
        "title": data["title"],
        "raw_markdown": markdown,
        "metadata": json.loads(json.dumps(metadata, cls=DjangoJSONEncoder)),
        "data": data,
        "commit_sha": commit_sha,
        "fingerprint": hashlib.sha256((markdown + tree_sha).encode()).hexdigest(),
    }


def fetch_snapshot():
    try:
        commit_sha = get_response(f"{API_ROOT}/commits/main").json()["sha"]
        if not re.fullmatch(r"[a-f0-9]{40}", commit_sha):
            raise SourceError("GitHub returned an invalid commit identifier.")
        entries = get_response(
            f"{API_ROOT}/contents/{DEVELOPER_PATH}?ref={commit_sha}"
        ).json()
        if not isinstance(entries, list):
            raise SourceError("GitHub did not return a project listing.")
        directories = [entry for entry in entries if entry["type"] == "dir"]
        if len(directories) > 50:
            raise SourceError(
                "Unexpectedly large portfolio; review the source before importing."
            )

        def fetch_entry(entry):
            slug = entry["name"]
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
                raise SourceError("GitHub returned an invalid project directory.")
            markdown = get_response(
                f"{RAW_ROOT}/{commit_sha}/{DEVELOPER_PATH}/{slug}/index.md"
            ).text
            return parse_record(markdown, slug, commit_sha, entry["sha"])

        with ThreadPoolExecutor(max_workers=4) as executor:
            return list(executor.map(fetch_entry, directories))
    except (
        requests.RequestException,
        ValueError,
        KeyError,
        TypeError,
        yaml.YAMLError,
        ValidationError,
    ) as error:
        raise SourceError(
            "Could not fetch a valid portfolio snapshot. Existing data is unchanged."
        ) from error


def refresh_sources():
    snapshot = fetch_snapshot()
    now = timezone.now()
    with transaction.atomic():
        seen = []
        for values in snapshot:
            record, _ = PortfolioSourceRecord.objects.update_or_create(
                source_path=values["source_path"],
                defaults={**values, "fetched_at": now, "missing_upstream": False},
            )
            # Adopt a migrated project by its record URL without modifying it.
            if not record.project_id:
                matches = PortfolioProject.objects.filter(
                    record_url=record.data["record_url"]
                ).exclude(source_record__isnull=False)
                if matches.count() == 1:
                    record.project = matches.get()
                    record.save(update_fields=["project"])
            seen.append(record.pk)
        PortfolioSourceRecord.objects.exclude(pk__in=seen).update(missing_upstream=True)
    return len(snapshot)
