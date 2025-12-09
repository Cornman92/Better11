import pytest

from better11.application_manager import ApplicationManager


def test_temp_file_removed_on_download_error(tmp_path):
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


def test_temp_file_removed_on_checksum_mismatch(tmp_path):
    class ChecksumMismatchManager(ApplicationManager):
        def _download_file(self, url, destination):
            destination.write_text("content")

    manager = ChecksumMismatchManager()
    destination = tmp_path / "media.bin"
    temp_destination = destination.with_suffix(destination.suffix + ".tmp")

    with pytest.raises(ValueError):
        manager.download_media("http://example.com/media.bin", destination, checksum="deadbeef")

    assert not temp_destination.exists()
    assert not destination.exists()
