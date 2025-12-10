from __future__ import annotations

import logging
import platform
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Sequence


LOGGER = logging.getLogger(__name__)


class UnsupportedPlatformError(RuntimeError):
    """Raised when a Windows-only operation is invoked on another platform."""


def is_windows() -> bool:
    """Return True when executing on a Windows platform."""

    if sys.platform.startswith("win"):
        return True
    return platform.system().lower() == "windows"


def _validate_command(command: Sequence[str]) -> None:
    if not command:
        raise ValueError("Command sequence cannot be empty")
    for part in command:
        if not part:
            raise ValueError("Command segments must be non-empty strings")


def _run_windows_command(command: Sequence[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    if not is_windows():
        raise UnsupportedPlatformError("This operation is only supported on Windows hosts.")

    _validate_command(command)
    LOGGER.debug("Executing command: %s", " ".join(command))
    return subprocess.run(command, capture_output=True, text=True, check=check)


def run_dism(arguments: Iterable[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run a DISM command with safety checks."""

    command = ["dism.exe", *list(arguments)]
    return _run_windows_command(command, check=check)


def run_powershell(commands: Iterable[str] | str, *, check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run a PowerShell command safely with standard flags."""

    if isinstance(commands, str):
        payload = commands
    else:
        payload = "; ".join(commands)
    command = ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", payload]
    return _run_windows_command(command, check=check)


def resolve_path(path: str | Path) -> Path:
    """Normalize and resolve filesystem paths for Windows commands."""

    resolved = Path(path).expanduser().resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"Path does not exist: {resolved}")
    return resolved
