"""Tests for media catalog CLI helpers."""
import json

from better11.media_cli import handle_fetch_media


def test_handle_fetch_media_with_malformed_json(capsys):
    exit_code = handle_fetch_media("{invalid_json}")

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Failed to load media catalog" in captured.err
    assert "Traceback" not in captured.err


def test_handle_fetch_media_missing_required_fields(capsys):
    payload = json.dumps({"items": [{"id": "media-1"}]})

    exit_code = handle_fetch_media(payload)

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "required fields" in captured.err
    assert "Traceback" not in captured.err


def test_handle_fetch_media_success():
    payload = json.dumps({"items": [{"id": "media-1", "url": "https://example.com"}]})

    exit_code = handle_fetch_media(payload)

    assert exit_code == 0
