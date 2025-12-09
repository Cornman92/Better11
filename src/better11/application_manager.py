"""Application manager utilities for downloading and validating media files."""

from __future__ import annotations

import hashlib
import shutil
import urllib.request
from pathlib import Path


class ApplicationManager:
    """Handle downloading media assets with optional checksum validation."""

    def download_media(self, url: str, destination: Path | str, checksum: str | None = None) -> Path:
        """
        Download a media file to *destination* and optionally verify its checksum.

        A temporary file is created and cleaned up if the download or checksum
        verification fails. When the download succeeds, the temporary file is
        atomically moved to *destination*.
        """

        destination_path = Path(destination)
        temp_destination = destination_path.with_suffix(destination_path.suffix + ".tmp")
        destination_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            self._download_file(url, temp_destination)
            if checksum is not None:
                self._verify_checksum(temp_destination, checksum)
            temp_destination.replace(destination_path)
            return destination_path
        except Exception:
            temp_destination.unlink(missing_ok=True)
            raise

    def _download_file(self, url: str, destination: Path) -> None:
        """Download *url* to *destination* streaming the response to disk."""

        with urllib.request.urlopen(url) as response, destination.open("wb") as file_handle:
            shutil.copyfileobj(response, file_handle)

    def _verify_checksum(self, file_path: Path, expected_checksum: str) -> None:
        """Validate the SHA256 checksum of *file_path* against *expected_checksum*."""

        digest = hashlib.sha256()
        with file_path.open("rb") as file_handle:
            for chunk in iter(lambda: file_handle.read(8192), b""):
                digest.update(chunk)

        actual_checksum = digest.hexdigest()
        if actual_checksum.lower() != expected_checksum.lower():
            raise ValueError(
                f"Checksum mismatch for {file_path}: expected {expected_checksum}, got {actual_checksum}"
            )
