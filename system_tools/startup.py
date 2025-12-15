"""Startup program management.

This module provides control over programs that run at Windows startup,
including registry entries, startup folders, and scheduled tasks.
"""
from __future__ import annotations

import os
import platform
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional

from . import get_logger
from .base import SystemTool, ToolMetadata

_LOGGER = get_logger(__name__)


class StartupLocation(Enum):
    """Location where startup item is configured."""
    
    REGISTRY_HKLM_RUN = "hklm_run"
    REGISTRY_HKCU_RUN = "hkcu_run"
    STARTUP_FOLDER_COMMON = "startup_common"
    STARTUP_FOLDER_USER = "startup_user"
    TASK_SCHEDULER = "task_scheduler"
    SERVICES = "services"


class StartupImpact(Enum):
    """Estimated impact of startup item on boot time."""
    
    HIGH = "high"      # >3s delay
    MEDIUM = "medium"  # 1-3s delay
    LOW = "low"        # <1s delay
    UNKNOWN = "unknown"


@dataclass
class StartupItem:
    """Representation of a startup program."""
    
    name: str
    command: str
    location: StartupLocation
    enabled: bool
    impact: StartupImpact = StartupImpact.UNKNOWN
    publisher: Optional[str] = None


# Registry paths for startup items
STARTUP_REGISTRY_PATHS = {
    "HKLM": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
    "HKCU": r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
}


