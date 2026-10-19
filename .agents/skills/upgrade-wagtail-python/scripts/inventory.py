#!/usr/bin/env python3
"""Print a read-only, stable backend upgrade inventory for this checkout."""

import hashlib
import json
import re
import sys
import tomllib
from pathlib import Path

COMPANION_FILES = (
    "pyproject.toml",
    "uv.lock",
    ".python-version",
    "docker/Dockerfile",
    ".github/workflows/test.yml",
    ".pre-commit-config.yaml",
    "AGENTS.md",
    "README.md",
    "CHANGELOG.md",
    "docs/python-upgrade.md",
    "docs/local.production.md",
    "docs/data-and-media.md",
    "docker-compose.yaml",
    "docker-compose.production.yaml",
    "gunicorn.conf.py",
    "Procfile",
    "app.json",
    "webapp/settings/base.py",
    "webapp/settings/dev.py",
    "webapp/settings/production.py",
    "webapp/urls.py",
    "webapp/home/models.py",
    "webapp/pages/models.py",
    "webapp/pages/blocks.py",
    "webapp/core/models.py",
)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def dependency_names(requirements):
    names = []
    for requirement in requirements:
        if isinstance(requirement, str):
            match = re.match(r"[A-Za-z0-9][A-Za-z0-9_.-]*", requirement)
            if not match:
                raise ValueError("Cannot identify a declared dependency name")
            names.append(re.sub(r"[-_.]+", "-", match.group()).lower())
        elif isinstance(requirement, dict) and "include-group" in requirement:
            names.append({"include-group": requirement["include-group"]})
        else:
            raise ValueError(
                "Unsupported dependency group entry; inspect pyproject.toml"
            )
    return sorted(names, key=lambda entry: json.dumps(entry, sort_keys=True))


def inventory(root):
    project = tomllib.loads((root / "pyproject.toml").read_text())
    if project["project"]["name"] != "nickmoreton":
        raise ValueError("This skill is specific to the nickmoreton.co.uk checkout")
    lock_bytes = (root / "uv.lock").read_bytes()
    lock = tomllib.loads(lock_bytes.decode())
    packages = []
    for package in lock["package"]:
        source = package.get("source", {})
        artifacts = [package["sdist"]] if "sdist" in package else []
        artifacts += package.get("wheels", [])
        packages.append(
            {
                "name": package["name"],
                "version": package["version"],
                "resolution_markers": package.get("resolution-markers", []),
                "source_kinds": sorted(source),
                # Fingerprint the source without printing private index URLs.
                "source_sha256": sha256(json.dumps(source, sort_keys=True).encode()),
                "artifact_hashes": sorted(
                    {artifact["hash"] for artifact in artifacts if "hash" in artifact}
                ),
            }
        )
    paths = set(COMPANION_FILES)
    for pattern in (
        ".github/workflows/*.yml",
        ".github/workflows/*.yaml",
        "webapp/**/test*.py",
        "webapp/**/migrations/*.py",
        "webapp/**/templatetags/*.py",
        "webapp/**/templates/**/*.html",
    ):
        paths.update(path.relative_to(root).as_posix() for path in root.glob(pattern))
    return {
        "schema_version": 1,
        "project": project["project"]["name"],
        "requires_python": project["project"].get("requires-python"),
        "python_version_file": (root / ".python-version").read_text().strip(),
        "direct_dependencies": dependency_names(project["project"]["dependencies"]),
        "dependency_groups": {
            name: dependency_names(entries)
            for name, entries in project.get("dependency-groups", {}).items()
        },
        "lock": {
            "sha256": sha256(lock_bytes),
            "version": lock.get("version"),
            "revision": lock.get("revision"),
            "requires_python": lock.get("requires-python"),
            "resolution_markers": lock.get("resolution-markers", []),
            "packages": sorted(
                packages, key=lambda item: json.dumps(item, sort_keys=True)
            ),
        },
        "companion_files": {
            name: sha256((root / name).read_bytes())
            if (root / name).is_file()
            else None
            for name in sorted(paths)
        },
    }


if __name__ == "__main__":
    try:
        # .agents/skills/upgrade-wagtail-python/scripts/inventory.py
        checkout = Path(__file__).resolve().parents[4]
        print(json.dumps(inventory(checkout), indent=2, sort_keys=True))
    except (OSError, ValueError, KeyError) as error:
        print(f"Inventory failed: {error}", file=sys.stderr)
        sys.exit(1)
