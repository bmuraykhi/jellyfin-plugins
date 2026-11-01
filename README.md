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

If you added `https://raw.githubusercontent.com/bmuraykhi/Sub-Jellyfin/main/manifest.json` for Season Subtitle
Downloader, it keeps working and keeps getting that plugin's updates, but it only lists that one plugin. To get
everything, replace it with the URL above under **Manage Repositories** (remove the old one, so Season Subtitle
Downloader isn't listed twice). Installed plugins stay installed.

## How the catalog is built

`manifest.json` is generated, so don't edit it by hand. The **Update catalog** workflow runs
`scripts/build_manifest.py` every hour, on demand (Actions → Update catalog → Run workflow) and whenever
`plugins.json` changes. For each plugin in `plugins.json` it lists every published GitHub release that has the
plugin's zip attached: the version number and target Jellyfin version come from the `meta.json` inside the zip, the
changelog from the release notes, and the checksum is the zip's MD5. Versions already in the catalog are kept as
they are, so a run only downloads new releases.

**Adding a plugin:** add an entry to `plugins.json` with its repository, the name of its release zip and its catalog
details (name, id, description, overview, owner, category, icon URL). Its releases need a zip containing the DLL and
`meta.json` (and the icon, if `meta.json` names one).

**After publishing a release** it shows up within the hour, or straight away if you run the workflow. GitHub pauses
scheduled workflows in repositories with no activity for 60 days; if that happens, run the workflow once by hand (or
re-enable it on the Actions tab) and the hourly runs resume.

## License

The Unlicense (public domain) — see [LICENSE](LICENSE). The plugins have their own licenses; see each repository.
