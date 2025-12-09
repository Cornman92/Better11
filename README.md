# Better11

An all around windows 11 system enhancer that includes live and offline image editing and application downloader/installer.

## Application manager

The application manager ships with a vetted catalog (`better11/apps/catalog.json`) and tools for downloading, validating, and running MSI/EXE/AppX installers with dependency-aware orchestration. Hash and HMAC-based signatures are checked before any install steps run, and installed application state is persisted under `~/.better11/`.

### Command line usage

```
python -m better11.cli list
python -m better11.cli install demo-appx
python -m better11.cli uninstall demo-exe
python -m better11.cli status
python -m better11.cli plan demo-appx
```

Use `--catalog` to point at a different catalog file if you maintain your own vetted app list.

`plan` previews the dependency order, highlights which entries are already installed, and warns if a dependency is missing or part of a cycle. This makes it easy to catch issues before invoking `install`.

### GUI usage

Start the Tkinter GUI with:

```
python -m better11.gui
```

Select an app from the list to download, install, or uninstall it. Operations are run asynchronously and report status in the footer.

The download cache automatically reuses installers that are already present in `~/.better11/downloads` after verifying their SHA-256 hash. Cached hits are surfaced in both the CLI and GUI so you know when a fresh download was (or was not) required.

### Catalog schema highlights

Each entry in `catalog.json` records vetted domains, SHA-256 hash, an HMAC-SHA256 signature, dependencies, and silent installation arguments. File-based URIs can be relative to the catalog file, while HTTPS entries must match a vetted domain before downloads are allowed.
