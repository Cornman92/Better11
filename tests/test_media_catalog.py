import json
from pathlib import Path

import pytest

from better11.media_catalog import InstallType, MediaCatalog


def test_media_catalog_loads_sections():
    payload = json.dumps(
        {
            "drivers": [
                {"id": "gpu", "source": "https://example.com/gpu.exe", "target": "drivers/gpu.exe"}
            ],
            "updates": [
                {"id": "kb123", "source": "https://example.com/kb123.msu", "target": "updates/kb123.msu"}
            ],
            "applications": [
                {
                    "id": "demo",
                    "source": "https://example.com/demo.exe",
                    "target": "apps/demo.exe",
                    "checksum": "abc123",
                }
            ],
        }
    )

    catalog = MediaCatalog.load(payload)

    drivers = list(catalog.drivers)
    updates = list(catalog.updates)
    apps = list(catalog.applications)

    assert drivers[0].install_type == InstallType.DRIVER
    assert updates[0].install_type == InstallType.UPDATE
    assert apps[0].checksum == "abc123"
    assert drivers[0].target_path == Path("drivers/gpu.exe")


def test_invalid_install_type_raises():
    payload = json.dumps(
        {
            "applications": [
                {
                    "id": "demo",
                    "source": "https://example.com/demo.exe",
                    "target": "apps/demo.exe",
                    "install_type": "invalid",
                }
            ]
        }
    )

    with pytest.raises(ValueError):
        MediaCatalog.load(payload)


def test_items_key_is_supported_for_backward_compatibility():
    payload = json.dumps({"items": [{"id": "legacy", "url": "https://example.com/legacy.exe"}]})

    catalog = MediaCatalog.load(payload)

    app = next(iter(catalog.all_entries()))
    assert app.identifier == "legacy"
    assert app.install_type == InstallType.APPLICATION
    assert app.target_path == Path("legacy")
