from __future__ import annotations

import platform
import subprocess
import tempfile
from pathlib import Path
from typing import Callable, Optional

from . import get_logger


_LOGGER = get_logger(__name__)


class SafetyError(RuntimeError):
    """Raised when a safety precondition fails."""


def ensure_windows() -> None:
    """Ensure the current platform is Windows."""
    system = platform.system().lower()
    if system != "windows":
        raise SafetyError("Windows platform is required for this operation.")


def confirm_action(prompt: str, input_func: Callable[[str], str] = input) -> bool:
    """Prompt the user to confirm a sensitive action.

    Parameters
    ----------
    prompt: str
        The message shown to the user.
    input_func: Callable[[str], str]
        Input function, defaulting to :func:`input` for CLI interaction. Tests can
        inject a mock implementation.
    """
    response = input_func(f"{prompt} [y/N]: ").strip().lower()
    confirmed = response in {"y", "yes"}
    if confirmed:
        _LOGGER.info("User confirmed action: %s", prompt)
    else:
        _LOGGER.warning("User cancelled action: %s", prompt)
    return confirmed


def create_restore_point(description: str) -> None:
    """Create a system restore point using PowerShell.

    This is a best-effort operation: failures are logged and surfaced to callers
    as :class:`SafetyError` to discourage continuing without recovery options.
    """
    ensure_windows()
    command = [
        "powershell",
        "-NoProfile",
        "-Command",
        f"Checkpoint-Computer -Description '{description}' -RestorePointType 'MODIFY_SETTINGS'",
    ]
    _LOGGER.info("Creating restore point: %s", description)
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        _LOGGER.error("Failed to create restore point: %s", exc)
        raise SafetyError("Unable to create system restore point.") from exc


def backup_registry_key(key_path: str, destination: Optional[Path] = None) -> Path:
    """Export a registry key to the specified destination.

    Parameters
    ----------
    key_path: str
        Path of the registry key, e.g., ``HKCU\\Software\\MyApp``.
    destination: Path, optional
        Destination file path. If omitted, a temporary file is created.
    """
    ensure_windows()
    backup_path = destination or Path(tempfile.mkstemp(suffix=".reg")[1])
    command = ["reg", "export", key_path, str(backup_path), "/y"]
    _LOGGER.info("Backing up registry key %s to %s", key_path, backup_path)
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        _LOGGER.error("Registry backup failed for %s: %s", key_path, exc)
        raise SafetyError(f"Unable to back up registry key {key_path}.") from exc
    return backup_path


__all__ = [
    "SafetyError",
    "backup_registry_key",
    "confirm_action",
    "create_restore_point",
    "ensure_windows",
]
