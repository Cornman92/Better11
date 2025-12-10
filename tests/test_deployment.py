from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from better11 import cli
from better11 import windows_ops
from better11.deployment import WindowsDeploymentManager


def test_run_dism_rejects_non_windows(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(windows_ops, "is_windows", lambda: False)

    with pytest.raises(windows_ops.UnsupportedPlatformError):
        windows_ops.run_dism(["/Help"])


def test_service_image_invokes_mount(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(windows_ops, "is_windows", lambda: True)
    import better11.deployment as deployment_module

    monkeypatch.setattr(deployment_module, "is_windows", lambda: True)

    calls: list[list[str]] = []

    def fake_dism(args, **_: str) -> None:  # type: ignore[no-untyped-def]
        calls.append(list(args))

    monkeypatch.setattr(windows_ops, "run_dism", fake_dism)
    monkeypatch.setattr(deployment_module, "run_dism", fake_dism)

    image = tmp_path / "image.wim"
    image.write_text("dummy")
    mount_dir = tmp_path / "mount"

    manager = WindowsDeploymentManager()
    manager.service_image(image, mount_dir, drivers=[], features=[], updates=[], commit=False)

    assert any("/Mount-Image" in arg for arg in calls[0])
    assert any(arg.startswith("/Unmount-Image") for arg in calls[-1])


def test_deploy_cli_gracefully_blocks_non_windows(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "is_windows", lambda: False)
    runner = CliRunner()

    result = runner.invoke(cli.deploy, ["capture", "C:\\", "D:\\image.wim", "--name", "Test"])

    assert result.exit_code == 1
    assert "only available on Windows" in result.output
