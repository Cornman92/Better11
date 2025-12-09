from __future__ import annotations

from pathlib import Path

from better11.apps.state_store import InstallationStateStore


def test_state_store_persists_between_sessions(tmp_path: Path) -> None:
    state_file = tmp_path / "state.json"
    store = InstallationStateStore(state_file)

    store.mark_installed("demo", "1.0", tmp_path / "demo.exe", dependencies=["dep"])
    status = store.get("demo")
    assert status is not None
    assert status.installed

    store.mark_uninstalled("demo")
    status = store.get("demo")
    assert status is not None and not status.installed

    reloaded = InstallationStateStore(state_file)
    reloaded_status = reloaded.get("demo")
    assert reloaded_status is not None
    assert not reloaded_status.installed
    assert reloaded_status.dependencies_installed == ["dep"]
