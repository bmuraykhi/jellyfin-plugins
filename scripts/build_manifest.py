#!/usr/bin/env python3
"""Builds manifest.json (the Jellyfin plugin catalog) from the GitHub releases of the plugins in plugins.json.

For every plugin it lists each published release that has the plugin's zip attached. A version's number and target
Jellyfin version come from the meta.json inside the zip, its changelog from the release notes, and its checksum is the
zip's MD5. Versions already in manifest.json are reused as they are (matched by download URL), so a run only downloads
new releases. If a plugin's releases can't be read, its current entry is kept unchanged.

Standard library only. Set GITHUB_TOKEN to raise the API rate limit (the workflow does).
"""
import hashlib
import io
import json
import os
import re
import sys
import urllib.error
import urllib.request
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGINS = os.path.join(ROOT, "plugins.json")
MANIFEST = os.path.join(ROOT, "manifest.json")
API = "https://api.github.com"
PLUGIN_FIELDS = ("name", "guid", "description", "overview", "owner", "category", "imageUrl")


def fetch(url, api=False):
    headers = {"User-Agent": "jellyfin-plugin-catalog"}
    if api:
        headers["Accept"] = "application/vnd.github+json"
        if os.environ.get("GITHUB_TOKEN"):
            headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]  # only ever sent to api.github.com
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60) as response:
        return response.read()


def releases(repo):
    out, page = [], 1
    while True:
        batch = json.loads(fetch(f"{API}/repos/{repo}/releases?per_page=100&page={page}", api=True))
        out.extend(batch)
        if len(batch) < 100:
            return out
        page += 1


def version_key(version):
    return tuple(int(p) for p in re.findall(r"\d+", version))


def version_from_tag(tag):
    parts = re.findall(r"\d+", tag)[:4]
    return ".".join(parts + ["0"] * (4 - len(parts)))


def clean_notes(body):
    """Release notes without GitHub's generated "What's Changed" / "Full Changelog" footer."""
    body = body or ""
    for marker in ("## What's Changed", "**Full Changelog**"):
        if marker in body:
            body = body[:body.index(marker)]
    return body.strip()


def new_version(release, asset, previous_abi):
    data = fetch(asset["browser_download_url"])
    meta = {}
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        if "meta.json" in archive.namelist():
            meta = json.loads(archive.read("meta.json").decode("utf-8-sig"))
    return {
        "version": meta.get("version") or version_from_tag(release["tag_name"]),
        "changelog": clean_notes(release.get("body")) or meta.get("changelog") or "",
        "targetAbi": meta.get("targetAbi") or previous_abi or "",
        "sourceUrl": asset["browser_download_url"],
        "checksum": hashlib.md5(data).hexdigest().upper(),
        "timestamp": release.get("published_at") or release.get("created_at"),
    }


def build_entry(plugin, current):
    cached = {v["sourceUrl"]: v for v in (current or {}).get("versions", [])}
    try:
        found = releases(plugin["repo"])
    except (urllib.error.URLError, OSError, ValueError) as err:
        print(f"{plugin['name']}: could not read releases of {plugin['repo']} ({err}); keeping the current entry",
              file=sys.stderr)
        return current
    versions = []
    for release in sorted(found, key=lambda r: r.get("published_at") or "", reverse=False):
        if release.get("draft") or release.get("prerelease"):
            continue
        asset = next((a for a in release.get("assets", []) if a["name"] == plugin["asset"]), None)
        if not asset:
            continue
        url = asset["browser_download_url"]
        if url in cached:
            versions.append(cached[url])
        else:
            previous_abi = versions[-1]["targetAbi"] if versions else ""
            versions.append(new_version(release, asset, previous_abi))
            print(f"{plugin['name']}: added {versions[-1]['version']} from {release['tag_name']}")
    if not versions:
        print(f"{plugin['name']}: no releases with {plugin['asset']} yet", file=sys.stderr)
        return current
    entry = {k: plugin[k] for k in PLUGIN_FIELDS if k in plugin}
    entry["versions"] = sorted(versions, key=lambda v: version_key(v["version"]), reverse=True)
    return entry


def main():
    plugins = json.load(open(PLUGINS, encoding="utf-8"))
    current = {}
    if os.path.exists(MANIFEST):
        current = {p["guid"]: p for p in json.load(open(MANIFEST, encoding="utf-8"))}
    manifest = [e for e in (build_entry(p, current.get(p["guid"])) for p in plugins) if e]
    text = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    if os.path.exists(MANIFEST) and open(MANIFEST, encoding="utf-8").read() == text:
        print("manifest.json is up to date")
        return
    with open(MANIFEST, "w", encoding="utf-8") as f:
        f.write(text)
    print("manifest.json updated: " + ", ".join(f"{e['name']} {e['versions'][0]['version']}" for e in manifest))


if __name__ == "__main__":
    main()
