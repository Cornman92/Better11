from __future__ import annotations

import logging
import os
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Literal, Optional, Set, Tuple

from .catalog import AppCatalog
from .download import AppDownloader
from .models import AppMetadata, AppStatus
from .runner import InstallerResult, InstallerRunner
from .state_store import InstallationStateStore
from .verification import DownloadVerifier, VerificationError

logger = logging.getLogger(__name__)


class DependencyError(RuntimeError):
    pass


@dataclass
class InstallPlanStep:
    app_id: str
    name: str
    version: str
    dependencies: List[str]
    installed: bool
    action: Literal["install", "skip", "blocked"]
    notes: str = ""


@dataclass
class InstallPlanSummary:
    target_app_id: str
    steps: List[InstallPlanStep] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


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

    def download(self, app_id: str) -> Tuple[Path, bool]:
        app = self.catalog.get(app_id)
        destination = self.downloader.destination_for(app)
        cache_hit = False

        if destination.exists():
            try:
                self.verifier.verify_hash(destination, app.sha256)
                logger.info("Using cached installer for %s at %s", app.app_id, destination)
                cache_hit = True
            except VerificationError:
                logger.warning("Cached installer for %s failed verification; redownloading", app.app_id)
                destination.unlink(missing_ok=True)

        if not cache_hit:
            logger.info("Downloading %s from %s", app.name, app.uri)
            destination = self.downloader.download(app, destination=destination)

        return destination, cache_hit

    def install(self, app_id: str) -> Tuple[AppStatus, InstallerResult]:
        visited: Set[str] = set()
        return self._install_recursive(app_id, visited)

    def _install_recursive(self, app_id: str, visited: Set[str]) -> Tuple[AppStatus, InstallerResult]:
        if app_id in visited:
            raise DependencyError(f"Circular dependency detected at {app_id}")
        visited.add(app_id)
        try:
            app = self.catalog.get(app_id)
            existing = self.state_store.get(app_id)
            if existing and existing.installed and existing.version == app.version:
                logger.info("%s is already installed (version %s)", app_id, app.version)
                return existing, InstallerResult([], 0, "already installed", "")

        dependency_statuses: Dict[str, AppStatus] = {}
        for dependency_id in app.dependencies:
            dep_status, _ = self._install_recursive(dependency_id, visited)
            dependency_statuses[dependency_id] = dep_status

            installer_path, _ = self.download(app_id)
            self.verifier.verify(app, installer_path)
            result = self.runner.install(app, installer_path)
            status = self.state_store.mark_installed(
                app.app_id,
                app.version,
                installer_path,
                dependencies=list(dependency_statuses.keys()),
            )
            return status, result
        finally:
            visited.remove(app_id)

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

    def build_install_plan(self, app_id: str) -> InstallPlanSummary:
        summary = InstallPlanSummary(target_app_id=app_id)
        visited: Set[str] = set()
        visiting_stack: List[str] = []
        visiting_set: Set[str] = set()
        blocked_reasons: Dict[str, List[str]] = defaultdict(list)

        def add_block_reason(target: str, reason: str) -> None:
            if reason not in blocked_reasons[target]:
                blocked_reasons[target].append(reason)

        def add_warning(message: str) -> None:
            if message not in summary.warnings:
                summary.warnings.append(message)

        def dfs(current_id: str) -> None:
            if current_id in visited:
                return
            if current_id in visiting_set:
                cycle_start = visiting_stack.index(current_id)
                cycle = visiting_stack[cycle_start:] + [current_id]
                add_warning(f"Circular dependency detected: {' -> '.join(cycle)}")
                for node in cycle:
                    add_block_reason(node, "Cycle detected")
                return

            try:
                app = self.catalog.get(current_id)
            except KeyError:
                add_warning(f"Missing catalog entry for dependency '{current_id}'")
                add_block_reason(current_id, "Missing from catalog")
                summary.steps.append(
                    InstallPlanStep(
                        app_id=current_id,
                        name="(missing)",
                        version="unknown",
                        dependencies=[],
                        installed=False,
                        action="blocked",
                        notes="Missing from catalog",
                    )
                )
                visited.add(current_id)
                return

            visiting_stack.append(current_id)
            visiting_set.add(current_id)
            for dependency_id in app.dependencies:
                dfs(dependency_id)
                if dependency_id in blocked_reasons:
                    add_block_reason(app.app_id, f"Depends on blocked dependency: {dependency_id}")
            visiting_stack.pop()
            visiting_set.remove(current_id)

            status = self.state_store.get(app.app_id)
            is_installed = bool(status and status.installed and status.version == app.version)
            action: Literal["install", "skip", "blocked"] = "skip" if is_installed else "install"
            if app.app_id in blocked_reasons:
                action = "blocked"

            notes = "; ".join(blocked_reasons.get(app.app_id, []))
            summary.steps.append(
                InstallPlanStep(
                    app_id=app.app_id,
                    name=app.name,
                    version=app.version,
                    dependencies=list(app.dependencies),
                    installed=is_installed,
                    action=action,
                    notes=notes,
                )
            )
            visited.add(current_id)

        dfs(app_id)
        return summary
