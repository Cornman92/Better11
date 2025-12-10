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
        ensure_windows()
        _LOGGER.info("Enabling startup item: %s", item.name)
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would enable startup item: %s", item.name)
            return True
        
        try:
            if item.location in (StartupLocation.REGISTRY_HKLM_RUN, StartupLocation.REGISTRY_HKCU_RUN):
                # Re-add to registry
                import winreg
                
                hive = winreg.HKEY_LOCAL_MACHINE if item.location == StartupLocation.REGISTRY_HKLM_RUN else winreg.HKEY_CURRENT_USER
                key_path = STARTUP_REGISTRY_PATHS["HKLM" if item.location == StartupLocation.REGISTRY_HKLM_RUN else "HKCU"]
                
                try:
                    key = winreg.OpenKey(hive, key_path, 0, winreg.KEY_WRITE)
                except FileNotFoundError:
                    key = winreg.CreateKey(hive, key_path)
                
                winreg.SetValueEx(key, item.name, 0, winreg.REG_SZ, item.command)
                winreg.CloseKey(key)
                
                _LOGGER.info("Successfully enabled startup item in registry: %s", item.name)
                return True
                
            elif item.location in (StartupLocation.STARTUP_FOLDER_COMMON, StartupLocation.STARTUP_FOLDER_USER):
                # Re-create shortcut in startup folder
                import shutil
                
                if item.location == StartupLocation.STARTUP_FOLDER_COMMON:
                    programdata = os.environ.get('PROGRAMDATA', 'C:\\ProgramData')
                    startup_folder = Path(programdata) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup'
                else:
                    appdata = os.environ.get('APPDATA', '')
                    startup_folder = Path(appdata) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup'
                
                startup_folder.mkdir(parents=True, exist_ok=True)
                
                # Create shortcut (simplified - in production, use win32com for proper shortcuts)
                shortcut_path = startup_folder / f"{item.name}.lnk"
                # For now, create a batch file that runs the command
                batch_path = startup_folder / f"{item.name}.bat"
                with open(batch_path, 'w') as f:
                    f.write(f'@echo off\n"{item.command}"\n')
                
                _LOGGER.info("Successfully enabled startup item in folder: %s", item.name)
                return True
            else:
                _LOGGER.warning("Cannot enable startup item from location: %s", item.location)
                return False
                
        except PermissionError:
            _LOGGER.error("Administrator privileges required to enable startup item")
            return False
        except Exception as e:
            _LOGGER.error("Error enabling startup item: %s", e)
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
        ensure_windows()
        _LOGGER.info("Disabling startup item: %s", item.name)
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would disable startup item: %s", item.name)
            return True
        
        try:
            if item.location in (StartupLocation.REGISTRY_HKLM_RUN, StartupLocation.REGISTRY_HKCU_RUN):
                # Remove from registry
                import winreg
                
                hive = winreg.HKEY_LOCAL_MACHINE if item.location == StartupLocation.REGISTRY_HKLM_RUN else winreg.HKEY_CURRENT_USER
                key_path = STARTUP_REGISTRY_PATHS["HKLM" if item.location == StartupLocation.REGISTRY_HKLM_RUN else "HKCU"]
                
                try:
                    key = winreg.OpenKey(hive, key_path, 0, winreg.KEY_WRITE)
                    winreg.DeleteValue(key, item.name)
                    winreg.CloseKey(key)
                    _LOGGER.info("Successfully disabled startup item in registry: %s", item.name)
                    return True
                except FileNotFoundError:
                    _LOGGER.warning("Startup item not found in registry: %s", item.name)
                    return False
                
            elif item.location in (StartupLocation.STARTUP_FOLDER_COMMON, StartupLocation.STARTUP_FOLDER_USER):
                # Remove from startup folder
                if item.location == StartupLocation.STARTUP_FOLDER_COMMON:
                    programdata = os.environ.get('PROGRAMDATA', 'C:\\ProgramData')
                    startup_folder = Path(programdata) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup'
                else:
                    appdata = os.environ.get('APPDATA', '')
                    startup_folder = Path(appdata) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup'
                
                # Try to find and remove the file
                for ext in ['.lnk', '.bat', '.exe', '.vbs']:
                    file_path = startup_folder / f"{item.name}{ext}"
                    if file_path.exists():
                        file_path.unlink()
                        _LOGGER.info("Successfully disabled startup item in folder: %s", item.name)
                        return True
                
                _LOGGER.warning("Startup item file not found: %s", item.name)
                return False
            else:
                _LOGGER.warning("Cannot disable startup item from location: %s", item.location)
                return False
                
        except PermissionError:
            _LOGGER.error("Administrator privileges required to disable startup item")
            return False
        except Exception as e:
            _LOGGER.error("Error disabling startup item: %s", e)
            return False
    
    def remove_startup_item(self, item: StartupItem) -> bool:
        """Permanently remove a startup item.
        
        This is the same as disable for most cases, but provides
        a clear semantic distinction.
        
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
        # For now, removal is the same as disable
        # In the future, could add additional cleanup
        return self.disable_startup_item(item)
    
    def get_recommendations(self) -> List[str]:
        """Get startup optimization recommendations.
        
        Returns
        -------
        List[str]
            List of optimization recommendations
        """
        _LOGGER.info("Generating startup optimization recommendations")
        
        items = self.list_startup_items()
        recommendations: List[str] = []
        
        if not items:
            recommendations.append("No startup items found. System should boot quickly.")
            return recommendations
        
        # Count items by location
        registry_items = [i for i in items if i.location.value.startswith("registry")]
        folder_items = [i for i in items if i.location.value.startswith("startup")]
        
        if len(items) > 10:
            recommendations.append(
                f"Found {len(items)} startup items. Consider disabling non-essential items "
                "to improve boot time."
            )
        
        if len(registry_items) > 5:
            recommendations.append(
                f"Found {len(registry_items)} registry-based startup items. "
                "Registry items start earlier and may slow boot time."
            )
        
        # Check for common unnecessary items
        unnecessary_patterns = [
            "update", "updater", "helper", "launcher", "tray",
            "quicktime", "adobe", "skype", "spotify"
        ]
        
        unnecessary = [
            item for item in items
            if any(pattern in item.name.lower() for pattern in unnecessary_patterns)
        ]
        
        if unnecessary:
            recommendations.append(
                f"Found {len(unnecessary)} potentially unnecessary startup items: "
                f"{', '.join([i.name for i in unnecessary[:5]])}. "
                "Consider disabling if not needed."
            )
        
        # Check for high-impact items
        high_impact = [i for i in items if i.impact == StartupImpact.HIGH]
        if high_impact:
            recommendations.append(
                f"Found {len(high_impact)} high-impact startup items that may significantly "
                "slow boot time. Review and disable if not essential."
            )
        
        if not recommendations:
            recommendations.append("Startup configuration looks reasonable.")
        
        return recommendations


__all__ = [
    "StartupLocation",
    "StartupImpact",
    "StartupItem",
    "StartupManager",
]
