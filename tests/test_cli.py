from __future__ import annotations

from pathlib import Path

import pytest

from better11 import cli
from better11.apps.download import DownloadError
from better11.apps.manager import DependencyError
from better11.apps.models import AppMetadata, AppStatus, InstallerType
from better11.apps.runner import InstallerResult


@pytest.fixture
def sample_metadata() -> AppMetadata:
    return AppMetadata(
        app_id="demo",
        name="Demo",
        version="1.0",
        uri="file://demo.exe",
        sha256="deadbeef",
        installer_type=InstallerType.EXE,
    )


def test_list_apps_writes_human_readable_entries(sample_metadata, capsys) -> None:
    manager = type(
        "Manager",
        (),
        {"list_available": lambda self: [sample_metadata]},
    )()

    exit_code = cli.list_apps(manager)

    assert exit_code == 0
    captured = capsys.readouterr()
    assert "demo" in captured.out
    assert "Demo" in captured.out


def test_install_app_reports_success(capsys) -> None:
    status = AppStatus(app_id="demo", version="1.0", installer_path="/tmp/demo.exe", installed=True)
    result = InstallerResult(["demo.exe"], 0, "", "")

    class Manager:
        def install(self, app_id):
            return status, result

    exit_code = cli.install_app(Manager(), "demo")
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "Installed demo" in captured.out


def test_install_app_surfaces_failures(capsys) -> None:
    class Manager:
        def install(self, app_id):
            raise DownloadError("boom")

    exit_code = cli.install_app(Manager(), "demo")
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Installation failed" in captured.err


def test_uninstall_app_handles_dependency_errors(capsys) -> None:
    class Manager:
        def uninstall(self, app_id):
            raise DependencyError("in use")

    exit_code = cli.uninstall_app(Manager(), "demo")
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Uninstall failed" in captured.err


def test_main_dispatches_commands(tmp_path: Path, monkeypatch) -> None:
    called = {}

    def fake_build_manager(catalog_path: Path):
        called["catalog"] = catalog_path
        return "manager"

    def fake_list(manager):
        called["manager"] = manager
        return 0

    monkeypatch.setattr(cli, "build_manager", fake_build_manager)
    monkeypatch.setattr(cli, "list_apps", fake_list)

    catalog = tmp_path / "catalog.json"
    catalog.write_text("{}")

    exit_code = cli.main(["--catalog", str(catalog), "list"])

    assert exit_code == 0
    assert called["catalog"] == catalog
    assert called["manager"] == "manager"


def test_handle_fetch_media_with_malformed_json(capsys):
    """Test error handling for malformed JSON in media catalog."""
    exit_code = cli.handle_fetch_media("{invalid_json}")

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Failed to load media catalog" in captured.err
    assert "Traceback" not in captured.err


def test_handle_fetch_media_missing_required_fields(capsys):
    """Test error handling for media catalog with missing fields."""
    import json
    payload = json.dumps({"items": [{"id": "media-1"}]})

    exit_code = cli.handle_fetch_media(payload)

    captured = capsys.readouterr()
    assert exit_code == 1
    assert "missing required field(s): url" in captured.err
    assert "Traceback" not in captured.err


def test_handle_fetch_media_success():
    """Test successful media catalog handling."""
    import json
    payload = json.dumps({"items": [{"id": "media-1", "url": "https://example.com"}]})

    exit_code = cli.handle_fetch_media(payload)

    assert exit_code == 0


def test_deploy_unattend_command(tmp_path: Path) -> None:
    output_file = tmp_path / "unattend.xml"

    exit_code = cli.main(
        [
            "deploy",
            "unattend",
            "--product-key",
            "AAAAA-BBBBB-CCCCC-DDDDD-EEEEE",
            "--output",
            str(output_file),
            "--language",
            "en-US",
            "--timezone",
            "UTC",
            "--admin-user",
            "Deployer",
            "--first-logon-command",
            "1:echo post setup",
        ]
    )

    assert exit_code == 0
    assert output_file.exists()
    content = output_file.read_text()
    assert "Deployer" in content
    assert "AAAAA-BBBBB-CCCCC-DDDDD-EEEEE" in content
