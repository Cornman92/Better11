"""Installation state management for Better11 applications."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from .models import AppStatus

logger = logging.getLogger(__name__)


class InstallationStateStore:
    """Manages persistent installation state for applications.

    The state is stored in a JSON file that tracks which applications
    are installed, their versions, and their dependencies.

    Attributes
    ----------
    state_file : Path
        Path to the state JSON file
    _state : Dict[str, AppStatus]
        In-memory cache of installation state
    """

    def __init__(self, state_file: Path) -> None:
        """Initialize the state store.

        Parameters
        ----------
        state_file : Path
            Path to the state JSON file
        """
        self.state_file = state_file
        self._state: Dict[str, AppStatus] = {}
        self._load()

    def _load(self) -> None:
        """Load state from the JSON file.

        If the file doesn't exist, initializes with empty state.
        """
        if not self.state_file.exists():
            logger.info("State file not found, initializing empty state: %s", self.state_file)
            return

        try:
            with self.state_file.open("r", encoding="utf-8") as f:
                data = json.load(f)

            for app_id, app_data in data.items():
                self._state[app_id] = AppStatus(
                    app_id=app_data["app_id"],
                    version=app_data["version"],
                    installed=app_data["installed"],
                    installer_path=app_data.get("installer_path", ""),
                    dependencies_installed=app_data.get("dependencies_installed", []),
                )
            logger.info("Loaded state for %d applications", len(self._state))
        except Exception as exc:
            logger.error("Failed to load state file: %s", exc)
            # Continue with empty state rather than failing

    def _save(self) -> None:
        """Save state to the JSON file."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        data = {}
        for app_id, status in self._state.items():
            data[app_id] = {
                "app_id": status.app_id,
                "version": status.version,
                "installed": status.installed,
                "installer_path": status.installer_path,
                "dependencies_installed": status.dependencies_installed,
            }

        try:
            with self.state_file.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            logger.debug("Saved state to %s", self.state_file)
        except Exception as exc:
            logger.error("Failed to save state file: %s", exc)
            raise

    def get(self, app_id: str) -> Optional[AppStatus]:
        """Get the installation status for an application.

        Parameters
        ----------
        app_id : str
            Application identifier

        Returns
        -------
        Optional[AppStatus]
            Installation status if found, None otherwise
        """
        return self._state.get(app_id)

    def list(self) -> List[AppStatus]:
        """Get all installation statuses.

        Returns
        -------
        List[AppStatus]
            List of all installation statuses
        """
        return list(self._state.values())

    def mark_installed(
        self,
        app_id: str,
        version: str,
        installer_path: Path,
        dependencies: Optional[List[str]] = None,
    ) -> AppStatus:
        """Mark an application as installed.

        Parameters
        ----------
        app_id : str
            Application identifier
        version : str
            Installed version
        installer_path : Path
            Path where the installer was cached
        dependencies : Optional[List[str]], optional
            List of dependency app_ids that were installed

        Returns
        -------
        AppStatus
            Updated installation status
        """
        status = AppStatus(
            app_id=app_id,
            version=version,
            installed=True,
            installer_path=str(installer_path),
            dependencies_installed=dependencies or [],
        )
        self._state[app_id] = status
        self._save()
        logger.info("Marked %s v%s as installed", app_id, version)
        return status

    def mark_uninstalled(self, app_id: str) -> None:
        """Mark an application as uninstalled.

        Parameters
        ----------
        app_id : str
            Application identifier
        """
        if app_id in self._state:
            self._state[app_id].installed = False
            self._save()
            logger.info("Marked %s as uninstalled", app_id)

    def remove(self, app_id: str) -> None:
        """Remove an application from the state store entirely.

        Parameters
        ----------
        app_id : str
            Application identifier
        """
        if app_id in self._state:
            del self._state[app_id]
            self._save()
            logger.info("Removed %s from state store", app_id)

    def clear(self) -> None:
        """Clear all installation state."""
        self._state.clear()
        self._save()
        logger.info("Cleared all installation state")
