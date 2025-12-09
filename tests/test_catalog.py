from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from better11.apps.catalog import AppCatalog


def _catalog_entry(tmp_path: Path, app_id: str) -> dict[str, object]:
    payload = tmp_path / f"{app_id}.exe"
    payload.write_text(app_id)
    sha256 = hashlib.sha256(payload.read_bytes()).hexdigest()
    return {
        "app_id": app_id,
        "name": app_id,
        "version": "1.0",
        "uri": str(payload),
        "sha256": sha256,
        "installer_type": "exe",
    }


def test_duplicate_app_ids_raise(catalog_writer, tmp_path: Path) -> None:
    catalog = catalog_writer([
        _catalog_entry(tmp_path, "dup"),
        _catalog_entry(tmp_path, "dup"),
    ])

    with pytest.raises(ValueError):
        AppCatalog.from_file(catalog)
