"""Application catalog management for Better11."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from .models import AppMetadata, InstallerType


class AppCatalog:
    """Manages the application catalog.

    Attributes
    ----------
    catalog_path : Path
        Path to the catalog JSON file
    _apps : Dict[str, AppMetadata]
        Dictionary of app_id to AppMetadata
    """

    def __init__(self, catalog_path: Path) -> None:
        """Initialize the catalog.

        Parameters
        ----------
        catalog_path : Path
            Path to the catalog JSON file
        """
        self.catalog_path = catalog_path
        self._apps: Dict[str, AppMetadata] = {}

    @classmethod
    def from_file(cls, catalog_path: Path) -> AppCatalog:
        """Load a catalog from a JSON file.

        Parameters
        ----------
        catalog_path : Path
            Path to the catalog JSON file

        Returns
        -------
        AppCatalog
            Loaded catalog instance

        Raises
        ------
        FileNotFoundError
            If the catalog file doesn't exist
        json.JSONDecodeError
            If the catalog file is not valid JSON
        """
        catalog = cls(catalog_path)
        catalog._load()
        return catalog

    def _load(self) -> None:
        """Load the catalog from the JSON file."""
        if not self.catalog_path.exists():
            raise FileNotFoundError(f"Catalog file not found: {self.catalog_path}")

        with self.catalog_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        applications = data.get("applications", [])
        for app_data in applications:
            app = self._parse_app(app_data)
            self._apps[app.app_id] = app

    def _parse_app(self, app_data: dict) -> AppMetadata:
        """Parse an application entry from the catalog.

        Parameters
        ----------
        app_data : dict
            Dictionary containing application metadata

        Returns
        -------
        AppMetadata
            Parsed application metadata
        """
        # Handle both Python style (snake_case) and JSON style (camelCase)
        installer_type_str = app_data.get("installer_type") or app_data.get("installerType", "exe")

        return AppMetadata(
            app_id=app_data.get("app_id") or app_data.get("appId"),
            name=app_data.get("name"),
            version=app_data.get("version"),
            uri=app_data.get("uri") or app_data.get("installerUrl"),
            sha256=app_data.get("sha256") or app_data.get("sha256Hash") or app_data.get("sha256hash", ""),
            installer_type=InstallerType(installer_type_str.lower()),
            vetted_domains=app_data.get("vetted_domains") or app_data.get("vettedDomains", []),
            dependencies=app_data.get("dependencies", []),
            uninstall_command=app_data.get("uninstall_command") or app_data.get("uninstallCommand"),
            signature=app_data.get("signature"),
            signature_key=app_data.get("signature_key") or app_data.get("signatureKey"),
            silent_args=app_data.get("silent_args") or app_data.get("installerArgs", "").split() if app_data.get("silent_args") or app_data.get("installerArgs") else [],
        )

    def get(self, app_id: str) -> AppMetadata:
        """Get application metadata by ID.

        Parameters
        ----------
        app_id : str
            Application identifier

        Returns
        -------
        AppMetadata
            Application metadata

        Raises
        ------
        KeyError
            If the application is not found in the catalog
        """
        if app_id not in self._apps:
            raise KeyError(f"Application '{app_id}' not found in catalog")
        return self._apps[app_id]

    def list_all(self) -> List[AppMetadata]:
        """Get all applications in the catalog.

        Returns
        -------
        List[AppMetadata]
            List of all application metadata
        """
        return list(self._apps.values())

    def add(self, app: AppMetadata) -> None:
        """Add an application to the catalog.

        Parameters
        ----------
        app : AppMetadata
            Application metadata to add
        """
        self._apps[app.app_id] = app

    def remove(self, app_id: str) -> None:
        """Remove an application from the catalog.

        Parameters
        ----------
        app_id : str
            Application identifier to remove

        Raises
        ------
        KeyError
            If the application is not found in the catalog
        """
        if app_id not in self._apps:
            raise KeyError(f"Application '{app_id}' not found in catalog")
        del self._apps[app_id]
