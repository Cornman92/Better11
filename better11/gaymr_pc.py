"""GaYmR-PC integration helpers.

This module centralizes runtime checks and initialization logic for the
GaYmR-PC integration. GaYmR-PC is treated as an external Windows service
that Better11 can talk to when enabled. No GaYmR-PC binaries are bundled
or redistributed by Better11; the integration only coordinates safety
checks, compatibility validation, and simple discovery of the running
service.
"""
from __future__ import annotations

import platform
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Callable, Optional

from better11.interfaces import Version


class GaYmRPCSource(Enum):
    """Supported GaYmR-PC distribution options."""

    SERVICE = "service"
    LIBRARY = "library"


@dataclass
class GaYmRPCLicense:
    """License information for the GaYmR-PC integration."""

    name: str = "External vendor license"
    url: str = "https://vendor.example.com/gaymr-pc/license"
    redistributable: bool = False


@dataclass
class GaYmRPCInitializationResult:
    """Result of GaYmR-PC initialization."""

    enabled: bool
    source: GaYmRPCSource
    compatible: bool
    issues: list[str]
    detected_version: Optional[Version] = None
    license: GaYmRPCLicense = field(default_factory=GaYmRPCLicense)

    @property
    def reason(self) -> str:
        """Concise status summary."""

        if not self.enabled:
            return "GaYmR-PC integration disabled via configuration"
        if not self.compatible and self.issues:
            return "; ".join(self.issues)
        return "GaYmR-PC integration ready"


class GaYmRPCInitializer:
    """Initialize GaYmR-PC integration based on configuration."""

    def __init__(
        self,
        *,
        enabled: bool,
        source: str,
        service_name: str,
        library_path: str,
        minimum_version: str,
        license: Optional[GaYmRPCLicense] = None,
        service_probe: Optional[Callable[[str], bool]] = None,
        library_probe: Optional[Callable[[str], bool]] = None,
    ) -> None:
        self.enabled = enabled
        self.source = GaYmRPCSource(source)
        self.service_name = service_name
        self.library_path = library_path
        self.minimum_version = Version.parse(minimum_version)
        self.license = license or GaYmRPCLicense()
        self._service_probe = service_probe or self._default_service_probe
        self._library_probe = library_probe or self._default_library_probe

    @staticmethod
    def _default_service_probe(service_name: str) -> bool:
        command = ["sc", "query", service_name]
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        return result.returncode == 0 and "STATE" in result.stdout

    @staticmethod
    def _default_library_probe(library_path: str) -> bool:
        return Path(library_path).exists()

    def _is_windows(self) -> bool:
        return platform.system().lower() == "windows"

    def _check_compatibility(self) -> list[str]:
        issues: list[str] = []
        if not self._is_windows():
            issues.append("GaYmR-PC requires Windows 10/11 or later")
            return issues

        if self.source is GaYmRPCSource.SERVICE:
            if not self._service_probe(self.service_name):
                issues.append(f"Service '{self.service_name}' is not installed or not reachable")
        elif self.source is GaYmRPCSource.LIBRARY:
            if not self._library_probe(self.library_path):
                issues.append(f"Library path '{self.library_path}' is not available")
        return issues

    def _detect_version(self) -> Optional[Version]:
        # In a full implementation this would query the service or library metadata.
        # For now we record the minimum version as the expected baseline so downstream
        # consumers can reason about compatibility.
        return self.minimum_version

    def initialize(self) -> GaYmRPCInitializationResult:
        if not self.enabled:
            return GaYmRPCInitializationResult(
                enabled=False,
                source=self.source,
                compatible=False,
                issues=["Feature flag disabled"],
                detected_version=None,
                license=self.license,
            )

        issues = self._check_compatibility()
        detected_version = self._detect_version()
        compatible = not issues and detected_version is not None and detected_version >= self.minimum_version

        return GaYmRPCInitializationResult(
            enabled=True,
            source=self.source,
            compatible=compatible,
            issues=issues,
            detected_version=detected_version,
            license=self.license,
        )


__all__ = [
    "GaYmRPCInitializer",
    "GaYmRPCInitializationResult",
    "GaYmRPCLicense",
    "GaYmRPCSource",
]
