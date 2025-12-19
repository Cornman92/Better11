from __future__ import annotations

import json
import os
import sys
import pathlib
from pathlib import Path
from typing import Callable, Iterable, Mapping

try:
    import _pytest.nodes as _pytest_nodes

    # Force pytest internals to use PosixPath semantics even if upstream tests
    # monkeypatch `os.name` to simulate Windows environments. This prevents
    # `WindowsPath` from being instantiated on non-Windows hosts, which causes
    # `NotImplementedError` during error reporting.
    _pytest_nodes.Path = pathlib.PosixPath  # type: ignore[attr-defined]
except Exception:
    # If pytest internals change, fallback gracefully without breaking tests.
    pass

# Prevent accidental promotion to WindowsPath on POSIX hosts. Some libraries
# instantiate ``WindowsPath`` when simulating Windows behavior; remapping it to
# ``PosixPath`` keeps path handling compatible in this environment.
pathlib.WindowsPath = pathlib.PosixPath  # type: ignore[attr-defined]

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
root_path = str(REPO_ROOT)
if root_path not in sys.path:
    sys.path.insert(0, root_path)

DEFAULT_CATALOG = REPO_ROOT / "better11" / "apps" / "catalog.json"
SAMPLES_DIR = REPO_ROOT / "better11" / "apps" / "samples"
_ORIGINAL_OS_NAME = os.name


@pytest.fixture(autouse=True)
def reset_os_name() -> None:
    """Ensure os.name mutations from tests don't leak across the suite."""

    yield
    os.name = _ORIGINAL_OS_NAME


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Guarantee OS name is restored before pytest teardown utilities run."""

    os.name = _ORIGINAL_OS_NAME


@pytest.fixture
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture
def samples_dir() -> Path:
    return SAMPLES_DIR


@pytest.fixture
def default_catalog_path() -> Path:
    return DEFAULT_CATALOG


@pytest.fixture
def manager_factory(tmp_path: Path):
    from better11.apps.manager import AppManager
    from better11.apps.runner import InstallerRunner

    def factory(**overrides):
        catalog_path: Path = overrides.get("catalog_path", DEFAULT_CATALOG)
        download_dir: Path = overrides.get("download_dir", tmp_path / "downloads")
        state_file: Path = overrides.get("state_file", tmp_path / "state.json")
        runner = overrides.get("runner", InstallerRunner(dry_run=True))
        downloader = overrides.get("downloader")
        verifier = overrides.get("verifier")
        return AppManager(
            catalog_path=catalog_path,
            download_dir=download_dir,
            state_file=state_file,
            runner=runner,
            downloader=downloader,
            verifier=verifier,
        )

    return factory


@pytest.fixture
def catalog_writer(tmp_path: Path) -> Callable[[Iterable[Mapping[str, object]]], Path]:
    def _write(entries: Iterable[Mapping[str, object]]) -> Path:
        catalog_path = tmp_path / "catalog.json"
        with catalog_path.open("w", encoding="utf-8") as handle:
            json.dump({"applications": list(entries)}, handle, indent=2)
        return catalog_path

    return _write


@pytest.fixture
def make_installer(tmp_path: Path) -> Callable[[str, bytes | str], Path]:
    def _make(filename: str, contents: bytes | str = b"payload") -> Path:
        path = tmp_path / filename
        data = contents if isinstance(contents, bytes) else contents.encode("utf-8")
        path.write_bytes(data)
        return path

    return _make


# Fixtures for new modules

@pytest.fixture
def mock_wim_file(tmp_path):
    """Create a mock WIM file for testing"""
    wim_path = tmp_path / "test.wim"
    wim_path.touch()
    return str(wim_path)


@pytest.fixture
def mock_iso_file(tmp_path):
    """Create a mock ISO file for testing"""
    iso_path = tmp_path / "test.iso"
    iso_path.touch()
    return str(iso_path)


@pytest.fixture
def mock_driver_dir(tmp_path):
    """Create a mock driver directory structure"""
    driver_dir = tmp_path / "drivers"
    driver_dir.mkdir()

    # Create mock INF files
    inf_content = """[Version]
Signature="$WINDOWS NT$"
Class=Display
ClassGUID={4d36e968-e325-11ce-bfc1-08002be10318}
Provider=TestProvider
DriverVer=01/01/2024,1.0.0.0
"""

    for i in range(3):
        inf_path = driver_dir / f"driver{i}.inf"
        inf_path.write_text(inf_content)

    return str(driver_dir)


@pytest.fixture
def mock_subprocess_success(monkeypatch):
    """Mock subprocess.run to return success"""
    import subprocess
    from unittest.mock import Mock

    def mock_run(*args, **kwargs):
        result = Mock()
        result.returncode = 0
        result.stdout = ""
        result.stderr = ""
        return result

    monkeypatch.setattr(subprocess, "run", mock_run)


@pytest.fixture
def sample_packages():
    """Sample package data for testing"""
    return [
        {
            "name": "TestPackage1",
            "package_id": "test.package1",
            "version": "1.0.0",
            "manager": "winget",
            "description": "Test package 1"
        },
        {
            "name": "TestPackage2",
            "package_id": "test.package2",
            "version": "2.0.0",
            "manager": "chocolatey",
            "description": "Test package 2"
        }
    ]


@pytest.fixture
def sample_drivers():
    """Sample driver data for testing"""
    return [
        {
            "class_name": "Display",
            "device_name": "Test GPU",
            "driver_provider": "TestVendor",
            "driver_version": "1.0.0.0",
            "driver_date": "2024-01-01",
            "inf_name": "testgpu.inf"
        },
        {
            "class_name": "Net",
            "device_name": "Test Network Adapter",
            "driver_provider": "TestVendor",
            "driver_version": "2.0.0.0",
            "driver_date": "2024-01-01",
            "inf_name": "testnet.inf"
        }
    ]


# Test markers
def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "windows_only: marks tests that only run on Windows"
    )
    config.addinivalue_line(
        "markers", "requires_admin: marks tests that require admin privileges"
    )
