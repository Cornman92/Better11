import platform

import pytest

from better11.gaymr_pc import GaYmRPCInitializer, GaYmRPCLicense, GaYmRPCSource
from better11.interfaces import Version


def _set_platform(monkeypatch: pytest.MonkeyPatch, name: str) -> None:
    monkeypatch.setattr(platform, "system", lambda: name)


def test_initialization_disabled(monkeypatch: pytest.MonkeyPatch):
    _set_platform(monkeypatch, "Windows")
    initializer = GaYmRPCInitializer(
        enabled=False,
        source="service",
        service_name="GaYmR-PC",
        library_path="C:/Program Files/GaYmR-PC/gaymr_pc.dll",
        minimum_version="1.0.0",
    )

    result = initializer.initialize()

    assert result.enabled is False
    assert result.compatible is False
    assert "Feature flag disabled" in result.issues
    assert result.reason.startswith("GaYmR-PC integration disabled")


def test_service_source_ready(monkeypatch: pytest.MonkeyPatch):
    _set_platform(monkeypatch, "Windows")
    initializer = GaYmRPCInitializer(
        enabled=True,
        source="service",
        service_name="GaYmR-PC",
        library_path="C:/Program Files/GaYmR-PC/gaymr_pc.dll",
        minimum_version="1.2.0",
        service_probe=lambda name: True,
    )

    result = initializer.initialize()

    assert result.enabled is True
    assert result.source is GaYmRPCSource.SERVICE
    assert result.compatible is True
    assert result.detected_version == Version.parse("1.2.0")
    assert result.issues == []


def test_service_missing(monkeypatch: pytest.MonkeyPatch):
    _set_platform(monkeypatch, "Windows")
    initializer = GaYmRPCInitializer(
        enabled=True,
        source="service",
        service_name="GaYmR-PC",
        library_path="C:/Program Files/GaYmR-PC/gaymr_pc.dll",
        minimum_version="1.0.0",
        service_probe=lambda name: False,
    )

    result = initializer.initialize()

    assert result.compatible is False
    assert "Service 'GaYmR-PC' is not installed" in result.reason


def test_library_source_missing_file(monkeypatch: pytest.MonkeyPatch):
    _set_platform(monkeypatch, "Windows")
    initializer = GaYmRPCInitializer(
        enabled=True,
        source="library",
        service_name="GaYmR-PC",
        library_path="C:/does/not/exist.dll",
        minimum_version="1.0.0",
        library_probe=lambda path: False,
    )

    result = initializer.initialize()

    assert result.source is GaYmRPCSource.LIBRARY
    assert result.compatible is False
    assert "Library path" in result.reason


def test_non_windows_incompatible(monkeypatch: pytest.MonkeyPatch):
    _set_platform(monkeypatch, "Linux")
    initializer = GaYmRPCInitializer(
        enabled=True,
        source="service",
        service_name="GaYmR-PC",
        library_path="/tmp/libgaymr.so",
        minimum_version="1.0.0",
    )

    result = initializer.initialize()

    assert result.compatible is False
    assert "requires Windows" in result.reason


def test_license_metadata_respected(monkeypatch: pytest.MonkeyPatch):
    _set_platform(monkeypatch, "Windows")
    license_info = GaYmRPCLicense(
        name="GaYmR-PC Commercial License",
        url="https://vendor.example.com/gaymr-pc/eula",
        redistributable=False,
    )
    initializer = GaYmRPCInitializer(
        enabled=True,
        source="service",
        service_name="GaYmR-PC",
        library_path="C:/Program Files/GaYmR-PC/gaymr_pc.dll",
        minimum_version="1.1.0",
        service_probe=lambda name: True,
        license=license_info,
    )

    result = initializer.initialize()

    assert result.license.name == "GaYmR-PC Commercial License"
    assert result.license.url.endswith("/eula")
    assert result.license.redistributable is False
