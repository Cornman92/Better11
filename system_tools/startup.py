"""Startup program management.

This module provides control over programs that run at Windows startup,
including registry entries, startup folders, and scheduled tasks.
"""
from __future__ import annotations

import os
import platform
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional

from . import get_logger
from .base import SystemTool, ToolMetadata
from .safety import ensure_windows

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
        
        # TODO: Add scheduled tasks and services
        
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
    
    def enable_startup_item(self, name: str, command: str, location: StartupLocation) -> bool:
        """Enable a startup item by adding it to the specified location.
        
        Parameters
        ----------
        name : str
            Name of the startup item
        command : str
            Command to execute
        location : StartupLocation
            Where to add the startup item
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Enabling startup item: %s at %s", name, location.value)
        
        if self.dry_run:
            _LOGGER.info("DRY RUN: Would enable %s at %s", name, location.value)
            return True
        
        try:
            if location in [StartupLocation.REGISTRY_HKLM_RUN, StartupLocation.REGISTRY_HKCU_RUN]:
                return self._enable_registry_item(name, command, location)
            elif location in [StartupLocation.STARTUP_FOLDER_COMMON, StartupLocation.STARTUP_FOLDER_USER]:
                _LOGGER.warning("Enabling folder items not yet implemented")
                return False
            else:
                _LOGGER.warning("Enabling %s not yet supported", location.value)
                return False
        
        except Exception as exc:
            _LOGGER.error("Failed to enable startup item %s: %s", name, exc)
            return False
    
    def _enable_registry_item(self, name: str, command: str, location: StartupLocation) -> bool:
        """Enable a registry startup item by creating/updating the value.
        
        Parameters
        ----------
        name : str
            Name of startup item
        command : str
            Command to execute
        location : StartupLocation
            Registry location
        
        Returns
        -------
        bool
            True if successful
        """
        import platform
        if platform.system() != "Windows":
            _LOGGER.warning("Registry operations only on Windows")
            return False
        
        import winreg
        
        # Determine which registry hive
        if location == StartupLocation.REGISTRY_HKLM_RUN:
            hive = winreg.HKEY_LOCAL_MACHINE
            key_path = STARTUP_REGISTRY_PATHS["HKLM"]
        else:
            hive = winreg.HKEY_CURRENT_USER
            key_path = STARTUP_REGISTRY_PATHS["HKCU"]
        
        try:
            # Open/create the key with write access
            key = winreg.CreateKey(hive, key_path)
            
            # Set the value
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, command)
            winreg.CloseKey(key)
            
            _LOGGER.info("Enabled registry startup item: %s", name)
            return True
        
        except PermissionError:
            _LOGGER.error("Permission denied - admin rights may be required")
            return False
        except Exception as exc:
            _LOGGER.error("Failed to set registry value: %s", exc)
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
            _LOGGER.info("DRY RUN: Would disable %s from %s", item.name, item.location.value)
            return True
        
        try:
            if item.location in [StartupLocation.REGISTRY_HKLM_RUN, StartupLocation.REGISTRY_HKCU_RUN]:
                return self._disable_registry_item(item)
            elif item.location in [StartupLocation.STARTUP_FOLDER_COMMON, StartupLocation.STARTUP_FOLDER_USER]:
                return self._disable_folder_item(item)
            else:
                _LOGGER.warning("Disabling %s not yet supported", item.location.value)
                return False
        
        except Exception as exc:
            _LOGGER.error("Failed to disable startup item %s: %s", item.name, exc)
            return False
    
    def _disable_registry_item(self, item: StartupItem) -> bool:
        """Disable a registry startup item by deleting the value.
        
        Parameters
        ----------
        item : StartupItem
            Registry startup item
        
        Returns
        -------
        bool
            True if successful
        """
        import platform
        if platform.system() != "Windows":
            _LOGGER.warning("Registry operations only on Windows")
            return False
        
        import winreg
        
        # Determine which registry hive
        if item.location == StartupLocation.REGISTRY_HKLM_RUN:
            hive = winreg.HKEY_LOCAL_MACHINE
            key_path = STARTUP_REGISTRY_PATHS["HKLM"]
        else:
            hive = winreg.HKEY_CURRENT_USER
            key_path = STARTUP_REGISTRY_PATHS["HKCU"]
        
        try:
            # Open the key with write access
            key = winreg.OpenKey(hive, key_path, 0, winreg.KEY_SET_VALUE)
            
            # Delete the value
            winreg.DeleteValue(key, item.name)
            winreg.CloseKey(key)
            
            _LOGGER.info("Disabled registry startup item: %s", item.name)
            return True
        
        except FileNotFoundError:
            _LOGGER.warning("Registry key or value not found: %s", item.name)
            return False
        except PermissionError:
            _LOGGER.error("Permission denied - admin rights may be required")
            return False
        except Exception as exc:
            _LOGGER.error("Failed to delete registry value: %s", exc)
            return False
    
    def _disable_folder_item(self, item: StartupItem) -> bool:
        """Disable a startup folder item by renaming/moving it.
        
        Parameters
        ----------
        item : StartupItem
            Folder startup item
        
        Returns
        -------
        bool
            True if successful
        """
        try:
            item_path = Path(item.command)
            
            if not item_path.exists():
                _LOGGER.warning("Startup item file not found: %s", item_path)
                return False
            
            # Rename by adding .disabled extension
            disabled_path = item_path.with_suffix(item_path.suffix + '.disabled')
            
            # If already has a .disabled, don't duplicate
            if disabled_path.exists():
                _LOGGER.warning("Item already disabled: %s", item.name)
                return True
            
            item_path.rename(disabled_path)
            _LOGGER.info("Disabled startup folder item: %s -> %s", item.name, disabled_path.name)
            return True
        
        except PermissionError:
            _LOGGER.error("Permission denied to modify startup folder")
            return False
        except Exception as exc:
            _LOGGER.error("Failed to disable folder item: %s", exc)
            return False
    
    def remove_startup_item(self, item: StartupItem) -> bool:
        """Permanently remove a startup item.
        
        This is an alias for disable_startup_item for now, since
        disabling removes from registry or renames in folder.
        
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
        return self.disable_startup_item(item)
    
    def get_recommendations(self) -> List[str]:
        """Get startup optimization recommendations.
        
        Returns
        -------
        List[str]
            List of optimization recommendations
        """
        # TODO: Analyze startup items and provide recommendations
        raise NotImplementedError("Startup recommendations - coming in v0.3.0")


__all__ = [
    "StartupLocation",
    "StartupImpact",
    "StartupItem",
    "StartupManager",
]
