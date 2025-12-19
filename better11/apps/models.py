"""Data models for Better11 application management."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional


class InstallerType(Enum):
    """Type of installer package."""
    MSI = "msi"
    EXE = "exe"
    APPX = "appx"


@dataclass
class AppMetadata:
    """Metadata for an installable application from the catalog.

    Attributes
    ----------
    app_id : str
        Unique identifier for the application
    name : str
        Human-readable application name
    version : str
        Version string
    uri : str
        Download URL or relative path to installer
    sha256 : str
        Expected SHA-256 hash of the installer
    installer_type : InstallerType
        Type of installer (MSI, EXE, APPX)
    vetted_domains : List[str]
        List of approved domains for downloads
    dependencies : List[str]
        List of app_ids that must be installed first
    uninstall_command : Optional[str]
        Command to uninstall (if not standard)
    signature : Optional[str]
        Base64-encoded HMAC signature for verification
    signature_key : Optional[str]
        Base64-encoded HMAC key for signature verification
    silent_args : List[str]
        Additional arguments for silent installation
    """

    app_id: str
    name: str
    version: str
    uri: str
    sha256: str
    installer_type: InstallerType
    vetted_domains: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    uninstall_command: Optional[str] = None
    signature: Optional[str] = None
    signature_key: Optional[str] = None
    silent_args: List[str] = field(default_factory=list)

    def domain_is_vetted(self, hostname: str) -> bool:
        """Check if a hostname is in the vetted domains list.

        Parameters
        ----------
        hostname : str
            The hostname to check

        Returns
        -------
        bool
            True if hostname is vetted or no vetting required
        """
        if not self.vetted_domains:
            return True
        return hostname in self.vetted_domains

    def requires_signature_verification(self) -> bool:
        """Check if HMAC signature verification is required.

        Returns
        -------
        bool
            True if both signature and signature_key are provided
        """
        return bool(self.signature and self.signature_key)


@dataclass
class AppStatus:
    """Installation status for an application.

    Attributes
    ----------
    app_id : str
        Unique identifier for the application
    version : str
        Installed version
    installed : bool
        Whether the application is currently installed
    installer_path : str
        Path where the installer was cached
    dependencies_installed : List[str]
        List of app_ids installed as dependencies
    """

    app_id: str
    version: str
    installed: bool
    installer_path: str
    dependencies_installed: List[str] = field(default_factory=list)
