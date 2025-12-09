from __future__ import annotations

import os
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence

from .models import AppMetadata, InstallerType


@dataclass
class InstallerResult:
    command: List[str]
    returncode: int
    stdout: str
    stderr: str


class InstallerError(RuntimeError):
    pass


class InstallerRunner:
    """Executes Windows installers with optional dry-run support."""

    def __init__(self, dry_run: bool | None = None):
        # default to dry-run on non-Windows hosts to keep tests safe
        self.dry_run = os.name != "nt" if dry_run is None else dry_run

    def _execute(self, command: Sequence[str]) -> InstallerResult:
        if self.dry_run:
            return InstallerResult(list(command), 0, "", "")

        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            raise InstallerError(
                f"Installer failed with exit code {completed.returncode}: {completed.stderr.strip()}"
            )
        return InstallerResult(list(command), completed.returncode, completed.stdout, completed.stderr)

    def install(self, app: AppMetadata, installer_path: Path) -> InstallerResult:
        command = self._install_command(app, installer_path)
        return self._execute(command)

    def uninstall(self, app: AppMetadata, installer_path: Path | None = None) -> InstallerResult:
        command = self._uninstall_command(app, installer_path)
        return self._execute(command)

    def _install_command(self, app: AppMetadata, installer_path: Path) -> List[str]:
        if app.installer_type == InstallerType.MSI:
            base = ["msiexec", "/i", str(installer_path), "/qn", "/norestart"]
            return base + app.silent_args
        if app.installer_type == InstallerType.EXE:
            default_args = ["/quiet", "/norestart"] if not app.silent_args else []
            return [str(installer_path)] + (app.silent_args or default_args)
        if app.installer_type == InstallerType.APPX:
            command = f"Add-AppxPackage -ForceApplicationShutdown \"{installer_path}\""
            return ["powershell", "-NoProfile", "-Command", command]
        raise InstallerError(f"Unsupported installer type: {app.installer_type}")

    def _uninstall_command(self, app: AppMetadata, installer_path: Path | None) -> List[str]:
        if app.uninstall_command:
            return shlex.split(app.uninstall_command)

        if app.installer_type == InstallerType.MSI:
            if installer_path is None:
                raise InstallerError("MSI uninstall requires installer_path when uninstall_command is not provided")
            return ["msiexec", "/x", str(installer_path), "/qn", "/norestart"]

        if app.installer_type == InstallerType.APPX:
            raise InstallerError("AppX uninstall requires an explicit uninstall_command with package identity")

        if app.installer_type == InstallerType.EXE:
            raise InstallerError("Executable uninstall requires an explicit uninstall_command")

        raise InstallerError(f"Unsupported installer type: {app.installer_type}")
