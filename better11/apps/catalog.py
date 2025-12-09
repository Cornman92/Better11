from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List

from .models import AppMetadata, InstallerType, ensure_unique_ids


class AppCatalog:
    """Loads vetted application metadata from disk."""

    def __init__(self, applications: Iterable[AppMetadata]):
        self._apps: Dict[str, AppMetadata] = {app.app_id: app for app in applications}
        ensure_unique_ids(self._apps.values())

    @classmethod
    def from_file(cls, path: Path) -> "AppCatalog":
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)

        applications: List[AppMetadata] = []
        for entry in data.get("applications", []):
            applications.append(
                AppMetadata(
                    app_id=entry["app_id"],
                    name=entry["name"],
                    version=entry["version"],
                    uri=entry["uri"],
                    sha256=entry["sha256"],
                    installer_type=InstallerType(entry["installer_type"].lower()),
                    vetted_domains=entry.get("vetted_domains", []),
                    signature=entry.get("signature"),
                    signature_key=entry.get("signature_key"),
                    dependencies=entry.get("dependencies", []),
                    silent_args=entry.get("silent_args", []),
                    uninstall_command=entry.get("uninstall_command"),
                )
            )
        return cls(applications)

    def list_all(self) -> List[AppMetadata]:
        return list(self._apps.values())

    def get(self, app_id: str) -> AppMetadata:
        try:
            return self._apps[app_id]
        except KeyError as exc:
            raise KeyError(f"Unknown application id: {app_id}") from exc

    def __contains__(self, app_id: str) -> bool:
        return app_id in self._apps
