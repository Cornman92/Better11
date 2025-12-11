"""Privacy and telemetry control for Windows.

This module provides comprehensive control over Windows privacy settings,
telemetry collection, and app permissions.
"""
from __future__ import annotations

import platform
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional

from . import get_logger
from .base import SystemTool, ToolMetadata

# Import winreg for Windows, use compatibility module for non-Windows
try:
    import winreg
except ImportError:
    from . import winreg_compat as winreg

_LOGGER = get_logger(__name__)


class TelemetryLevel(Enum):
    """Windows telemetry level."""
    
    SECURITY = 0  # Enterprise only
    BASIC = 1
    ENHANCED = 2
    FULL = 3


class PrivacySetting(Enum):
    """Privacy settings that can be controlled."""
    
    LOCATION = "location"
    CAMERA = "camera"
    MICROPHONE = "microphone"
    NOTIFICATIONS = "notifications"
    ACCOUNT_INFO = "account_info"
    CONTACTS = "contacts"
    CALENDAR = "calendar"
    PHONE_CALLS = "phone_calls"
    CALL_HISTORY = "call_history"
    EMAIL = "email"
    TASKS = "tasks"
    MESSAGING = "messaging"
    RADIOS = "radios"
    OTHER_DEVICES = "other_devices"
    BACKGROUND_APPS = "background_apps"
    APP_DIAGNOSTICS = "app_diagnostics"
    DOCUMENTS = "documents"
    PICTURES = "pictures"
    VIDEOS = "videos"
    FILE_SYSTEM = "file_system"


@dataclass
class PrivacyPreset:
    """Predefined privacy configuration preset."""
    
    name: str
    description: str
    telemetry_level: TelemetryLevel
    settings: Dict[PrivacySetting, bool]
    disable_advertising_id: bool = True
    disable_cortana: bool = False


