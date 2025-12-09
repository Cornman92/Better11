from __future__ import annotations

import subprocess
from typing import Iterable

from . import get_logger
from .safety import SafetyError, confirm_action, create_restore_point, ensure_windows


_LOGGER = get_logger(__name__)


def _remove_with_powershell(package: str) -> None:
    command = [
        "powershell",
        "-NoProfile",
        "-Command",
        f"Get-AppxPackage -Name '{package}' | Remove-AppxPackage",
    ]
    subprocess.run(command, check=True, capture_output=True, text=True)


def remove_bloatware(packages: Iterable[str], *, confirm: bool = True, input_func=input) -> None:
    """Remove a list of AppX packages with safety checks."""
    ensure_windows()
    packages = list(packages)
    if not packages:
        _LOGGER.info("No bloatware packages specified.")
        return

    create_restore_point("Bloatware removal via Better11")
    if confirm and not confirm_action("Remove bundled applications?", input_func=input_func):
        raise SafetyError("Bloatware removal cancelled by the user.")

    for package in packages:
        _LOGGER.info("Removing package %s", package)
        try:
            _remove_with_powershell(package)
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            _LOGGER.error("Failed to remove package %s: %s", package, exc)
            raise SafetyError(f"Failed to remove package {package}.") from exc


__all__ = ["remove_bloatware"]
