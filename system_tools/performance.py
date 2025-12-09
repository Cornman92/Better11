from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List

from . import get_logger
from .registry import RegistryTweak, apply_tweaks
from .safety import SafetyError, confirm_action, create_restore_point, ensure_windows
from .services import ServiceAction, apply_service_actions


_LOGGER = get_logger(__name__)


@dataclass
class PerformancePreset:
    name: str
    registry_tweaks: List[RegistryTweak] = field(default_factory=list)
    service_actions: List[ServiceAction] = field(default_factory=list)
    description: str = ""


def apply_performance_preset(
    preset: PerformancePreset,
    *,
    confirm: bool = True,
    input_func=input,
) -> None:
    """Apply a performance preset composed of registry tweaks and service actions."""
    ensure_windows()
    if confirm and not confirm_action(f"Apply performance preset '{preset.name}'?", input_func=input_func):
        raise SafetyError("Performance preset application cancelled by the user.")

    create_restore_point(f"Performance preset: {preset.name}")

    if preset.registry_tweaks:
        apply_tweaks(
            preset.registry_tweaks,
            confirm=False,
            create_backup=True,
            create_restore=False,
            input_func=input_func,
        )
    if preset.service_actions:
        apply_service_actions(
            preset.service_actions,
            confirm=False,
            create_restore=False,
            input_func=input_func,
        )
    _LOGGER.info("Applied performance preset '%s'", preset.name)


__all__ = ["PerformancePreset", "apply_performance_preset"]