class PrivacyManager(SystemTool):
    """Manage Windows privacy and telemetry settings.
    
    This class provides methods to control Windows telemetry, manage app
    permissions, and apply privacy presets.
    
    Parameters
    ----------
    config : dict, optional
        Configuration dictionary
    dry_run : bool
        If True, simulate operations without making changes
    """
    
    # Predefined presets
    MAXIMUM_PRIVACY = PrivacyPreset(
        name="Maximum Privacy",
        description="Disable all telemetry and most app permissions",
        telemetry_level=TelemetryLevel.BASIC,
        settings={s: False for s in PrivacySetting},
        disable_advertising_id=True,
        disable_cortana=True
    )
    
    BALANCED = PrivacyPreset(
        name="Balanced",
        description="Reasonable privacy with essential features enabled",
        telemetry_level=TelemetryLevel.BASIC,
        settings={
            PrivacySetting.LOCATION: True,
            PrivacySetting.NOTIFICATIONS: True,
            PrivacySetting.BACKGROUND_APPS: True,
            # Other settings default to False
        }
    )
    
    def __init__(self, config: Optional[dict] = None, dry_run: bool = False):
        super().__init__(config, dry_run)
    
    def get_metadata(self) -> ToolMetadata:
        """Return tool metadata."""
        return ToolMetadata(
            name="Privacy Manager",
            description="Manage Windows privacy and telemetry settings",
            version="0.3.0",
            requires_admin=True,
            requires_restart=False,
            category="privacy"
        )
    
    def validate_environment(self) -> None:
        """Validate registry access for privacy settings."""
        pass
    
    def execute(self) -> bool:
        """Execute default privacy check operation."""
        level = self.get_telemetry_level()
        _LOGGER.info("Current telemetry level: %s", level)
        return True
    
    def set_telemetry_level(self, level: TelemetryLevel) -> bool:
        """Set Windows telemetry level.

        Parameters
        ----------
        level : TelemetryLevel
            Desired telemetry level

        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Setting telemetry level to %s", level.name)

        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would set telemetry level to %s", level.name)
            return True

        try:
            if platform.system() != "Windows":
                _LOGGER.error("Telemetry control only supported on Windows")
                return False

            # Set telemetry level in group policy registry
            key_path = r"SOFTWARE\Policies\Microsoft\Windows\DataCollection"

            try:
                key = winreg.CreateKeyEx(
                    winreg.HKEY_LOCAL_MACHINE,
                    key_path,
                    0,
                    winreg.KEY_WRITE
                )

                # AllowTelemetry value:
                # 0 = Security (Enterprise only)
                # 1 = Basic
                # 2 = Enhanced
                # 3 = Full
                winreg.SetValueEx(key, "AllowTelemetry", 0, winreg.REG_DWORD, level.value)
                winreg.CloseKey(key)

                _LOGGER.info("Successfully set telemetry level to %s", level.name)
                return True

            except PermissionError:
                _LOGGER.error("Insufficient permissions to set telemetry level. Run as administrator.")
                return False

        except Exception as exc:
            _LOGGER.error("Failed to set telemetry level: %s", exc)
            return False
    
    def get_telemetry_level(self) -> TelemetryLevel:
        """Get current Windows telemetry level.

        Returns
        -------
        TelemetryLevel
            Current telemetry level
        """
        try:
            if platform.system() != "Windows":
                _LOGGER.warning("Telemetry control only supported on Windows")
                return TelemetryLevel.FULL  # Default assumption on non-Windows

            key_path = r"SOFTWARE\Policies\Microsoft\Windows\DataCollection"

            try:
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    key_path,
                    0,
                    winreg.KEY_READ
                )

                value, _ = winreg.QueryValueEx(key, "AllowTelemetry")
                winreg.CloseKey(key)

                # Map registry value to enum
                level_map = {
                    0: TelemetryLevel.SECURITY,
                    1: TelemetryLevel.BASIC,
                    2: TelemetryLevel.ENHANCED,
                    3: TelemetryLevel.FULL,
                }

                return level_map.get(value, TelemetryLevel.FULL)

            except FileNotFoundError:
                # Key doesn't exist, telemetry likely at default (Full)
                _LOGGER.debug("Telemetry registry key not found, assuming FULL")
                return TelemetryLevel.FULL

        except Exception as exc:
            _LOGGER.error("Failed to get telemetry level: %s", exc)
            return TelemetryLevel.FULL  # Default assumption
    
    def set_app_permission(self, setting: PrivacySetting, enabled: bool) -> bool:
        """Set an app permission.
        
        Parameters
        ----------
        setting : PrivacySetting
            Permission to configure
        enabled : bool
            Whether to enable or disable the permission
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Setting %s permission to %s", setting.value, enabled)
        # TODO: Set registry keys for app permissions
        raise NotImplementedError("App permissions - coming in v0.3.0")
    
    def get_app_permission(self, setting: PrivacySetting) -> bool:
        """Get current state of an app permission.
        
        Parameters
        ----------
        setting : PrivacySetting
            Permission to check
        
        Returns
        -------
        bool
            True if permission is enabled
        """
        # TODO: Read from registry
        raise NotImplementedError("Get app permission - coming in v0.3.0")
    
    def disable_advertising_id(self) -> bool:
        """Disable Windows advertising ID.

        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Disabling advertising ID")

        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would disable advertising ID")
            return True

        try:
            if platform.system() != "Windows":
                _LOGGER.error("Advertising ID control only supported on Windows")
                return False

            # Disable advertising ID in HKCU
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo"

            try:
                key = winreg.CreateKeyEx(
                    winreg.HKEY_CURRENT_USER,
                    key_path,
                    0,
                    winreg.KEY_WRITE
                )

                # Set Enabled to 0 to disable
                winreg.SetValueEx(key, "Enabled", 0, winreg.REG_DWORD, 0)
                winreg.CloseKey(key)

                _LOGGER.info("Successfully disabled advertising ID")
                return True

            except PermissionError:
                _LOGGER.error("Insufficient permissions to disable advertising ID")
                return False

        except Exception as exc:
            _LOGGER.error("Failed to disable advertising ID: %s", exc)
            return False
    
    def disable_cortana(self) -> bool:
        """Disable Cortana.

        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Disabling Cortana")

        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would disable Cortana")
            return True

        try:
            if platform.system() != "Windows":
                _LOGGER.error("Cortana control only supported on Windows")
                return False

            # Disable Cortana via group policy
            key_path = r"SOFTWARE\Policies\Microsoft\Windows\Windows Search"

            try:
                key = winreg.CreateKeyEx(
                    winreg.HKEY_LOCAL_MACHINE,
                    key_path,
                    0,
                    winreg.KEY_WRITE
                )

                # Set AllowCortana to 0 to disable
                winreg.SetValueEx(key, "AllowCortana", 0, winreg.REG_DWORD, 0)
                winreg.CloseKey(key)

                _LOGGER.info("Successfully disabled Cortana")
                return True

            except PermissionError:
                _LOGGER.error("Insufficient permissions to disable Cortana. Run as administrator.")
                return False

        except Exception as exc:
            _LOGGER.error("Failed to disable Cortana: %s", exc)
            return False
    
    def apply_preset(self, preset: PrivacyPreset) -> bool:
        """Apply a privacy preset.
        
        Parameters
        ----------
        preset : PrivacyPreset
            Preset to apply
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Applying privacy preset: %s", preset.name)
        
        # Set telemetry level
        self.set_telemetry_level(preset.telemetry_level)
        
        # Set app permissions
        for setting, enabled in preset.settings.items():
            self.set_app_permission(setting, enabled)
        
        # Disable advertising ID if configured
        if preset.disable_advertising_id:
            self.disable_advertising_id()
        
        # Disable Cortana if configured
        if preset.disable_cortana:
            self.disable_cortana()
        
        return True


__all__ = [
    "TelemetryLevel",
    "PrivacySetting",
    "PrivacyPreset",
    "PrivacyManager",
]
