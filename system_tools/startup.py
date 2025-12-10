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
        """
        if self.dry_run:
            _LOGGER.info("DRY RUN: Would enable %s", item.name)
            return True
        
        _LOGGER.info("Enabling startup item: %s", item.name)
        
        # TODO: Implement enable logic based on location
        # For registry: restore the value
        # For folder: restore the file
        
        raise NotImplementedError("Enable functionality not yet implemented")
    
    def disable_startup_item(self, item: StartupItem) -> bool:
        """Disable a startup item without removing it.
        
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
        """
        if self.dry_run:
            _LOGGER.info("DRY RUN: Would disable %s", item.name)
            return True
        
        _LOGGER.info("Disabling startup item: %s", item.name)
        
        # TODO: Implement disable logic based on location
        # For registry: rename value or delete it
        # For folder: rename file or move it
        
        raise NotImplementedError("Disable functionality not yet implemented")
    
    def remove_startup_item(self, item: StartupItem) -> bool:
        """Permanently remove a startup item.
        
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
        """
        if self.dry_run:
            _LOGGER.info("DRY RUN: Would remove %s", item.name)
            return True
        
        _LOGGER.info("Removing startup item: %s", item.name)
        
        # TODO: Implement remove logic based on location
        
        raise NotImplementedError("Remove functionality not yet implemented")
    
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
