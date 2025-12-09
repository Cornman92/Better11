from __future__ import annotations

import shutil
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Optional

from .models import AppMetadata


class DownloadError(RuntimeError):
    pass


class AppDownloader:
    """Downloads vetted installers from HTTP(S) or local file URIs."""

    def __init__(self, download_root: Path, source_root: Optional[Path] = None):
        self.download_root = download_root
        self.download_root.mkdir(parents=True, exist_ok=True)
        self.source_root = source_root or Path.cwd()

    def _destination_for(self, app: AppMetadata) -> Path:
        parsed = urllib.parse.urlparse(app.uri)
        filename = Path(parsed.path).name
        if not filename:
            raise DownloadError(f"Unable to determine filename from {app.uri}")
        return self.download_root / filename

    def download(self, app: AppMetadata, destination: Optional[Path] = None) -> Path:
        parsed = urllib.parse.urlparse(app.uri)
        destination = destination or self._destination_for(app)

        if parsed.scheme in {"http", "https"}:
            hostname = parsed.hostname or ""
            if not app.domain_is_vetted(hostname):
                raise DownloadError(f"Host '{hostname}' is not in vetted domains for {app.app_id}")
            with urllib.request.urlopen(app.uri, timeout=30) as response, destination.open("wb") as handle:
                shutil.copyfileobj(response, handle)
            return destination

        if parsed.scheme in {"file", ""}:  # allow local files for testing or offline sources
            source = Path(parsed.path)
            if not source.is_absolute():
                source = (self.source_root / source).resolve()
            if not source.exists():
                raise DownloadError(f"Local source does not exist: {source}")
            with source.open("rb") as source_handle, destination.open("wb") as dest_handle:
                shutil.copyfileobj(source_handle, dest_handle)
            return destination

        raise DownloadError(f"Unsupported URI scheme for {app.uri}")
