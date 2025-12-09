from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from .catalog import AppCatalog
from .download import AppDownloader
from .models import AppMetadata, AppStatus
from .runner import InstallerResult, InstallerRunner
from .state_store import InstallationStateStore
from .verification import DownloadVerifier

logger = logging.getLogger(__name__)


class DependencyError(RuntimeError):
    pass


class AppManager:
    """Coordinates catalog lookup, downloading, verification, and installation."""

    def __init__(
        self,
        catalog_path: Path,
        download_dir: Optional[Path] = None,
        state_file: Optional[Path] = None,
        downloader: Optional[AppDownloader] = None,
        verifier: Optional[DownloadVerifier] = None,
        runner: Optional[InstallerRunner] = None,
    ) -> None:
        self.catalog_path = catalog_path
        self.catalog = AppCatalog.from_file(catalog_path)
        self.download_dir = download_dir or Path.home() / ".better11" / "downloads"
        self.state_file = state_file or Path.home() / ".better11" / "installed.json"
        self.downloader = downloader or AppDownloader(self.download_dir, catalog_path.parent)
        self.verifier = verifier or DownloadVerifier()
        self.runner = runner or InstallerRunner()
        self.state_store = InstallationStateStore(self.state_file)

    def list_available(self) -> List[AppMetadata]:
        return self.catalog.list_all()

    def download(self, app_id: str) -> Path:
        app = self.catalog.get(app_id)
        logger.info("Downloading %s from %s", app.name, app.uri)
        return self.downloader.download(app)

    def install(self, app_id: str) -> Tuple[AppStatus, InstallerResult]:
        visited: Set[str] = set()
        return self._install_recursive(app_id, visited)

    def _install_recursive(self, app_id: str, visited: Set[str]) -> Tuple[AppStatus, InstallerResult]:
        if app_id in visited:
            raise DependencyError(f"Circular dependency detected at {app_id}")
        visited.add(app_id)

        app = self.catalog.get(app_id)
        existing = self.state_store.get(app_id)
        if existing and existing.installed and existing.version == app.version:
            logger.info("%s is already installed (version %s)", app_id, app.version)
            return existing, InstallerResult([], 0, "already installed", "")

        dependency_statuses: Dict[str, AppStatus] = {}
        for dependency_id in app.dependencies:
            dep_status, _ = self._install_recursive(dependency_id, visited)
            dependency_statuses[dependency_id] = dep_status

        installer_path = self.download(app_id)
        self.verifier.verify(app, installer_path)
        result = self.runner.install(app, installer_path)
        status = self.state_store.mark_installed(
            app.app_id,
            app.version,
            installer_path,
            dependencies=list(dependency_statuses.keys()),
        )
        return status, result

    def uninstall(self, app_id: str) -> InstallerResult:
        self._ensure_not_required_by_dependents(app_id)
        status = self.state_store.get(app_id)
        if not status or not status.installed:
            raise DependencyError(f"{app_id} is not currently installed")

        app = self.catalog.get(app_id)
        installer_path = Path(status.installer_path) if status.installer_path else None
        result = self.runner.uninstall(app, installer_path)
        self.state_store.mark_uninstalled(app_id)
        return result

    def _ensure_not_required_by_dependents(self, app_id: str) -> None:
        dependents = []
        for candidate in self.catalog.list_all():
            if app_id in candidate.dependencies:
                status = self.state_store.get(candidate.app_id)
                if status and status.installed:
                    dependents.append(candidate.app_id)
        if dependents:
            joined = ", ".join(sorted(dependents))
            raise DependencyError(f"Cannot uninstall {app_id}; required by: {joined}")

    def status(self, app_id: Optional[str] = None) -> List[AppStatus]:
        if app_id:
            status = self.state_store.get(app_id)
            return [status] if status else []
        return self.state_store.list()

    def summarized_status(self, app_id: Optional[str] = None) -> List[str]:
        messages = []
        for entry in self.status(app_id):
            if entry:
                messages.append(
                    f"{entry.app_id} v{entry.version}: {'installed' if entry.installed else 'not installed'}"
                )
        return messages

    def ensure_directories(self) -> None:
        os.makedirs(self.download_dir, exist_ok=True)
        os.makedirs(self.state_file.parent, exist_ok=True)
