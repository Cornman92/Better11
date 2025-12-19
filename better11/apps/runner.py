"""Installer execution for Better11 applications."""

from __future__ import annotations

import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from .models import AppMetadata, InstallerType

logger = logging.getLogger(__name__)


class InstallerError(RuntimeError):
    """Raised when installer execution fails."""
    pass


@dataclass
class InstallerResult:
    """Result of an installer execution.

    Attributes
    ----------
    command : List[str]
        The command that was executed
    returncode : int
        Exit code from the installer
    stdout : str
        Standard output from the installer
    stderr : str
        Standard error from the installer
    """

    command: List[str]
    returncode: int
    stdout: str
    stderr: str


class InstallerRunner:
    """Executes application installers.

    Attributes
    ----------
    dry_run : bool
        If True, only generates commands without executing them
    """

    def __init__(self, dry_run: bool = False) -> None:
        """Initialize the installer runner.

        Parameters
        ----------
        dry_run : bool, optional
            If True, commands are generated but not executed (default: False)
        """
        self.dry_run = dry_run

    def install(self, app: AppMetadata, installer_path: Path) -> InstallerResult:
        """Install an application.

        Parameters
        ----------
        app : AppMetadata
            Application metadata
        installer_path : Path
            Path to the installer file

        Returns
        -------
        InstallerResult
            Result of the installation

        Raises
        ------
        InstallerError
            If the installer type is not supported
        """
        command = self._build_install_command(app, installer_path)
        return self._execute(command)

    def uninstall(self, app: AppMetadata, installer_path: Optional[Path] = None) -> InstallerResult:
        """Uninstall an application.

        Parameters
        ----------
        app : AppMetadata
            Application metadata
        installer_path : Optional[Path], optional
            Path to the installer file (may be needed for some uninstalls)

        Returns
        -------
        InstallerResult
            Result of the uninstallation

        Raises
        ------
        InstallerError
            If uninstall command is missing or installer type is not supported
        """
        command = self._build_uninstall_command(app, installer_path)
        return self._execute(command)

    def _build_install_command(self, app: AppMetadata, installer_path: Path) -> List[str]:
        """Build the installation command based on installer type.

        Parameters
        ----------
        app : AppMetadata
            Application metadata
        installer_path : Path
            Path to the installer file

        Returns
        -------
        List[str]
            Command to execute

        Raises
        ------
        InstallerError
            If the installer type is not supported
        """
        installer_str = str(installer_path.absolute())

        if app.installer_type == InstallerType.MSI:
            command = ["msiexec", "/i", installer_str, "/quiet", "/norestart"]
            if app.silent_args:
                command.extend(app.silent_args)
            return command

        elif app.installer_type == InstallerType.EXE:
            command = [installer_str]
            if app.silent_args:
                command.extend(app.silent_args)
            return command

        elif app.installer_type == InstallerType.APPX:
            command = [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                f"Add-AppxPackage -Path '{installer_str}'"
            ]
            return command

        else:
            raise InstallerError(f"Unsupported installer type: {app.installer_type}")

    def _build_uninstall_command(self, app: AppMetadata, installer_path: Optional[Path] = None) -> List[str]:
        """Build the uninstallation command.

        Parameters
        ----------
        app : AppMetadata
            Application metadata
        installer_path : Optional[Path]
            Path to the installer file (may be needed for some uninstalls)

        Returns
        -------
        List[str]
            Command to execute

        Raises
        ------
        InstallerError
            If uninstall command is missing or installer type is not supported
        """
        if app.installer_type == InstallerType.MSI:
            if installer_path:
                return ["msiexec", "/x", str(installer_path.absolute()), "/quiet", "/norestart"]
            elif app.uninstall_command:
                return app.uninstall_command.split()
            else:
                raise InstallerError(f"MSI uninstall requires either installer_path or uninstall_command for {app.app_id}")

        elif app.installer_type == InstallerType.EXE:
            if not app.uninstall_command:
                raise InstallerError(f"EXE uninstall requires uninstall_command in catalog for {app.app_id}")
            return app.uninstall_command.split()

        elif app.installer_type == InstallerType.APPX:
            command = [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                f"Remove-AppxPackage -Package '{app.name}'"
            ]
            if app.uninstall_command:
                # Use custom uninstall command if provided
                command = app.uninstall_command.split()
            return command

        else:
            raise InstallerError(f"Unsupported installer type: {app.installer_type}")

    def _execute(self, command: List[str]) -> InstallerResult:
        """Execute a command and return the result.

        Parameters
        ----------
        command : List[str]
            Command to execute

        Returns
        -------
        InstallerResult
            Result of the execution
        """
        if self.dry_run:
            logger.info("DRY RUN: Would execute: %s", " ".join(command))
            return InstallerResult(
                command=command,
                returncode=0,
                stdout="",
                stderr=""
            )

        try:
            logger.info("Executing: %s", " ".join(command))
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
                timeout=3600  # 1 hour timeout
            )
            return InstallerResult(
                command=command,
                returncode=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr
            )
        except subprocess.TimeoutExpired as exc:
            raise InstallerError(f"Command timed out after 1 hour: {' '.join(command)}") from exc
        except Exception as exc:
            raise InstallerError(f"Failed to execute command: {exc}") from exc
