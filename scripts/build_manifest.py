#!/usr/bin/env python3
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
META_FIELDS = ("name", "guid", "description", "overview", "owner", "category")
GENERATED_NOTES = ("## What's Changed", "**Full Changelog**")


def log(message):
    print(message, file=sys.stderr)


def fetch(url, accept=None):
    headers = {"User-Agent": "jellyfin-plugin-catalog"}
    if url.startswith(API + "/"):
        headers["Accept"] = accept or "application/vnd.github+json"
        if os.environ.get("GITHUB_TOKEN"):
            headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60) as response:
        return response.read()


def releases(repo):
    found, page = [], 1
    while True:
        batch = json.loads(fetch(f"{API}/repos/{repo}/releases?per_page=100&page={page}"))
        found.extend(batch)
        if len(batch) < 100:
            return found
        page += 1


def version_key(version):
    parts = [int(p) for p in re.findall(r"\d+", version)]
    return tuple(parts + [0] * (4 - len(parts)))


def changelog_sections(repo):
    try:
        text = fetch(f"{API}/repos/{repo}/contents/CHANGELOG.md", accept="application/vnd.github.raw").decode("utf-8")
    except urllib.error.HTTPError as err:
        if err.code == 404:
            return {}
        raise
    sections, current = {}, None
    for line in text.splitlines():
        heading = re.match(r"## \[(\d+(?:\.\d+)*)\]", line)
        if heading:
            current = version_key(heading.group(1))
            sections[current] = []
        elif line.startswith("## "):
            current = None
        elif current is not None:
            sections[current].append(line)
    return {key: "\n".join(lines).strip() for key, lines in sections.items()}


def release_notes(release):
    body = release.get("body") or ""
    for marker in GENERATED_NOTES:
        if marker in body:
            body = body[:body.index(marker)]
    return body.strip()


def read_version(release, asset, changelogs):
    data = fetch(asset["browser_download_url"])
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        meta = json.loads(archive.read("meta.json").decode("utf-8-sig"))
    version = meta["version"]
    return meta, {
        "version": version,
        "changelog": changelogs.get(version_key(version)) or release_notes(release) or meta.get("changelog") or "",
        "targetAbi": meta.get("targetAbi", ""),
        "sourceUrl": asset["browser_download_url"],
        "checksum": hashlib.md5(data).hexdigest().upper(),
        "timestamp": release["published_at"],
    }


def build_entry(plugin, current):
    try:
        found = releases(plugin["repo"])
    except (urllib.error.URLError, OSError, ValueError) as err:
        log(f"{plugin['repo']}: can't read releases ({err}), keeping its current entry")
        return current
    changelogs = changelog_sections(plugin["repo"])
    versions = []
    for release in found:
        if release.get("draft") or release.get("prerelease"):
            continue
        asset = next((a for a in release.get("assets", []) if a["name"] == plugin["asset"]), None)
        if asset:
            versions.append(read_version(release, asset, changelogs))
    if not versions:
        log(f"{plugin['repo']}: no releases with {plugin['asset']} yet")
        return current
    versions.sort(key=lambda v: version_key(v[1]["version"]), reverse=True)
    newest = versions[0][0]
    entry = {field: newest[field] for field in META_FIELDS if field in newest}
    entry["imageUrl"] = plugin["imageUrl"]
    entry["versions"] = [version for _, version in versions]
    return entry


def current_entry(manifest, repo):
    prefix = f"https://github.com/{repo}/releases/download/"
    return next((p for p in manifest if any(v["sourceUrl"].startswith(prefix) for v in p.get("versions", []))), None)


def commit_subject(old, new):
    before = {(p["guid"], v["version"]) for p in old for v in p.get("versions", [])}
    added = [f"{p['name'].lower()} {v['version']}" for p in new for v in p["versions"]
             if (p["guid"], v["version"]) not in before]
    if added:
        return "chore(catalog): add " + ", ".join(added)
    return "chore(catalog): update manifest.json"


def main():
    with open(PLUGINS, encoding="utf-8") as f:
        plugins = json.load(f)
    old_text, old = "", []
    if os.path.exists(MANIFEST):
        with open(MANIFEST, encoding="utf-8") as f:
            old_text = f.read()
        old = json.loads(old_text)
    manifest = [e for e in (build_entry(p, current_entry(old, p["repo"])) for p in plugins) if e]
    text = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    if text == old_text:
        log("manifest.json is up to date")
        return
    with open(MANIFEST, "w", encoding="utf-8") as f:
        f.write(text)
    subject = commit_subject(old, manifest)
    log(subject)
    print(subject)


if __name__ == "__main__":
    main()
