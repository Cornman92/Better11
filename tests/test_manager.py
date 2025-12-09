from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from better11.apps.manager import DependencyError
from better11.apps.runner import InstallerRunner
from better11.apps.verification import DownloadVerifier, VerificationError

def test_install_with_dependencies(manager_factory, tmp_path: Path, default_catalog_path: Path) -> None:
    manager = manager_factory(catalog_path=default_catalog_path, runner=InstallerRunner(dry_run=True))

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


def test_uninstall_prevents_breaking_dependencies(manager_factory, tmp_path: Path, default_catalog_path: Path) -> None:
    manager = manager_factory(catalog_path=default_catalog_path, runner=InstallerRunner(dry_run=True))
    manager.install("demo-appx")

    with pytest.raises(DependencyError):
        manager.uninstall("demo-msi")

    manager.uninstall("demo-appx")
    manager.uninstall("demo-msi")
    manager.uninstall("demo-exe")

    statuses = manager.status()
    assert all(not status.installed for status in statuses)


def _catalog_entry(tmp_path: Path, app_id: str, *, dependencies: list[str] | None = None) -> dict[str, object]:
    payload = (tmp_path / f"{app_id}.exe")
    payload.write_text(app_id)
    sha256 = hashlib.sha256(payload.read_bytes()).hexdigest()
    return {
        "app_id": app_id,
        "name": app_id,
        "version": "1.0",
        "uri": str(payload),
        "sha256": sha256,
        "installer_type": "exe",
        "dependencies": dependencies or [],
    }


def test_shared_dependencies_do_not_trigger_false_cycle(catalog_writer, manager_factory, tmp_path: Path) -> None:
    catalog = catalog_writer(
        [
            _catalog_entry(tmp_path, "core"),
            _catalog_entry(tmp_path, "alpha", dependencies=["core"]),
            _catalog_entry(tmp_path, "beta", dependencies=["core"]),
        ]
    )
    manager = manager_factory(catalog_path=catalog)

    manager.install("alpha")
    manager.install("beta")

    core_status = manager.state_store.get("core")
    assert core_status is not None and core_status.installed


def test_circular_dependency_detection(catalog_writer, manager_factory, tmp_path: Path) -> None:
    catalog = catalog_writer(
        [
            _catalog_entry(tmp_path, "core", dependencies=["addon"]),
            _catalog_entry(tmp_path, "addon", dependencies=["core"]),
        ]
    )
    manager = manager_factory(catalog_path=catalog)

    with pytest.raises(DependencyError):
        manager.install("core")
