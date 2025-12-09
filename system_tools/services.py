from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import Iterable

from . import get_logger
from .safety import SafetyError, confirm_action, create_restore_point, ensure_windows


_LOGGER = get_logger(__name__)


@dataclass
class ServiceAction:
    name: str
    action: str  # start, stop, disable, enable

    def command(self) -> list[str]:
        if self.action == "start":
            return ["sc", "start", self.name]
        if self.action == "stop":
            return ["sc", "stop", self.name]
        if self.action == "disable":
            return ["sc", "config", self.name, "start=", "disabled"]
        if self.action == "enable":
            return ["sc", "config", self.name, "start=", "auto"]
        raise ValueError(f"Unsupported service action: {self.action}")


def apply_service_actions(
    actions: Iterable[ServiceAction],
    *,
    confirm: bool = True,
    create_restore: bool = True,
    input_func=input,
) -> None:
    ensure_windows()
    actions = list(actions)
    if not actions:
        _LOGGER.info("No service actions to apply.")
        return

    if create_restore:
        create_restore_point("Service changes for Better11")

    if confirm and not confirm_action("Modify Windows services?", input_func=input_func):
        raise SafetyError("Service changes were cancelled by the user.")

    for action in actions:
        command = action.command()
        _LOGGER.info("Executing service action %s on %s", action.action, action.name)
        try:
            subprocess.run(command, check=True, capture_output=True, text=True)
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            _LOGGER.error("Service action failed for %s: %s", action.name, exc)
            raise SafetyError(f"Failed to {action.action} service {action.name}.") from exc


__all__ = ["ServiceAction", "apply_service_actions"]
