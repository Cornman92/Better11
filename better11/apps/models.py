from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable, List, Optional


class InstallerType(str, Enum):
    MSI = "msi"
    EXE = "exe"
    APPX = "appx"

    @classmethod
    def from_filename(cls, filename: str) -> "InstallerType":
        suffix = filename.rsplit(".", maxsplit=1)[-1].lower()
        for candidate in cls:
            if candidate.value == suffix:
                return candidate
        raise ValueError(f"Unsupported installer type for file '{filename}'")


@dataclass(frozen=True)
class AppMetadata:
    """Description of a vetted application installer."""

    app_id: str
    name: str
    version: str
    uri: str
    sha256: str
    installer_type: InstallerType
    vetted_domains: List[str] = field(default_factory=list)
    signature: Optional[str] = None
    signature_key: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    silent_args: List[str] = field(default_factory=list)
    uninstall_command: Optional[str] = None

    def domain_is_vetted(self, hostname: str) -> bool:
        normalized = hostname.lower()
        return any(normalized == domain.lower() for domain in self.vetted_domains)

    def requires_signature_verification(self) -> bool:
        return bool(self.signature and self.signature_key)


@dataclass
class AppStatus:
    app_id: str
    version: str
    installer_path: str
    installed: bool
    dependencies_installed: List[str] = field(default_factory=list)


def ensure_unique_ids(metadata: Iterable[AppMetadata]) -> None:
    seen = set()
    for entry in metadata:
        if entry.app_id in seen:
            raise ValueError(f"Duplicate application id detected: {entry.app_id}")
        seen.add(entry.app_id)
