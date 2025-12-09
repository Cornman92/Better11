from __future__ import annotations

from pathlib import Path

import pytest

from better11.apps.models import AppMetadata, InstallerType
from better11.apps.runner import InstallerError, InstallerResult, InstallerRunner


def _app(app_id: str, installer_type: InstallerType) -> AppMetadata:
    return AppMetadata(
        app_id=app_id,
        name=app_id,
        version="1.0",
        uri=f"file://{app_id}.{installer_type.value}",
        sha256="deadbeef",
        installer_type=installer_type,
    )


def test_installer_runner_generates_commands_for_each_type(tmp_path: Path) -> None:
    runner = InstallerRunner(dry_run=True)
    installer_path = tmp_path / "demo.msi"
    installer_path.write_bytes(b"payload")

    msi_result = runner.install(_app("demo", InstallerType.MSI), installer_path)
    assert "/i" in msi_result.command

    exe_path = tmp_path / "demo.exe"
    exe_path.write_bytes(b"payload")
    exe_result = runner.install(_app("demo", InstallerType.EXE), exe_path)
    assert exe_result.command[0] == str(exe_path)

    appx_path = tmp_path / "demo.appx"
    appx_path.write_bytes(b"payload")
    appx_result = runner.install(_app("demo", InstallerType.APPX), appx_path)
    assert appx_result.command[:2] == ["powershell", "-NoProfile"]


def test_uninstall_requires_explicit_command_for_exe(tmp_path: Path) -> None:
    runner = InstallerRunner(dry_run=True)
    app = _app("demo", InstallerType.EXE)

    with pytest.raises(InstallerError):
        runner.uninstall(app)


def test_uninstall_uses_provided_command(tmp_path: Path) -> None:
    runner = InstallerRunner(dry_run=True)
    app = AppMetadata(
        app_id="demo",
        name="demo",
        version="1.0",
        uri="file://demo.exe",
        sha256="deadbeef",
        installer_type=InstallerType.EXE,
        uninstall_command="cmd /c echo demo",
    )

    result = runner.uninstall(app)
    assert "cmd" in result.command[0]
