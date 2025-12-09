from __future__ import annotations

from pathlib import Path

import pytest

from better11.apps.download import AppDownloader, DownloadError
from better11.apps.models import AppMetadata, InstallerType


def _metadata(uri: str, vetted_domains: list[str] | None = None) -> AppMetadata:
    return AppMetadata(
        app_id="demo",
        name="Demo",
        version="1.0.0",
        uri=uri,
        sha256="deadbeef",
        installer_type=InstallerType.EXE,
        vetted_domains=vetted_domains or [],
    )


def test_downloads_relative_file_sources(tmp_path: Path) -> None:
    source_root = tmp_path / "source"
    download_root = tmp_path / "downloads"
    source_root.mkdir()
    payload = source_root / "demo.exe"
    payload.write_bytes(b"payload")

    downloader = AppDownloader(download_root=download_root, source_root=source_root)
    metadata = _metadata("demo.exe")

    destination = downloader.download(metadata)

    assert destination.exists()
    assert destination.read_bytes() == payload.read_bytes()


def test_rejects_unvetted_http_domain(tmp_path: Path) -> None:
    downloader = AppDownloader(download_root=tmp_path / "downloads")
    metadata = _metadata("https://example.com/demo.exe")

    with pytest.raises(DownloadError) as exc:
        downloader.download(metadata)

    assert "not in vetted domains" in str(exc.value)


def test_missing_local_source_raises(tmp_path: Path) -> None:
    downloader = AppDownloader(download_root=tmp_path / "downloads", source_root=tmp_path / "source")
    metadata = _metadata("non-existent.exe")

    with pytest.raises(DownloadError) as exc:
        downloader.download(metadata)

    assert "Local source does not exist" in str(exc.value)
