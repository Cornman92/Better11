from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from . import get_logger
from .safety import SafetyError, backup_registry_key, confirm_action, create_restore_point, ensure_windows
from .winreg_compat import winreg


_LOGGER = get_logger(__name__)


@dataclass
class RegistryTweak:
    """Represents a registry change."""

    hive: str
    path: str
    name: str
    value: object
    value_type: int

    @property
    def full_path(self) -> str:
        return f"{self.hive}\\{self.path}"


def _open_key(tweak: RegistryTweak):
    hive = getattr(winreg, tweak.hive)
    return winreg.CreateKeyEx(hive, tweak.path)


def apply_tweak(tweak: RegistryTweak) -> None:
    """Apply a single registry tweak with logging and error handling."""
    ensure_windows()
    _LOGGER.info("Applying registry tweak at %s", tweak.full_path)
    try:
        with _open_key(tweak) as key:
            winreg.SetValueEx(key, tweak.name, 0, tweak.value_type, tweak.value)
    except OSError as exc:
        _LOGGER.error("Failed to apply registry tweak %s: %s", tweak.full_path, exc)
        raise SafetyError(f"Unable to apply registry tweak at {tweak.full_path}.") from exc


def apply_tweaks(
    tweaks: Iterable[RegistryTweak],
    *,
    confirm: bool = True,
    create_backup: bool = True,
    create_restore: bool = True,
    input_func=input,
) -> None:
    """Apply multiple registry tweaks with safeguards."""
    ensure_windows()
    tweaks = list(tweaks)
    if not tweaks:
        _LOGGER.info("No registry tweaks provided; skipping.")
        return

    if create_restore:
        create_restore_point("Registry changes for Better11")

    if confirm and not confirm_action("Apply registry tweaks?", input_func=input_func):
        raise SafetyError("Registry tweaks were cancelled by the user.")

    backed_up_paths = set()
    for tweak in tweaks:
        if create_backup and tweak.full_path not in backed_up_paths:
            backup_registry_key(tweak.full_path)
            backed_up_paths.add(tweak.full_path)
        apply_tweak(tweak)


__all__ = ["RegistryTweak", "apply_tweak", "apply_tweaks"]
