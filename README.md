# Bandar's Jellyfin plugins

One catalog for all my Jellyfin plugins.

## Add the catalog

1. Dashboard → **Plugins** → **Manage Repositories** → **+**, and add
   `https://raw.githubusercontent.com/bmuraykhi/jellyfin-plugins/main/manifest.json`
2. **Catalog** → pick a plugin → **Install**, then restart Jellyfin.

The plugins need the [File Transformation](https://github.com/IAmParadox27/jellyfin-plugin-file-transformation)
plugin. Add `https://www.iamparadox.dev/jellyfin/plugins/manifest.json` the same way and install it first.

If you added the old `https://raw.githubusercontent.com/bmuraykhi/Sub-Jellyfin/main/manifest.json` catalog, replace it
with this one. The old one is retired.

## Plugins

| Plugin | What it does | Jellyfin |
| --- | --- | --- |
| [Season Subtitle Downloader](https://github.com/bmuraykhi/Sub-Jellyfin) | Downloads subtitles for a whole season or series in one click | 10.11+ |
| [Untrack Show](https://github.com/bmuraykhi/jellyfin-plugin-untrack) | Removes a show from Continue Watching and Next Up | 12.4 |

## Maintaining

`manifest.json` is generated, so don't edit it. The **Update catalog** workflow rebuilds it from each plugin's
GitHub releases when a plugin releases, once a day and on demand, and commits it as the catalog's GitHub App. Each
version's details come from the `meta.json` in its zip, its changelog from the plugin's `CHANGELOG.md`, and its
checksum is the zip's MD5.

**Releasing a plugin:** set `version` in `meta.json`, move the Unreleased notes in `CHANGELOG.md` under
`## [x.y.z.w] – date`, push, then push the tag `vx.y.z.w`. The plugin's `release.yml` runs its CI and then
`release-plugin.yml` from this repository, which checks the tag, builds the zip, publishes the release and updates
the catalog.

**Adding a plugin:** give it a `meta.json`, a `CHANGELOG.md` and a `release.yml` like the others. Then add the
`CATALOG_APP_CLIENT_ID` variable and `CATALOG_APP_PRIVATE_KEY` secret to its repository, and list it in
`plugins.json`.

## License

[The Unlicense](LICENSE). Each plugin has its own license.
