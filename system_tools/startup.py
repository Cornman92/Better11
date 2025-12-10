"""Windows startup program management.

This module provides functionality to list, enable, disable, and remove
startup programs from various locations in Windows.
"""
from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional

from . import get_logger
from .base import SystemTool, ToolMetadata
from .safety import SafetyError

_LOGGER = get_logger(__name__)

# Platform-specific imports
try:
    import winreg
    WINREG_AVAILABLE = True
except ImportError:
    WINREG_AVAILABLE = False
    _LOGGER.warning("winreg not available - startup management will be limited")


class StartupLocation(Enum):
    """Location where startup item is registered."""
    REGISTRY_HKLM_RUN = "hklm_run"
    REGISTRY_HKCU_RUN = "hkcu_run"
    REGISTRY_HKLM_RUN_ONCE = "hklm_run_once"
    REGISTRY_HKCU_RUN_ONCE = "hkcu_run_once"
    STARTUP_FOLDER_COMMON = "startup_common"
    STARTUP_FOLDER_USER = "startup_user"
    TASK_SCHEDULER = "task_scheduler"
    SERVICES = "services"


class StartupImpact(Enum):
    """Estimated impact on boot time."""
    HIGH = "high"      # >3s delay
    MEDIUM = "medium"  # 1-3s delay
    LOW = "low"        # <1s delay
    UNKNOWN = "unknown"


@dataclass
class StartupItem:
    """Represents a startup program.
    
    Attributes
    ----------
    name : str
        Display name of the startup item
    command : str
        Command or path that executes on startup
    location : StartupLocation
        Where the startup item is registered
    enabled : bool
        Whether the item is currently enabled
    impact : StartupImpact
        Estimated boot time impact
    publisher : str, optional
        Software publisher/vendor
    """
    name: str
    command: str
    location: StartupLocation
    enabled: bool
    impact: StartupImpact = StartupImpact.UNKNOWN
    publisher: Optional[str] = None
    
    def __str__(self) -> str:
        status = "✓" if self.enabled else "✗"
        return f"{status} {self.name} [{self.location.value}]"


