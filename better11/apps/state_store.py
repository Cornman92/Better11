from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from .models import AppStatus


class InstallationStateStore:
    def __init__(self, state_file: Path):
        self.state_file = state_file
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self._state: Dict[str, AppStatus] = {}
        if self.state_file.exists():
            self._load()

    def _load(self) -> None:
        with self.state_file.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        for app_id, entry in data.items():
            self._state[app_id] = AppStatus(
                app_id=app_id,
                version=entry["version"],
                installer_path=entry["installer_path"],
                installed=entry["installed"],
                dependencies_installed=entry.get("dependencies_installed", []),
            )

    def _persist(self) -> None:
        serialized = {
            app_id: {
                "version": status.version,
                "installer_path": status.installer_path,
                "installed": status.installed,
                "dependencies_installed": status.dependencies_installed,
            }
            for app_id, status in self._state.items()
        }
        with self.state_file.open("w", encoding="utf-8") as handle:
            json.dump(serialized, handle, indent=2)

    def mark_installed(
        self, app_id: str, version: str, installer_path: Path, dependencies: Optional[List[str]] = None
    ) -> AppStatus:
        status = AppStatus(
            app_id=app_id,
            version=version,
            installer_path=str(installer_path),
            installed=True,
            dependencies_installed=dependencies or [],
        )
        self._state[app_id] = status
        self._persist()
        return status

    def mark_uninstalled(self, app_id: str) -> None:
        if app_id in self._state:
            self._state[app_id].installed = False
            self._persist()

    def get(self, app_id: str) -> Optional[AppStatus]:
        return self._state.get(app_id)

    def list(self) -> List[AppStatus]:
        return list(self._state.values())
