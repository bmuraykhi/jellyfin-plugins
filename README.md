<div align="center">

# Bandar's Jellyfin plugins

One catalog for all my Jellyfin plugins. Add it once, then install and update every plugin from Jellyfin's own
plugin catalog.

</div>

## Add the catalog

1. Dashboard → **Plugins** → **Manage Repositories** → **+**
2. Name: `Bandar's plugins` (any name works)
3. URL:

   ```
   https://raw.githubusercontent.com/bmuraykhi/jellyfin-plugins/main/manifest.json
   ```

4. Save, then Dashboard → **Plugins** → **Catalog**, pick a plugin (under *General*) and **Install**.
5. Restart Jellyfin, then reload the web page (or fully close and reopen the app).

The plugins below add to Jellyfin's web interface through the
**[File Transformation](https://github.com/IAmParadox27/jellyfin-plugin-file-transformation)** plugin. Install it
from its own catalog first: add `https://www.iamparadox.dev/jellyfin/plugins/manifest.json` the same way, install
**File Transformation** and restart.

## Plugins

| | Plugin | What it does | Jellyfin |
| :---: | --- | --- | --- |
| <img src="https://raw.githubusercontent.com/bmuraykhi/Sub-Jellyfin/main/assets/icon.png" width="48" alt=""> | **[Season Subtitle Downloader](https://github.com/bmuraykhi/Sub-Jellyfin)** | One button downloads subtitles for every episode of a season or a whole series, in as many languages as you need. | 10.11 and newer |
| <img src="https://raw.githubusercontent.com/bmuraykhi/jellyfin-plugin-untrack/main/assets/icon.png" width="48" alt=""> | **[Untrack Show](https://github.com/bmuraykhi/jellyfin-plugin-untrack)** | Clears a whole show out of Continue Watching and Next Up from its ⋮ menu. | 12.4 |

Each plugin's page has screenshots, settings and troubleshooting.

## Coming from the Sub-Jellyfin catalog?

`https://raw.githubusercontent.com/bmuraykhi/Sub-Jellyfin/main/manifest.json` is retired: it stops at Season Subtitle
Downloader 3.0.0.0 and gets no more updates. Replace it with the URL above under **Manage Repositories** (remove the
old one, so Season Subtitle Downloader isn't listed twice). Installed plugins stay installed.

## How the catalog is built

`manifest.json` is generated, so don't edit it by hand. The **Update catalog** workflow runs
`scripts/build_manifest.py` when a plugin publishes a release, when `plugins.json` or the script changes, once a day,
and on demand (Actions → Update catalog → Run workflow). It rebuilds the whole catalog from the GitHub releases of
the plugins in `plugins.json`, using every published release that has the plugin's zip attached:

- version, target Jellyfin version, name, description and the other details come from the `meta.json` inside the zip
  (the details from the newest version);
- the changelog is the version's `## [x.y.z.w]` section of the plugin's `CHANGELOG.md`, or else the release notes;
- the checksum is the zip's MD5.

When the result differs from `manifest.json`, the workflow commits it as the catalog's GitHub App.

## Releasing a plugin

Every plugin releases through the shared `.github/workflows/release-plugin.yml`, called from its own `release.yml`
after its CI passes:

1. Set `version` in `meta.json` and move the `## [Unreleased]` entries in `CHANGELOG.md` under
   `## [x.y.z.w] – date`. Commit and push to `main`.
2. `git tag vx.y.z.w && git push origin vx.y.z.w`

The workflow checks that the tag matches `meta.json`, is on `main` and has a CHANGELOG section, and that `targetAbi`
matches the Jellyfin package version. It then builds the zip (DLL, `meta.json` with the release date and changelog,
icon), publishes the release with that CHANGELOG section as its notes, and tells this catalog to rebuild. Nothing is
committed back to the plugin's repository. Running the plugin's Release workflow by hand builds the zip as a workflow
artifact without publishing anything.

## Adding a plugin

1. Give it a `meta.json` (name, guid, description, overview, owner, category, version, targetAbi, imagePath), a
   `CHANGELOG.md`, and a `release.yml` that calls the shared workflow (copy one from an existing plugin).
2. In its repository settings, add the `CATALOG_APP_CLIENT_ID` variable and the `CATALOG_APP_PRIVATE_KEY` secret of
   the catalog's GitHub App (this repository has the same two). The app only needs to be installed on this
   repository, with read and write access to its contents.
3. Add the repository, the release zip's file name and the icon URL to `plugins.json`.

## License

The Unlicense (public domain) — see [LICENSE](LICENSE). The plugins have their own licenses; see each repository.
