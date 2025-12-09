from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List
from urllib.parse import urlparse

from .models import AppMetadata, InstallerType, ensure_unique_ids


class AppCatalog:
    """Loads vetted application metadata from disk."""

    def __init__(self, applications: Iterable[AppMetadata]):
        materialized: List[AppMetadata] = list(applications)
        ensure_unique_ids(materialized)
        self._apps: Dict[str, AppMetadata] = {app.app_id: app for app in materialized}

    @classmethod
    def from_file(cls, path: Path) -> "AppCatalog":
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)

        if not isinstance(data, dict):
            raise ValueError("Catalog root must be a JSON object")

        raw_applications = data.get("applications")
        if raw_applications is None:
            raise ValueError("Catalog file is missing 'applications' array")
        if not isinstance(raw_applications, list):
            raise ValueError("'applications' must be a list of objects")

        applications: List[AppMetadata] = []
        for index, entry in enumerate(raw_applications):
            applications.append(cls._materialize_entry(entry, index))
        return cls(applications)

    @staticmethod
    def _materialize_entry(entry: object, index: int) -> AppMetadata:
        if not isinstance(entry, dict):
            raise ValueError(f"Application entry at index {index} must be an object")

        required_fields = ["app_id", "name", "version", "uri", "sha256", "installer_type"]
        for field_name in required_fields:
            if field_name not in entry:
                raise ValueError(f"Application entry {index} is missing required field '{field_name}'")
            if not isinstance(entry[field_name], str) or not entry[field_name].strip():
                raise ValueError(f"Field '{field_name}' in application entry {index} must be a non-empty string")

        parsed_uri = urlparse(entry["uri"])
        if not parsed_uri.scheme and not parsed_uri.path:
            raise ValueError(f"Application entry {index} contains an invalid uri: {entry['uri']}")

        vetted_domains = AppCatalog._coerce_string_list(entry, index, "vetted_domains")
        dependencies = AppCatalog._coerce_string_list(entry, index, "dependencies")
        silent_args = AppCatalog._coerce_string_list(entry, index, "silent_args")
        uninstall_command = entry.get("uninstall_command")
        if uninstall_command is not None and not isinstance(uninstall_command, str):
            raise ValueError(
                f"Field 'uninstall_command' in application entry {index} must be a string when provided"
            )

        signature = entry.get("signature")
        signature_key = entry.get("signature_key")
        if (signature and not signature_key) or (signature_key and not signature):
            raise ValueError(
                f"Application entry {index} must provide both 'signature' and 'signature_key' when signing is used"
            )

        try:
            installer_type = InstallerType(entry["installer_type"].lower())
        except Exception as exc:  # Enum raises ValueError for invalid names
            raise ValueError(
                f"Unsupported installer_type in application entry {index}: {entry['installer_type']}"
            ) from exc

        return AppMetadata(
            app_id=entry["app_id"],
            name=entry["name"],
            version=entry["version"],
            uri=entry["uri"],
            sha256=entry["sha256"],
            installer_type=installer_type,
            vetted_domains=vetted_domains,
            signature=signature,
            signature_key=signature_key,
            dependencies=dependencies,
            silent_args=silent_args,
            uninstall_command=uninstall_command,
        )

    @staticmethod
    def _coerce_string_list(entry: dict, index: int, field_name: str) -> List[str]:
        raw_value = entry.get(field_name, [])
        if raw_value is None:
            return []
        if not isinstance(raw_value, list) or not all(isinstance(item, str) for item in raw_value):
            raise ValueError(
                f"Field '{field_name}' in application entry {index} must be a list of strings if provided"
            )
        return raw_value

    def list_all(self) -> List[AppMetadata]:
        return list(self._apps.values())

    def get(self, app_id: str) -> AppMetadata:
        try:
            return self._apps[app_id]
        except KeyError as exc:
            raise KeyError(f"Unknown application id: {app_id}") from exc

    def __contains__(self, app_id: str) -> bool:
        return app_id in self._apps
