"""Tests for media catalog CLI helpers."""
from __future__ import annotations

import json
import hashlib
from pathlib import Path

from better11.media_cli import fetch_media, handle_fetch_media


def test_handle_fetch_media_with_malformed_json(capsys):
    exit_code = handle_fetch_media("{invalid_json}")

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Failed to load media catalog" in captured.err
    assert "Traceback" not in captured.err


def test_handle_fetch_media_missing_required_fields(capsys):
    payload = json.dumps({"drivers": [{"id": "media-1"}]})

    exit_code = handle_fetch_media(payload)

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "missing required fields" in captured.err
    assert "Traceback" not in captured.err


def test_handle_fetch_media_success():
    payload = json.dumps(
        {
            "drivers": [
                {
                    "id": "media-1",
                    "source": "https://example.com/driver.bin",
                    "target": "drivers/driver.bin",
                    "install_type": "driver",
                }
            ]
        }
    )

    exit_code = handle_fetch_media(payload)

    assert exit_code == 0


def test_fetch_media_downloads_payload(tmp_path: Path):
    source_file = tmp_path / "installer.bin"
    source_file.write_text("payload")
    checksum = hashlib.sha256(source_file.read_bytes()).hexdigest()

    catalog_payload = {
        "applications": [
            {
                "id": "app-1",
                "source": source_file.as_uri(),
                "target": "apps/app-1.bin",
                "checksum": checksum,
                "install_type": "application",
            }
        ]
    }
    catalog_path = tmp_path / "catalog.json"
    catalog_path.write_text(json.dumps(catalog_payload))

    exit_code = fetch_media(catalog_path, tmp_path / "repository")

    assert exit_code == 0
    assert (tmp_path / "repository" / "apps" / "app-1.bin").read_text() == "payload"


def test_fetch_media_handles_checksum_failure(tmp_path: Path, capsys):
    source_file = tmp_path / "installer.bin"
    source_file.write_text("payload")

    catalog_payload = {
        "applications": [
            {
                "id": "app-1",
                "source": source_file.as_uri(),
                "target": "apps/app-1.bin",
                "checksum": "deadbeef",
                "install_type": "application",
            }
        ]
    }
    catalog_path = tmp_path / "catalog.json"
    catalog_path.write_text(json.dumps(catalog_payload))

    exit_code = fetch_media(catalog_path, tmp_path / "repository")

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Checksum verification failed" in captured.err
    assert "app-1" in captured.err
