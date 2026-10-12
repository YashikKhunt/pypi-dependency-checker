#!/usr/bin/env python3
"""Check pinned dependencies against the PyPI JSON API.

Usage: python3 check_pypi.py [requirements.txt ...]
"""
import json
import sys
import urllib.error
import urllib.parse
import urllib.request

PYPI = "https://pypi.org/pypi"


def fetch_json(url):
    """Return parsed JSON, or None if PyPI answers 404."""
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def parse_line(line):
    """Return (name, version) from 'name==version'; version is None if unpinned."""
    line = line.split("#", 1)[0].split(";", 1)[0].strip()
    if not line:
        return None
    if "==" in line:
        name, version = (part.strip() for part in line.split("==", 1))
    else:
        name, version = line, None
        for op in ("~=", ">=", "<=", "!=", ">", "<"):
            name = name.split(op, 1)[0]
        name = name.strip()
    name = name.split("[", 1)[0].strip()  # drop extras like pkg[extra]
    return name, version


def main(paths):
    deps = []
    for path in paths:
        with open(path) as f:
            for line in f:
                parsed = parse_line(line)
                if parsed:
                    #print("parsed", parsed)
                    deps.append(parsed)

    missing_pkgs = []
    missing_versions = []
    oldest = None  # (upload_time, name, version)

    for name, version in deps:
        quoted = urllib.parse.quote(name)
        #print("quoted", quoted)
        if fetch_json(f"{PYPI}/{quoted}/json") is None:
            missing_pkgs.append(name)
            continue
        if version is None:
            continue
        release = fetch_json(f"{PYPI}/{quoted}/{urllib.parse.quote(version)}/json")
        if release is None:
            missing_versions.append(f"{name}=={version}")
            continue
        urls = release.get("urls") or []
        if not urls:
            continue  # release exists but has no files, so no upload_time
        uploaded = urls[0]["upload_time"]
        if oldest is None or uploaded < oldest[0]:
            oldest = (uploaded, name, version)

    print(f"Dependencies checked: {len(deps)}")
    print(f"Packages not on PyPI: {', '.join(missing_pkgs) or 'none'}")
    print(f"Versions not on PyPI: {', '.join(missing_versions) or 'none'}")
    if oldest:
        print(f"Oldest pinned release: {oldest[1]} == {oldest[2]} ({oldest[0][:4]})")
    else:
        print("Oldest pinned release: none")


if __name__ == "__main__":
    main(sys.argv[1:] or ["requirements.txt"])
