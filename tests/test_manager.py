import shutil
from pathlib import Path

import pytest

from better11.apps.manager import AppManager, DependencyError
from better11.apps.models import AppMetadata, InstallerType
from better11.apps.runner import InstallerRunner
from better11.apps.verification import DownloadVerifier, VerificationError
from better11.cli import plan_installation

CATALOG_PATH = Path(__file__).resolve().parent.parent / "better11" / "apps" / "catalog.json"
SAMPLES_DIR = Path(__file__).resolve().parent.parent / "better11" / "apps" / "samples"


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


def test_build_install_plan_orders_dependencies(tmp_path: Path) -> None:
    manager = build_manager(tmp_path)
    manager.state_store.mark_installed("demo-exe", "1.0.0", tmp_path / "downloads" / "demo-app.exe")

    plan = manager.build_install_plan("demo-appx")

    assert [step.app_id for step in plan.steps] == ["demo-exe", "demo-msi", "demo-appx"]
    actions = {step.app_id: step.action for step in plan.steps}
    assert actions["demo-exe"] == "skip"
    assert actions["demo-msi"] == "install"
    assert actions["demo-appx"] == "install"


def test_build_install_plan_handles_missing_dependency(tmp_path: Path) -> None:
    manager = build_manager(tmp_path)
    missing_parent = AppMetadata(
        app_id="custom-app",
        name="Custom App",
        version="1.0.0",
        uri="samples/demo-app.exe",
        sha256="362238e1f381cc1592edf3ba3805f5997a9147fd9223f2ba9714a5c144ba92d6",
        installer_type=InstallerType.EXE,
        dependencies=["ghost-app"],
    )
    manager.catalog._apps[missing_parent.app_id] = missing_parent  # type: ignore[attr-defined]

    plan = manager.build_install_plan("custom-app")

    assert any("ghost-app" in warning for warning in plan.warnings)
    actions = {step.app_id: step.action for step in plan.steps}
    assert actions["ghost-app"] == "blocked"
    assert actions["custom-app"] == "blocked"


def test_build_install_plan_detects_cycles(tmp_path: Path) -> None:
    manager = build_manager(tmp_path)
    first = AppMetadata(
        app_id="cycle-a",
        name="Cycle A",
        version="1.0",
        uri="samples/demo-app.exe",
        sha256="362238e1f381cc1592edf3ba3805f5997a9147fd9223f2ba9714a5c144ba92d6",
        installer_type=InstallerType.EXE,
        dependencies=["cycle-b"],
    )
    second = AppMetadata(
        app_id="cycle-b",
        name="Cycle B",
        version="1.0",
        uri="samples/demo-app.exe",
        sha256="362238e1f381cc1592edf3ba3805f5997a9147fd9223f2ba9714a5c144ba92d6",
        installer_type=InstallerType.EXE,
        dependencies=["cycle-a"],
    )
    manager.catalog._apps[first.app_id] = first  # type: ignore[attr-defined]
    manager.catalog._apps[second.app_id] = second  # type: ignore[attr-defined]

    plan = manager.build_install_plan("cycle-a")

    assert any("cycle-a" in warning and "cycle-b" in warning for warning in plan.warnings)
    actions = {step.app_id: step.action for step in plan.steps}
    assert actions["cycle-a"] == "blocked"
    assert actions["cycle-b"] == "blocked"


def test_download_uses_cache_when_hash_matches(tmp_path: Path) -> None:
    manager = build_manager(tmp_path)
    app = manager.catalog.get("demo-exe")
    destination = manager.downloader.destination_for(app)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SAMPLES_DIR / "demo-app.exe", destination)

    path, cache_hit = manager.download("demo-exe")

    assert cache_hit is True
    assert path == destination


def test_download_replaces_corrupt_cache(tmp_path: Path) -> None:
    manager = build_manager(tmp_path)
    app = manager.catalog.get("demo-exe")
    destination = manager.downloader.destination_for(app)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("corrupt")

    path, cache_hit = manager.download("demo-exe")

    assert cache_hit is False
    assert path == destination
    # File should now verify
    manager.verifier.verify_hash(path, app.sha256)


def test_cli_plan_outputs_table(tmp_path: Path, capsys) -> None:
    manager = build_manager(tmp_path)

    exit_code = plan_installation(manager, "demo-exe")
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "ACTION" in captured.out
    assert "demo-exe" in captured.out
