from pathlib import Path

import pytest

from better11.apps.manager import AppManager, DependencyError
from better11.apps.runner import InstallerRunner
from better11.apps.verification import DownloadVerifier, VerificationError

CATALOG_PATH = Path(__file__).resolve().parent.parent / "better11" / "apps" / "catalog.json"


def build_manager(tmp_path: Path) -> AppManager:
    return AppManager(
        catalog_path=CATALOG_PATH,
        download_dir=tmp_path / "downloads",
        state_file=tmp_path / "state.json",
        runner=InstallerRunner(dry_run=True),
    )


def test_install_with_dependencies(tmp_path: Path) -> None:
    manager = build_manager(tmp_path)

    status, result = manager.install("demo-appx")

    assert status.installed
    assert "demo-msi" in status.dependencies_installed
    assert result.returncode == 0

    dependency_status = manager.state_store.get("demo-msi")
    assert dependency_status is not None and dependency_status.installed

    leaf_status = manager.state_store.get("demo-exe")
    assert leaf_status is not None and leaf_status.installed


def test_signature_failure(tmp_path: Path) -> None:
    verifier = DownloadVerifier()
    target_file = Path(__file__).resolve().parent.parent / "better11" / "apps" / "samples" / "demo-app.exe"

    with pytest.raises(VerificationError):
        verifier.verify_signature(target_file, "ZmFrZXNpZ25hdHVyZQ==", "ZmFrZWtleQ==")


def test_uninstall_prevents_breaking_dependencies(tmp_path: Path) -> None:
    manager = build_manager(tmp_path)
    manager.install("demo-appx")

    with pytest.raises(DependencyError):
        manager.uninstall("demo-msi")

    manager.uninstall("demo-appx")
    manager.uninstall("demo-msi")
    manager.uninstall("demo-exe")

    statuses = manager.status()
    assert all(not status.installed for status in statuses)
