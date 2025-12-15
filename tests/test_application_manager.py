import hashlib
from pathlib import Path

import pytest

from better11.application_manager import ApplicationManager
from better11.media_catalog import InstallType, MediaCatalog, MediaEntry


def test_temp_file_removed_on_download_error(tmp_path: Path):
    class FailingDownloadManager(ApplicationManager):
        def _download_file(self, url, destination):
            destination.write_text("partial")
            raise RuntimeError("download failed")

    manager = FailingDownloadManager()
    destination = tmp_path / "media.bin"
    temp_destination = destination.with_suffix(destination.suffix + ".tmp")

    with pytest.raises(RuntimeError):
        manager.download_media("http://example.com/media.bin", destination)

    assert not temp_destination.exists()
    assert not destination.exists()


def test_temp_file_removed_on_checksum_mismatch(tmp_path: Path):
    class ChecksumMismatchManager(ApplicationManager):
        def _download_file(self, url, destination):
            destination.write_text("content")

    manager = ChecksumMismatchManager()
    destination = tmp_path / "media.bin"
    temp_destination = destination.with_suffix(destination.suffix + ".tmp")

    with pytest.raises(ValueError):
        manager.download_media(
            "http://example.com/media.bin", destination, checksum="deadbeef", validate_checksum=True
        )

    assert not temp_destination.exists()
    assert not destination.exists()


def test_checksum_validation_can_be_disabled(tmp_path: Path):
    class SkipChecksumManager(ApplicationManager):
        def _download_file(self, url, destination):
            destination.write_text("content")

    manager = SkipChecksumManager()
    destination = tmp_path / "media.bin"

    path = manager.download_media(
        "http://example.com/media.bin",
        destination,
        checksum="deadbeef",
        validate_checksum=False,
    )

    assert path.exists()
    assert path.read_text() == "content"


def test_fetch_catalog_entry_downloads_to_repository(tmp_path: Path):
    payload = tmp_path / "payload.bin"
    payload.write_text("payload")
    checksum = hashlib.sha256(payload.read_bytes()).hexdigest()

    entry = MediaEntry(
        identifier="demo",
        source=payload.as_uri(),
        target_path=Path("apps/demo.bin"),
        install_type=InstallType.APPLICATION,
        checksum=checksum,
    )
    manager = ApplicationManager()

    destination = manager.fetch_catalog_entry(entry, tmp_path)

    assert destination == tmp_path / "apps" / "demo.bin"
    assert destination.read_text() == "payload"


def test_export_and_import_catalog(tmp_path: Path):
    catalog = MediaCatalog(
        applications=[
            MediaEntry(
                identifier="demo",
                source="https://example.com/demo.bin",
                target_path=Path("apps/demo.bin"),
                install_type=InstallType.APPLICATION,
            )
        ]
    )
    destination = tmp_path / "catalogs" / "app-catalog.json"

    manager = ApplicationManager()
    manager.export_catalog(catalog, destination)

    loaded = manager.import_catalog(destination)

    assert len(list(loaded.all_entries())) == 1
    loaded_entry = next(iter(loaded.all_entries()))
    assert loaded_entry.identifier == "demo"
    assert loaded_entry.target_path == Path("apps/demo.bin")
