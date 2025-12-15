"""Windows startup program management.

This module provides functionality to list, enable, disable, and remove
startup programs from various locations in Windows.
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
    
    def _get_scheduled_tasks(self) -> List[StartupItem]:
        """Get startup items from Task Scheduler.
        
        Returns
        -------
        List[StartupItem]
            Startup tasks that run at logon or startup
        """
        items = []
        
        if os.name != 'nt':
            _LOGGER.debug("Skipping scheduled tasks (not on Windows)")
            return items
        
        try:
            # Use schtasks.exe to query tasks
            # /query: Query tasks
            # /fo CSV: Output in CSV format
            # /v: Verbose (includes status)
            result = subprocess.run(
                ['schtasks', '/query', '/fo', 'CSV', '/v'],
                capture_output=True,
                text=True,
                check=True,
                timeout=10
            )
            
            # Parse CSV output
            lines = result.stdout.strip().split('\n')
            if len(lines) < 2:
                return items
            
            # Skip header line
            for line in lines[1:]:
                # Split CSV (basic parsing)
                parts = line.split('","')
                if len(parts) < 10:
                    continue
                
                # Clean up quotes
                parts = [p.strip('"') for p in parts]
                
                task_name = parts[0] if len(parts) > 0 else ""
                status = parts[3] if len(parts) > 3 else ""
                triggers = parts[9] if len(parts) > 9 else ""
                
                # Filter for startup/logon tasks
                if not any(trigger in triggers.lower() for trigger in ['logon', 'startup', 'boot']):
                    continue
                
                # Skip disabled tasks unless we want to show them
                enabled = status.lower() == 'ready' or status.lower() == 'running'
                
                # Create startup item
                item = StartupItem(
                    name=task_name,
                    command=f"Task: {task_name}",
                    location=StartupLocation.TASK_SCHEDULER,
                    enabled=enabled,
                    impact=StartupImpact.MEDIUM,  # Tasks typically have medium impact
                    publisher=None
                )
                
                items.append(item)
                
        except subprocess.TimeoutExpired:
            _LOGGER.warning("Timeout querying scheduled tasks")
        except subprocess.CalledProcessError as exc:
            _LOGGER.warning("Failed to query scheduled tasks: %s", exc)
        except Exception as exc:
            _LOGGER.warning("Error parsing scheduled tasks: %s", exc)
        
        _LOGGER.info("Found %d scheduled startup tasks", len(items))
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
    "list_startup_items",
]