class StartupManager(SystemTool):
    """Manage Windows startup programs.
    
    This class provides methods to list, enable, disable, and remove
    programs that run at Windows startup.
    
    Parameters
    ----------
    config : dict, optional
        Configuration dictionary
    dry_run : bool
        If True, simulate operations without making changes
    """
    
    def __init__(self, config: Optional[dict] = None, dry_run: bool = False):
        super().__init__(config, dry_run)
    
    def get_metadata(self) -> ToolMetadata:
        """Return tool metadata."""
        return ToolMetadata(
            name="Startup Manager",
            description="Manage Windows startup programs",
            version="0.3.0",
            requires_admin=False,  # Most operations don't need admin
            requires_restart=False,
            category="optimization"
        )
    
    def validate_environment(self) -> None:
        """Validate environment for startup management."""
        pass
    
    def execute(self) -> bool:
        """Execute default startup listing operation."""
        items = self.list_startup_items()
        _LOGGER.info("Found %d startup items", len(items))
        return True
    
    def list_startup_items(self) -> List[StartupItem]:
        """List all startup programs from all locations.

        Returns
        -------
        List[StartupItem]
            List of all startup items
        """
        _LOGGER.info("Listing startup items from all locations")

        items: List[StartupItem] = []

        # Get items from registry
        items.extend(self._get_registry_items())

        # Get items from startup folders
        items.extend(self._get_startup_folder_items())

        # Get items from scheduled tasks
        items.extend(self._get_scheduled_task_items())

        # Get items from services
        items.extend(self._get_service_items())

        _LOGGER.info("Found %d startup items", len(items))
        return items
    
    def _get_registry_items(self) -> List[StartupItem]:
        """Get startup items from Windows registry.
        
        Returns
        -------
        List[StartupItem]
            Startup items from registry
        """
        items: List[StartupItem] = []
        
        if platform.system() != "Windows":
            _LOGGER.debug("Not on Windows, skipping registry enumeration")
            return items
        
        try:
            import winreg
        except ImportError:
            _LOGGER.warning("winreg not available, skipping registry enumeration")
            return items
        
        # Check HKLM Run key
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                STARTUP_REGISTRY_PATHS["HKLM"],
                0,
                winreg.KEY_READ
            )
            items.extend(self._enumerate_registry_key(key, StartupLocation.REGISTRY_HKLM_RUN))
            winreg.CloseKey(key)
        except FileNotFoundError:
            _LOGGER.debug("HKLM Run key not found")
        except PermissionError:
            _LOGGER.warning("No permission to read HKLM Run key")
        except Exception as exc:
            _LOGGER.error("Error reading HKLM Run key: %s", exc)
        
        # Check HKCU Run key
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                STARTUP_REGISTRY_PATHS["HKCU"],
                0,
                winreg.KEY_READ
            )
            items.extend(self._enumerate_registry_key(key, StartupLocation.REGISTRY_HKCU_RUN))
            winreg.CloseKey(key)
        except FileNotFoundError:
            _LOGGER.debug("HKCU Run key not found")
        except Exception as exc:
            _LOGGER.error("Error reading HKCU Run key: %s", exc)
        
        return items
    
    def _enumerate_registry_key(self, key, location: StartupLocation) -> List[StartupItem]:
        """Enumerate a registry key for startup items.
        
        Parameters
        ----------
        key
            Open registry key handle
        location : StartupLocation
            Location type for these items
        
        Returns
        -------
        List[StartupItem]
            Startup items from this key
        """
        import winreg
        
        items: List[StartupItem] = []
        index = 0
        
        while True:
            try:
                name, command, value_type = winreg.EnumValue(key, index)
                
                if command and isinstance(command, str):
                    item = StartupItem(
                        name=name,
                        command=command,
                        location=location,
                        enabled=True,  # If in registry, it's enabled
                        impact=StartupImpact.UNKNOWN
                    )
                    items.append(item)
                    _LOGGER.debug("Found startup item: %s -> %s", name, command)
                
                index += 1
            except OSError:
                # No more items
                break
        
        return items
    
    def _get_startup_folder_items(self) -> List[StartupItem]:
        """Get startup items from startup folders.
        
        Returns
        -------
        List[StartupItem]
            Startup items from folders
        """
        items: List[StartupItem] = []
        
        if platform.system() != "Windows":
            _LOGGER.debug("Not on Windows, skipping startup folders")
            return items
        
        # Common startup folder (all users)
        try:
            programdata = os.environ.get('PROGRAMDATA', 'C:\\ProgramData')
            common_startup = Path(programdata) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup'
            items.extend(self._enumerate_startup_folder(common_startup, StartupLocation.STARTUP_FOLDER_COMMON))
        except Exception as exc:
            _LOGGER.error("Error reading common startup folder: %s", exc)
        
        # User startup folder
        try:
            appdata = os.environ.get('APPDATA', '')
            if appdata:
                user_startup = Path(appdata) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup'
                items.extend(self._enumerate_startup_folder(user_startup, StartupLocation.STARTUP_FOLDER_USER))
        except Exception as exc:
            _LOGGER.error("Error reading user startup folder: %s", exc)
        
        return items
    
    def _enumerate_startup_folder(self, folder: Path, location: StartupLocation) -> List[StartupItem]:
        """Enumerate a startup folder for items.
        
        Parameters
        ----------
        folder : Path
            Startup folder path
        location : StartupLocation
            Location type
        
        Returns
        -------
        List[StartupItem]
            Startup items from folder
        """
        items: List[StartupItem] = []
        
        if not folder.exists():
            _LOGGER.debug("Startup folder does not exist: %s", folder)
            return items
        
        try:
            for item_path in folder.iterdir():
                if item_path.is_file():
                    # Get the shortcut target if it's a .lnk file
                    command = str(item_path)
                    
                    item = StartupItem(
                        name=item_path.stem,
                        command=command,
                        location=location,
                        enabled=True,
                        impact=StartupImpact.UNKNOWN
                    )
                    items.append(item)
                    _LOGGER.debug("Found startup item in folder: %s", item_path.name)
        except PermissionError:
            _LOGGER.warning("No permission to read startup folder: %s", folder)
        except Exception as exc:
            _LOGGER.error("Error enumerating startup folder %s: %s", folder, exc)
        
        return items

    def _get_scheduled_task_items(self) -> List[StartupItem]:
        """Get startup items from scheduled tasks.

        Returns
        -------
        List[StartupItem]
            Startup items from scheduled tasks
        """
        items: List[StartupItem] = []

        if platform.system() != "Windows":
            _LOGGER.debug("Not on Windows, skipping scheduled tasks")
            return items

        try:
            # Query scheduled tasks that run at logon or startup
            result = subprocess.run(
                ["schtasks", "/query", "/fo", "CSV", "/v"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    # Parse CSV output (skip header)
                    for line in lines[1:]:
                        # Simple CSV parsing - looking for tasks that run at logon/startup
                        if '"At logon"' in line or '"At startup"' in line:
                            try:
                                # Extract task name (first field in CSV)
                                parts = line.split('","')
                                if len(parts) > 0:
                                    task_name = parts[0].strip('"')
                                    # Check if task is enabled (status field)
                                    enabled = '"Ready"' in line or '"Running"' in line

                                    item = StartupItem(
                                        name=task_name,
                                        command=f"Scheduled Task: {task_name}",
                                        location=StartupLocation.TASK_SCHEDULER,
                                        enabled=enabled,
                                        impact=StartupImpact.UNKNOWN
                                    )
                                    items.append(item)
                                    _LOGGER.debug("Found scheduled task: %s", task_name)
                            except Exception as exc:
                                _LOGGER.debug("Error parsing task line: %s", exc)
                                continue
        except subprocess.TimeoutExpired:
            _LOGGER.warning("Timeout while querying scheduled tasks")
        except FileNotFoundError:
            _LOGGER.debug("schtasks command not found")
        except Exception as exc:
            _LOGGER.error("Error querying scheduled tasks: %s", exc)

        return items

    def _get_service_items(self) -> List[StartupItem]:
        """Get startup items from Windows services.

        Returns
        -------
        List[StartupItem]
            Startup items from services with automatic startup
        """
        items: List[StartupItem] = []

        if platform.system() != "Windows":
            _LOGGER.debug("Not on Windows, skipping services")
            return items

        try:
            # Query services with automatic startup type
            result = subprocess.run(
                ["sc", "query", "type=", "service", "state=", "all"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                # Parse sc query output
                current_service = None
                service_state = None

                for line in result.stdout.split('\n'):
                    line = line.strip()

                    if line.startswith("SERVICE_NAME:"):
                        current_service = line.split(":", 1)[1].strip()
                    elif line.startswith("STATE") and current_service:
                        service_state = line
                    elif line.startswith("DISPLAY_NAME:") and current_service:
                        display_name = line.split(":", 1)[1].strip()

                        # Check if service has auto-start by querying config
                        try:
                            config_result = subprocess.run(
                                ["sc", "qc", current_service],
                                capture_output=True,
                                text=True,
                                timeout=5
                            )

                            if "AUTO_START" in config_result.stdout:
                                enabled = "RUNNING" in service_state if service_state else False

                                item = StartupItem(
                                    name=display_name,
                                    command=f"Service: {current_service}",
                                    location=StartupLocation.SERVICES,
                                    enabled=enabled,
                                    impact=StartupImpact.UNKNOWN
                                )
                                items.append(item)
                                _LOGGER.debug("Found auto-start service: %s", current_service)
                        except subprocess.TimeoutExpired:
                            _LOGGER.debug("Timeout checking service config for %s", current_service)
                        except Exception:
                            pass

                        current_service = None
                        service_state = None

        except subprocess.TimeoutExpired:
            _LOGGER.warning("Timeout while querying services")
        except FileNotFoundError:
            _LOGGER.debug("sc command not found")
        except Exception as exc:
            _LOGGER.error("Error querying services: %s", exc)

        return items

    def enable_startup_item(self, item: StartupItem) -> bool:
        """Enable a startup item.

        Parameters
        ----------
        item : StartupItem
            Startup item to enable

        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Enabling startup item: %s", item.name)

        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would enable startup item: %s", item.name)
            return True

        try:
            if item.location == StartupLocation.REGISTRY_HKLM_RUN:
                return self._enable_registry_item(item, "HKLM")
            elif item.location == StartupLocation.REGISTRY_HKCU_RUN:
                return self._enable_registry_item(item, "HKCU")
            elif item.location in (StartupLocation.STARTUP_FOLDER_COMMON, StartupLocation.STARTUP_FOLDER_USER):
                _LOGGER.info("Startup folder items are always enabled if present")
                return True
            else:
                _LOGGER.warning("Cannot enable items from location: %s", item.location)
                return False
        except Exception as exc:
            _LOGGER.error("Failed to enable startup item %s: %s", item.name, exc)
            return False

    def _enable_registry_item(self, item: StartupItem, hive: str) -> bool:
        """Enable a registry startup item by adding it back.

        Parameters
        ----------
        item : StartupItem
            Startup item to enable
        hive : str
            Registry hive (HKLM or HKCU)

        Returns
        -------
        bool
            True if successful
        """
        if platform.system() != "Windows":
            _LOGGER.error("Registry operations only supported on Windows")
            return False

        try:
            import winreg

            key_path = STARTUP_REGISTRY_PATHS[hive]
            root_key = winreg.HKEY_LOCAL_MACHINE if hive == "HKLM" else winreg.HKEY_CURRENT_USER

            key = winreg.OpenKey(root_key, key_path, 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, item.name, 0, winreg.REG_SZ, item.command)
            winreg.CloseKey(key)

            _LOGGER.info("Successfully enabled startup item in %s: %s", hive, item.name)
            return True

        except Exception as exc:
            _LOGGER.error("Failed to enable registry startup item: %s", exc)
            return False
    
    def disable_startup_item(self, item: StartupItem) -> bool:
        """Disable a startup item.

        Parameters
        ----------
        item : StartupItem
            Startup item to disable

        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Disabling startup item: %s", item.name)

        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would disable startup item: %s", item.name)
            return True

        try:
            if item.location == StartupLocation.REGISTRY_HKLM_RUN:
                return self._disable_registry_item(item, "HKLM")
            elif item.location == StartupLocation.REGISTRY_HKCU_RUN:
                return self._disable_registry_item(item, "HKCU")
            elif item.location in (StartupLocation.STARTUP_FOLDER_COMMON, StartupLocation.STARTUP_FOLDER_USER):
                _LOGGER.info("Disabling startup folder item by removing file")
                return self.remove_startup_item(item)
            else:
                _LOGGER.warning("Cannot disable items from location: %s", item.location)
                return False
        except Exception as exc:
            _LOGGER.error("Failed to disable startup item %s: %s", item.name, exc)
            return False

    def _disable_registry_item(self, item: StartupItem, hive: str) -> bool:
        """Disable a registry startup item by removing it.

        Parameters
        ----------
        item : StartupItem
            Startup item to disable
        hive : str
            Registry hive (HKLM or HKCU)

        Returns
        -------
        bool
            True if successful
        """
        if platform.system() != "Windows":
            _LOGGER.error("Registry operations only supported on Windows")
            return False

        try:
            import winreg

            key_path = STARTUP_REGISTRY_PATHS[hive]
            root_key = winreg.HKEY_LOCAL_MACHINE if hive == "HKLM" else winreg.HKEY_CURRENT_USER

            key = winreg.OpenKey(root_key, key_path, 0, winreg.KEY_WRITE)
            try:
                winreg.DeleteValue(key, item.name)
                _LOGGER.info("Successfully disabled startup item in %s: %s", hive, item.name)
                return True
            finally:
                winreg.CloseKey(key)

        except FileNotFoundError:
            _LOGGER.warning("Startup item not found in registry: %s", item.name)
            return False
        except Exception as exc:
            _LOGGER.error("Failed to disable registry startup item: %s", exc)
            return False
    
    def remove_startup_item(self, item: StartupItem) -> bool:
        """Permanently remove a startup item.

        Parameters
        ----------
        item : StartupItem
            Startup item to remove

        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Removing startup item: %s", item.name)

        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would remove startup item: %s", item.name)
            return True

        try:
            if item.location in (StartupLocation.REGISTRY_HKLM_RUN, StartupLocation.REGISTRY_HKCU_RUN):
                return self.disable_startup_item(item)
            elif item.location in (StartupLocation.STARTUP_FOLDER_COMMON, StartupLocation.STARTUP_FOLDER_USER):
                return self._remove_startup_folder_item(item)
            else:
                _LOGGER.warning("Cannot remove items from location: %s", item.location)
                return False
        except Exception as exc:
            _LOGGER.error("Failed to remove startup item %s: %s", item.name, exc)
            return False

    def _remove_startup_folder_item(self, item: StartupItem) -> bool:
        """Remove a startup folder item by deleting the file.

        Parameters
        ----------
        item : StartupItem
            Startup item to remove

        Returns
        -------
        bool
            True if successful
        """
        if platform.system() != "Windows":
            _LOGGER.error("Startup folder operations only supported on Windows")
            return False

        try:
            file_path = Path(item.command)
            if file_path.exists():
                file_path.unlink()
                _LOGGER.info("Successfully removed startup folder item: %s", item.name)
                return True
            else:
                _LOGGER.warning("Startup folder item not found: %s", item.command)
                return False
        except Exception as exc:
            _LOGGER.error("Failed to remove startup folder item: %s", exc)
            return False
    
    def get_recommendations(self) -> List[str]:
        """Get startup optimization recommendations.

        Returns
        -------
        List[str]
            List of optimization recommendations
        """
        recommendations = []

        try:
            items = self.list_startup_items()

            if not items:
                recommendations.append("No startup items found to optimize")
                return recommendations

            # Count items by location
            registry_items = [i for i in items if i.location in (
                StartupLocation.REGISTRY_HKLM_RUN,
                StartupLocation.REGISTRY_HKCU_RUN
            )]
            folder_items = [i for i in items if i.location in (
                StartupLocation.STARTUP_FOLDER_COMMON,
                StartupLocation.STARTUP_FOLDER_USER
            )]

            total_items = len(items)

            # Provide recommendations based on number of items
            if total_items > 15:
                recommendations.append(
                    f"You have {total_items} startup items, which may slow down boot time. "
                    "Consider disabling unnecessary items."
                )
            elif total_items > 10:
                recommendations.append(
                    f"You have {total_items} startup items. Review and disable any that aren't essential."
                )
            else:
                recommendations.append(
                    f"You have {total_items} startup items, which is reasonable."
                )

            # Check for duplicate locations
            if registry_items:
                recommendations.append(
                    f"Found {len(registry_items)} registry startup items. "
                    "These start automatically with Windows."
                )

            if folder_items:
                recommendations.append(
                    f"Found {len(folder_items)} startup folder items. "
                    "Consider moving these to registry for better control."
                )

            # Common items that can usually be disabled
            common_safe_to_disable = [
                "OneDrive", "Skype", "Teams", "Spotify", "iTunes",
                "Discord", "Steam", "Epic", "Adobe", "Dropbox"
            ]

            potentially_safe = []
            for item in items:
                for safe_name in common_safe_to_disable:
                    if safe_name.lower() in item.name.lower() or safe_name.lower() in item.command.lower():
                        potentially_safe.append(item.name)
                        break

            if potentially_safe:
                recommendations.append(
                    "The following items can usually be started manually when needed: "
                    + ", ".join(potentially_safe)
                )

            # Check for high impact items
            high_impact = [i for i in items if i.impact == StartupImpact.HIGH]
            if high_impact:
                recommendations.append(
                    f"Found {len(high_impact)} high-impact startup items that may slow boot time"
                )

            return recommendations

        except Exception as exc:
            _LOGGER.error("Failed to generate recommendations: %s", exc)
            return ["Unable to generate recommendations due to an error"]


__all__ = [
    "StartupLocation",
    "StartupImpact",
    "StartupItem",
    "StartupManager",
]