class StartupManager(SystemTool):
    """Manage Windows startup programs.
    
    This tool provides comprehensive management of Windows startup programs,
    including listing, enabling, disabling, and removing items from various
    startup locations.
    
    Parameters
    ----------
    config : dict, optional
        Configuration dictionary
    dry_run : bool
        If True, simulate operations without making changes
    
    Examples
    --------
    List all startup items:
    
    >>> manager = StartupManager()
    >>> items = manager.list_startup_items()
    >>> for item in items:
    ...     print(f"{item.name}: {item.location.value}")
    
    Disable a startup item:
    
    >>> item = items[0]
    >>> manager.disable_startup_item(item)
    """
    
    # Registry keys to check
    REGISTRY_KEYS = [
        ("HKLM", r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
         StartupLocation.REGISTRY_HKLM_RUN),
        ("HKCU", r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
         StartupLocation.REGISTRY_HKCU_RUN),
        ("HKLM", r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce",
         StartupLocation.REGISTRY_HKLM_RUN_ONCE),
        ("HKCU", r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce",
         StartupLocation.REGISTRY_HKCU_RUN_ONCE),
    ]
    
    def get_metadata(self) -> ToolMetadata:
        """Return tool metadata."""
        return ToolMetadata(
            name="Startup Manager",
            description="Manage Windows startup programs",
            version="0.3.0",
            requires_admin=False,  # Reading doesn't need admin
            requires_restart=False,
            category="performance"
        )
    
    def validate_environment(self) -> None:
        """Validate environment prerequisites."""
        if not WINREG_AVAILABLE and os.name != 'posix':
            # On Windows, winreg should be available
            if os.name == 'nt':
                raise SafetyError("winreg module not available on Windows")
        
        # On non-Windows, we allow it for testing but log warning
        if os.name != 'nt':
            _LOGGER.debug("Running on non-Windows system - some features may not work")
    
    def execute(self, *args, **kwargs) -> bool:
        """Execute startup management.
        
        This is called by the base class run() method.
        For now, just lists items as a validation.
        """
        items = self.list_startup_items()
        _LOGGER.info("Found %d startup items", len(items))
        return True
    
    def list_startup_items(self) -> List[StartupItem]:
        """List all startup programs from all locations.
        
        Returns
        -------
        List[StartupItem]
            All discovered startup items
        
        Examples
        --------
        >>> manager = StartupManager()
        >>> items = manager.list_startup_items()
        >>> print(f"Found {len(items)} startup items")
        """
        items = []
        
        if WINREG_AVAILABLE:
            items.extend(self._get_registry_items())
        else:
            _LOGGER.debug("Skipping registry items (winreg not available)")
        
        items.extend(self._get_startup_folder_items())
        
        # TODO: Add scheduled tasks
        # TODO: Add services
        
        _LOGGER.info("Listed %d startup items", len(items))
        return items
    
    def _get_registry_items(self) -> List[StartupItem]:
        """Get startup items from registry.
        
        Returns
        -------
        List[StartupItem]
            Startup items found in registry keys
        """
        if not WINREG_AVAILABLE:
            return []
        
        items = []
        
        for hive_name, subkey, location in self.REGISTRY_KEYS:
            # Get the hive constant
            hive = getattr(winreg, f'HKEY_{hive_name.replace("HK", "")}')
            
            try:
                with winreg.OpenKey(hive, subkey) as key:
                    i = 0
                    while True:
                        try:
                            name, command, _ = winreg.EnumValue(key, i)
                            items.append(StartupItem(
                                name=name,
                                command=command,
                                location=location,
                                enabled=True  # In registry = enabled
                            ))
                            i += 1
                        except OSError:
                            # No more values
                            break
            except FileNotFoundError:
                _LOGGER.debug("Registry key not found: %s\\%s", hive_name, subkey)
            except Exception as exc:
                _LOGGER.warning("Failed to read registry %s\\%s: %s", 
                              hive_name, subkey, exc)
        
        _LOGGER.debug("Found %d registry startup items", len(items))
        return items
    
    def _get_startup_folder_items(self) -> List[StartupItem]:
        """Get startup items from startup folders.
        
        Returns
        -------
        List[StartupItem]
            Startup items found in startup folders
        """
        items = []
        
        # User startup folder
        appdata = os.environ.get('APPDATA', '')
        if appdata:
            user_startup = Path(appdata) / \
                'Microsoft/Windows/Start Menu/Programs/Startup'
        else:
            user_startup = Path.home() / \
                'AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup'
        
        # Common startup folder
        programdata = os.environ.get('PROGRAMDATA', '')
        if programdata:
            common_startup = Path(programdata) / \
                'Microsoft/Windows/Start Menu/Programs/Startup'
        else:
            common_startup = Path('C:/ProgramData/Microsoft/Windows/Start Menu/Programs/Startup')
        
        for folder, location in [
            (user_startup, StartupLocation.STARTUP_FOLDER_USER),
            (common_startup, StartupLocation.STARTUP_FOLDER_COMMON)
        ]:
            if folder.exists():
                for item in folder.iterdir():
                    if item.is_file() and item.suffix.lower() in {'.lnk', '.exe', '.bat', '.cmd'}:
                        items.append(StartupItem(
                            name=item.stem,
                            command=str(item),
                            location=location,
                            enabled=True
                        ))
            else:
                _LOGGER.debug("Startup folder not found: %s", folder)
        
        _LOGGER.debug("Found %d startup folder items", len(items))
        return items
    
    def enable_startup_item(self, item: StartupItem) -> bool:
        """Enable a disabled startup item.
        
        Parameters
        ----------
        item : StartupItem
            The startup item to enable
        
        Returns
        -------
        bool
            True if successful
        
        Raises
        ------
        SafetyError
            If operation fails
        
        Examples
        --------
        >>> manager = StartupManager()
        >>> items = manager.list_startup_items()
        >>> disabled_item = next((i for i in items if not i.enabled), None)
        >>> if disabled_item:
        ...     manager.enable_startup_item(disabled_item)
        """
        if self.dry_run:
            _LOGGER.info("DRY RUN: Would enable %s", item.name)
            return True
        
        if item.enabled:
            _LOGGER.warning("Item %s is already enabled", item.name)
            return True
        
        _LOGGER.info("Enabling startup item: %s", item.name)
        
        try:
            if item.location in [StartupLocation.REGISTRY_HKLM_RUN, 
                                StartupLocation.REGISTRY_HKCU_RUN,
                                StartupLocation.REGISTRY_HKLM_RUN_ONCE,
                                StartupLocation.REGISTRY_HKCU_RUN_ONCE]:
                return self._enable_registry_item(item)
            
            elif item.location in [StartupLocation.STARTUP_FOLDER_USER,
                                  StartupLocation.STARTUP_FOLDER_COMMON]:
                return self._enable_folder_item(item)
            
            else:
                raise NotImplementedError(
                    f"Enable not yet implemented for {item.location.value}")
        
        except Exception as exc:
            _LOGGER.error("Failed to enable %s: %s", item.name, exc)
            raise SafetyError(f"Failed to enable startup item: {exc}") from exc
    
    def _enable_registry_item(self, item: StartupItem) -> bool:
        """Enable a registry startup item."""
        if not WINREG_AVAILABLE:
            raise SafetyError("Registry operations require Windows")
        
        # Parse the location to get hive and key
        location_map = {
            StartupLocation.REGISTRY_HKLM_RUN: (
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            ),
            StartupLocation.REGISTRY_HKCU_RUN: (
                winreg.HKEY_CURRENT_USER,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            ),
            StartupLocation.REGISTRY_HKLM_RUN_ONCE: (
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce"
            ),
            StartupLocation.REGISTRY_HKCU_RUN_ONCE: (
                winreg.HKEY_CURRENT_USER,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce"
            ),
        }
        
        hive, subkey = location_map[item.location]
        
        try:
            # Try to restore from backup first (not implemented yet)
            # For now, assume item was disabled by being removed
            # User would need to manually add it back
            _LOGGER.warning(
                "Registry item restoration not fully implemented. "
                "Item must be manually added back to registry."
            )
            return False
        except Exception as exc:
            _LOGGER.error("Failed to enable registry item: %s", exc)
            raise
    
    def _enable_folder_item(self, item: StartupItem) -> bool:
        """Enable a startup folder item."""
        # If disabled, the file might have been renamed or moved
        # For now, log that manual intervention is needed
        _LOGGER.warning(
            "Folder item restoration not fully implemented. "
            "File may need to be manually restored."
        )
        return False
    
    def disable_startup_item(self, item: StartupItem) -> bool:
        """Disable a startup item without removing it.
        
        This will remove the startup entry but keep a backup for restoration.
        
        Parameters
        ----------
        item : StartupItem
            The startup item to disable
        
        Returns
        -------
        bool
            True if successful
        
        Raises
        ------
        SafetyError
            If operation fails
        
        Examples
        --------
        >>> manager = StartupManager()
        >>> items = manager.list_startup_items()
        >>> item = items[0]
        >>> manager.disable_startup_item(item)
        """
        if self.dry_run:
            _LOGGER.info("DRY RUN: Would disable %s", item.name)
            return True
        
        if not item.enabled:
            _LOGGER.warning("Item %s is already disabled", item.name)
            return True
        
        _LOGGER.info("Disabling startup item: %s", item.name)
        
        try:
            if item.location in [StartupLocation.REGISTRY_HKLM_RUN, 
                                StartupLocation.REGISTRY_HKCU_RUN,
                                StartupLocation.REGISTRY_HKLM_RUN_ONCE,
                                StartupLocation.REGISTRY_HKCU_RUN_ONCE]:
                return self._disable_registry_item(item)
            
            elif item.location in [StartupLocation.STARTUP_FOLDER_USER,
                                  StartupLocation.STARTUP_FOLDER_COMMON]:
                return self._disable_folder_item(item)
            
            else:
                raise NotImplementedError(
                    f"Disable not yet implemented for {item.location.value}")
        
        except Exception as exc:
            _LOGGER.error("Failed to disable %s: %s", item.name, exc)
            raise SafetyError(f"Failed to disable startup item: {exc}") from exc
    
    def _disable_registry_item(self, item: StartupItem) -> bool:
        """Disable a registry startup item by removing the value."""
        if not WINREG_AVAILABLE:
            raise SafetyError("Registry operations require Windows")
        
        # Parse the location to get hive and key
        location_map = {
            StartupLocation.REGISTRY_HKLM_RUN: (
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            ),
            StartupLocation.REGISTRY_HKCU_RUN: (
                winreg.HKEY_CURRENT_USER,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            ),
            StartupLocation.REGISTRY_HKLM_RUN_ONCE: (
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce"
            ),
            StartupLocation.REGISTRY_HKCU_RUN_ONCE: (
                winreg.HKEY_CURRENT_USER,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce"
            ),
        }
        
        hive, subkey = location_map[item.location]
        
        try:
            # Backup the value first (to a backup key)
            backup_key_path = subkey.replace("\\CurrentVersion\\", "\\CurrentVersion\\Better11Backup\\")
            
            # Create backup
            try:
                with winreg.CreateKeyEx(hive, backup_key_path) as backup_key:
                    winreg.SetValueEx(backup_key, item.name, 0, winreg.REG_SZ, item.command)
                    _LOGGER.info("Backed up %s to %s", item.name, backup_key_path)
            except Exception as backup_exc:
                _LOGGER.warning("Failed to create backup: %s", backup_exc)
            
            # Delete the value from the startup key
            with winreg.OpenKey(hive, subkey, 0, winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, item.name)
                _LOGGER.info("Deleted registry value: %s", item.name)
            
            return True
            
        except FileNotFoundError:
            _LOGGER.warning("Registry value not found: %s", item.name)
            return True  # Already disabled
        except Exception as exc:
            _LOGGER.error("Failed to disable registry item: %s", exc)
            raise
    
    def _disable_folder_item(self, item: StartupItem) -> bool:
        """Disable a startup folder item by renaming it."""
        file_path = Path(item.command)
        
        if not file_path.exists():
            _LOGGER.warning("Startup file not found: %s", file_path)
            return True  # Already disabled
        
        # Rename the file to disable it (add .disabled extension)
        disabled_path = file_path.with_suffix(file_path.suffix + '.disabled')
        
        try:
            file_path.rename(disabled_path)
            _LOGGER.info("Renamed %s to %s", file_path, disabled_path)
            return True
        except Exception as exc:
            _LOGGER.error("Failed to rename file: %s", exc)
            raise
    
    def remove_startup_item(self, item: StartupItem) -> bool:
        """Permanently remove a startup item.
        
        This will delete the startup entry without creating a backup.
        Use disable_startup_item() if you want to be able to restore it.
        
        Parameters
        ----------
        item : StartupItem
            The startup item to remove
        
        Returns
        -------
        bool
            True if successful
        
        Raises
        ------
        SafetyError
            If operation fails
        
        Examples
        --------
        >>> manager = StartupManager()
        >>> items = manager.list_startup_items()
        >>> item = items[0]
        >>> manager.remove_startup_item(item)  # Permanently removes
        """
        if self.dry_run:
            _LOGGER.info("DRY RUN: Would remove %s", item.name)
            return True
        
        _LOGGER.info("Removing startup item: %s", item.name)
        
        try:
            if item.location in [StartupLocation.REGISTRY_HKLM_RUN, 
                                StartupLocation.REGISTRY_HKCU_RUN,
                                StartupLocation.REGISTRY_HKLM_RUN_ONCE,
                                StartupLocation.REGISTRY_HKCU_RUN_ONCE]:
                return self._remove_registry_item(item)
            
            elif item.location in [StartupLocation.STARTUP_FOLDER_USER,
                                  StartupLocation.STARTUP_FOLDER_COMMON]:
                return self._remove_folder_item(item)
            
            else:
                raise NotImplementedError(
                    f"Remove not yet implemented for {item.location.value}")
        
        except Exception as exc:
            _LOGGER.error("Failed to remove %s: %s", item.name, exc)
            raise SafetyError(f"Failed to remove startup item: {exc}") from exc
    
    def _remove_registry_item(self, item: StartupItem) -> bool:
        """Permanently remove a registry startup item."""
        if not WINREG_AVAILABLE:
            raise SafetyError("Registry operations require Windows")
        
        # Parse the location to get hive and key
        location_map = {
            StartupLocation.REGISTRY_HKLM_RUN: (
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            ),
            StartupLocation.REGISTRY_HKCU_RUN: (
                winreg.HKEY_CURRENT_USER,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
            ),
            StartupLocation.REGISTRY_HKLM_RUN_ONCE: (
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce"
            ),
            StartupLocation.REGISTRY_HKCU_RUN_ONCE: (
                winreg.HKEY_CURRENT_USER,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce"
            ),
        }
        
        hive, subkey = location_map[item.location]
        
        try:
            # Delete the value from the startup key
            with winreg.OpenKey(hive, subkey, 0, winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, item.name)
                _LOGGER.info("Permanently deleted registry value: %s", item.name)
            
            return True
            
        except FileNotFoundError:
            _LOGGER.warning("Registry value not found: %s", item.name)
            return True  # Already removed
        except Exception as exc:
            _LOGGER.error("Failed to remove registry item: %s", exc)
            raise
    
    def _remove_folder_item(self, item: StartupItem) -> bool:
        """Permanently remove a startup folder item."""
        file_path = Path(item.command)
        
        if not file_path.exists():
            _LOGGER.warning("Startup file not found: %s", file_path)
            return True  # Already removed
        
        try:
            file_path.unlink()
            _LOGGER.info("Permanently deleted file: %s", file_path)
            return True
        except Exception as exc:
            _LOGGER.error("Failed to delete file: %s", exc)
            raise
    
    def get_boot_time_estimate(self) -> float:
        """Estimate total boot time impact from startup items.
        
        Returns
        -------
        float
            Estimated boot time in seconds
        """
        items = self.list_startup_items()
        
        # Simple heuristic estimation
        total_time = 0.0
        for item in items:
            if item.enabled:
                if item.impact == StartupImpact.HIGH:
                    total_time += 3.5
                elif item.impact == StartupImpact.MEDIUM:
                    total_time += 2.0
                elif item.impact == StartupImpact.LOW:
                    total_time += 0.5
                else:
                    total_time += 1.0  # Unknown impact
        
        return total_time
    
    def get_recommendations(self) -> List[str]:
        """Get startup optimization recommendations.
        
        Returns
        -------
        List[str]
            List of optimization recommendations
        """
        items = self.list_startup_items()
        recommendations = []
        
        enabled_count = sum(1 for item in items if item.enabled)
        
        if enabled_count > 15:
            recommendations.append(
                f"You have {enabled_count} startup items. "
                "Consider disabling unnecessary items to improve boot time."
            )
        
        high_impact = [item for item in items 
                      if item.enabled and item.impact == StartupImpact.HIGH]
        if high_impact:
            recommendations.append(
                f"Found {len(high_impact)} high-impact startup items. "
                "Review these first for optimization."
            )
        
        return recommendations


def list_startup_items() -> List[StartupItem]:
    """Convenience function to list startup items.
    
    Returns
    -------
    List[StartupItem]
        All discovered startup items
    
    Examples
    --------
    >>> items = list_startup_items()
    >>> for item in items:
    ...     print(item.name)
    """
    manager = StartupManager()
    return manager.list_startup_items()


__all__ = [
    "StartupLocation",
    "StartupImpact",
    "StartupItem",
    "StartupManager",
    "list_startup_items",
]
