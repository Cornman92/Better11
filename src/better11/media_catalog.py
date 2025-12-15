"""Media catalog modeling, validation, and serialization helpers."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Iterable, List


class InstallType(str, Enum):
    """Supported media installation categories."""

    DRIVER = "driver"
    UPDATE = "update"
    APPLICATION = "application"


@dataclass
class MediaEntry:
    """Representation of a media asset tracked in the catalog."""

    identifier: str
    source: str
    target_path: Path
    install_type: InstallType
    checksum: str | None = None

    def to_dict(self) -> dict:
        """Serialize the entry into a JSON-compatible dictionary."""

        payload = {
            "id": self.identifier,
            "source": self.source,
            "target": str(self.target_path),
            "install_type": self.install_type.value,
        }
        if self.checksum:
            payload["checksum"] = self.checksum
        return payload


@dataclass
class MediaCatalog:
    """Container for driver, update, and application media entries."""

    drivers: List[MediaEntry] = field(default_factory=list)
    updates: List[MediaEntry] = field(default_factory=list)
    applications: List[MediaEntry] = field(default_factory=list)

    @classmethod
    def load(cls, raw: str) -> "MediaCatalog":
        """Create a catalog from a JSON payload."""

        payload = json.loads(raw)
        if not isinstance(payload, dict):
            raise ValueError("Catalog payload must be a JSON object")

        def _parse_entries(key: str, default_install_type: InstallType) -> List[MediaEntry]:
            entries = payload.get(key, [])
            if entries is None:
                return []
            if not isinstance(entries, list):
                raise ValueError(f"Catalog section '{key}' must be a list")

            parsed: List[MediaEntry] = []
            for index, item in enumerate(entries):
                if not isinstance(item, dict):
                    raise ValueError(f"Item {index} in '{key}' must be an object")

                identifier = item.get("id")
                source = item.get("source")
                target = item.get("target")
                install_type = item.get("install_type") or default_install_type.value
                checksum = item.get("checksum")

                if not identifier or not source or not target:
                    raise ValueError(
                        f"Item {index} in '{key}' is missing required fields 'id', 'source', or 'target'"
                    )

                try:
                    parsed_install_type = InstallType(install_type)
                except ValueError as exc:
                    raise ValueError(
                        f"Item {index} in '{key}' has invalid install_type '{install_type}'"
                    ) from exc

                parsed.append(
                    MediaEntry(
                        identifier=str(identifier),
                        source=str(source),
                        target_path=Path(target),
                        install_type=parsed_install_type,
                        checksum=str(checksum) if checksum is not None else None,
                    )
                )
            return parsed

        if "items" in payload and not any(key in payload for key in ("drivers", "updates", "applications")):
            payload = {
                "applications": [
                    {
                        "id": item.get("id"),
                        "source": item.get("url"),
                        "target": item.get("id"),
                        "install_type": InstallType.APPLICATION.value,
                    }
                    for item in payload.get("items", [])
                ]
            }

        return cls(
            drivers=_parse_entries("drivers", InstallType.DRIVER),
            updates=_parse_entries("updates", InstallType.UPDATE),
            applications=_parse_entries("applications", InstallType.APPLICATION),
        )

    def all_entries(self) -> Iterable[MediaEntry]:
        """Iterate over all entries in the catalog."""

        yield from self.drivers
        yield from self.updates
        yield from self.applications

    def to_json(self, *, indent: int = 2) -> str:
        """Serialize the catalog to JSON."""

        payload = {
            "drivers": [entry.to_dict() for entry in self.drivers],
            "updates": [entry.to_dict() for entry in self.updates],
            "applications": [entry.to_dict() for entry in self.applications],
        }
        return json.dumps(payload, indent=indent)

    def add_entry(self, entry: MediaEntry) -> None:
        """Append a media entry to the appropriate category."""

        if entry.install_type == InstallType.DRIVER:
            self.drivers.append(entry)
        elif entry.install_type == InstallType.UPDATE:
            self.updates.append(entry)
        else:
            self.applications.append(entry)
