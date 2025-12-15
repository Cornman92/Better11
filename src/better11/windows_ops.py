"""Windows-specific helpers for running deployment tooling safely."""

from __future__ import annotations

import platform
import subprocess
from typing import Iterable, List


class UnsupportedPlatformError(RuntimeError):
    """Raised when a Windows-only operation is attempted on another platform."""


def is_windows() -> bool:
    """Return True when running on Windows."""

    return platform.system().lower() == "windows"


def require_windows(action: str = "This operation") -> None:
    """Raise an :class:`UnsupportedPlatformError` on non-Windows systems."""

    if not is_windows():
        raise UnsupportedPlatformError(f"{action} is only supported on Windows hosts.")


def _run_command(command: Iterable[str]) -> subprocess.CompletedProcess:
    """Execute a command and raise helpful errors on failure."""

    try:
        return subprocess.run(
            list(command),
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise UnsupportedPlatformError(
            "Required Windows deployment tools are not available on this system."
        ) from exc
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.strip() if exc.stderr else ""
        stdout = exc.stdout.strip() if exc.stdout else ""
        details = stderr or stdout or str(exc)
        raise RuntimeError(f"Command failed: {details}") from exc


def run_dism(arguments: List[str]) -> subprocess.CompletedProcess:
    """Invoke DISM with the provided arguments after validating platform."""

    require_windows("DISM")
    return _run_command(["dism.exe", *arguments])


def run_powershell(command: str | List[str]) -> subprocess.CompletedProcess:
    """Invoke a PowerShell command safely on Windows."""

    require_windows("PowerShell")
    script = command if isinstance(command, str) else " ".join(command)
    return _run_command(
        [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            script,
        ]
    )
