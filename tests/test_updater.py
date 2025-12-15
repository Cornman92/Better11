"""Tests for Better11 update helpers."""

from __future__ import annotations

import hashlib
import io
import json
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from better11.apps.state_store import InstallationStateStore
from better11.apps.updater import (
    ApplicationUpdater,
    Better11Updater,
    UpdateInfo,
)
from better11.interfaces import Version


def _catalog_entry(app_id: str, version: str, uri: str, sha256: str) -> dict:
    return {
        "app_id": app_id,
        "name": app_id,
        "version": version,
        "uri": uri,
        "sha256": sha256,
        "installer_type": "exe",
        "dependencies": [],
        "vetted_domains": [],
    }


def test_application_updater_detects_catalog_update(catalog_writer, make_installer, tmp_path: Path):
    installer_v2 = make_installer("demo.exe", b"payload")
    sha = hashlib.sha256(installer_v2.read_bytes()).hexdigest()

    catalog_path = catalog_writer([
        _catalog_entry("demo", "1.0.0", str(installer_v2), sha),
    ])

    state_path = tmp_path / "installed.json"
    store = InstallationStateStore(state_path)
    store.mark_installed("demo", "0.9.0", installer_v2)

    updater = ApplicationUpdater(catalog_path=catalog_path, state_path=state_path)
    updates = updater.check_for_updates()

    assert len(updates) == 1
    assert updates[0].app_id == "demo"
    assert updates[0].current_version == "0.9.0"
    assert updates[0].new_version == "1.0.0"
    assert updates[0].download_url == str(installer_v2)


def test_application_updater_no_update_when_versions_equal(catalog_writer, make_installer, tmp_path: Path):
    installer = make_installer("demo.exe", b"payload")
    sha = hashlib.sha256(installer.read_bytes()).hexdigest()

    catalog_path = catalog_writer([
        _catalog_entry("demo", "1.0.0", str(installer), sha),
    ])

    state_path = tmp_path / "installed.json"
    store = InstallationStateStore(state_path)
    store.mark_installed("demo", "1.0.0", installer)

    updater = ApplicationUpdater(catalog_path=catalog_path, state_path=state_path)
    assert updater.check_for_updates() == []


def test_better11_updater_parses_github_release_json_for_update(monkeypatch):
    payload = {
        "tag_name": "v0.4.0",
        "body": "changelog",
        "published_at": "2025-12-01T00:00:00Z",
        "assets": [
            {
                "name": "better11.zip",
                "browser_download_url": "https://example.com/better11.zip",
                "size": 123,
            }
        ],
        "zipball_url": "https://example.com/source.zip",
    }

    class _Resp:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return json.dumps(payload).encode("utf-8")

    def fake_urlopen(request, timeout=0):
        return _Resp()

    monkeypatch.setattr("better11.apps.updater.urlopen", fake_urlopen)

    updater = Better11Updater(update_url="https://api.github.com/repos/x/y/releases/latest")
    monkeypatch.setattr(updater, "BETTER11_VERSION", "0.3.0")

    new_version = updater.check_for_updates()

    assert new_version == Version.parse("0.4.0")
    info = updater.get_update_info()
    assert info is not None
    assert info.download_url == "https://example.com/better11.zip"


def test_better11_updater_verify_download_hash(tmp_path: Path):
    file_path = tmp_path / "update.zip"
    file_path.write_bytes(b"hello")

    expected = hashlib.sha256(b"hello").hexdigest()

    updater = Better11Updater(update_url="https://example.com/manifest.json")
    updater._update_info = UpdateInfo(
        current_version=Version.parse("0.3.0"),
        new_version=Version.parse("0.4.0"),
        download_url="https://example.com/update.zip",
        changelog="",
        release_date=datetime.now(),
        size_bytes=5,
        hash_sha256=expected,
    )

    assert updater._verify_download(file_path) is True


def test_better11_updater_verify_download_hash_mismatch(tmp_path: Path):
    file_path = tmp_path / "update.zip"
    file_path.write_bytes(b"hello")

    updater = Better11Updater(update_url="https://example.com/manifest.json")
    updater._update_info = UpdateInfo(
        current_version=Version.parse("0.3.0"),
        new_version=Version.parse("0.4.0"),
        download_url="https://example.com/update.zip",
        changelog="",
        release_date=datetime.now(),
        size_bytes=5,
        hash_sha256="0" * 64,
    )

    assert updater._verify_download(file_path) is False


@patch("better11.apps.updater.AppManager")
def test_application_updater_install_update_uses_app_manager(mock_manager, catalog_writer, make_installer, tmp_path: Path):
    installer = make_installer("demo.exe", b"payload")
    sha = hashlib.sha256(installer.read_bytes()).hexdigest()

    catalog_path = catalog_writer([
        _catalog_entry("demo", "1.0.0", str(installer), sha),
    ])

    state_path = tmp_path / "installed.json"
    store = InstallationStateStore(state_path)
    store.mark_installed("demo", "0.9.0", installer)

    updater = ApplicationUpdater(catalog_path=catalog_path, state_path=state_path)
    updater.check_for_updates()

    mock_instance = mock_manager.return_value
    mock_status = MagicMock()
    mock_status.installed = True
    mock_instance.install.return_value = (mock_status, MagicMock())

    assert updater.install_update("demo") is True
    mock_instance.install.assert_called_once_with("demo")
