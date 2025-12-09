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


def test_missing_required_field_raises(catalog_writer, tmp_path: Path) -> None:
    entry = _catalog_entry(tmp_path, "missing")
    entry.pop("uri")
    catalog = catalog_writer([entry])

    with pytest.raises(ValueError) as err:
        AppCatalog.from_file(catalog)

    assert "missing required field 'uri'" in str(err.value)


def test_invalid_installer_type_raises(catalog_writer, tmp_path: Path) -> None:
    entry = _catalog_entry(tmp_path, "badtype")
    entry["installer_type"] = "pkg"
    catalog = catalog_writer([entry])

    with pytest.raises(ValueError) as err:
        AppCatalog.from_file(catalog)

    assert "Unsupported installer_type" in str(err.value)


def test_signature_and_key_must_be_paired(catalog_writer, tmp_path: Path) -> None:
    entry = _catalog_entry(tmp_path, "signed")
    entry["signature"] = "abc"
    catalog = catalog_writer([entry])

    with pytest.raises(ValueError) as err:
        AppCatalog.from_file(catalog)

    assert "must provide both 'signature' and 'signature_key'" in str(err.value)


def test_list_fields_require_strings(catalog_writer, tmp_path: Path) -> None:
    entry = _catalog_entry(tmp_path, "lists")
    entry["dependencies"] = ["dep1", 2]
    catalog = catalog_writer([entry])

    with pytest.raises(ValueError) as err:
        AppCatalog.from_file(catalog)

    assert "list of strings" in str(err.value)
