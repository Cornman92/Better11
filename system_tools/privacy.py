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
from .safety import ensure_windows

_LOGGER = get_logger(__name__)

# Registry paths for privacy settings
TELEMETRY_KEY = r"HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection"
PRIVACY_KEY = r"HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager"
ADVERTISING_KEY = r"HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo"
CORTANA_KEY = r"HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search"


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
        ensure_windows()
        _LOGGER.info("Setting telemetry level to %s", level.name)
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would set telemetry level to %s", level.name)
            return True
        
        try:
            import winreg
            
            # Open or create registry key
            key_path = r"SOFTWARE\Policies\Microsoft\Windows\DataCollection"
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    key_path,
                    0,
                    winreg.KEY_WRITE
                )
            except FileNotFoundError:
                # Create key if it doesn't exist
                key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
            
            # Set AllowTelemetry value
            winreg.SetValueEx(key, "AllowTelemetry", 0, winreg.REG_DWORD, level.value)
            winreg.CloseKey(key)
            
            _LOGGER.info("Successfully set telemetry level to %s", level.name)
            return True
            
        except PermissionError:
            _LOGGER.error("Administrator privileges required to set telemetry level")
            return False
        except Exception as e:
            _LOGGER.error("Error setting telemetry level: %s", e)
            return False
    
    def get_telemetry_level(self) -> TelemetryLevel:
        """Get current Windows telemetry level.
        
        Returns
        -------
        TelemetryLevel
            Current telemetry level
        """
        ensure_windows()
        
        try:
            import winreg
            
            key_path = r"SOFTWARE\Policies\Microsoft\Windows\DataCollection"
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
            
            return level_map.get(value, TelemetryLevel.BASIC)
            
        except FileNotFoundError:
            # Key doesn't exist, return default
            _LOGGER.debug("Telemetry registry key not found, using default")
            return TelemetryLevel.BASIC
        except Exception as e:
            _LOGGER.warning("Error reading telemetry level: %s", e)
            return TelemetryLevel.BASIC
    
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
        ensure_windows()
        _LOGGER.info("Setting %s permission to %s", setting.value, enabled)
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would set %s permission to %s", setting.value, enabled)
            return True
        
        try:
            import winreg
            
            # Map privacy settings to registry subkeys
            # Windows 10/11 stores app permissions in CapabilityAccessManager
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore"
            
            # Create subkey for this permission
            subkey_path = f"{key_path}\\{setting.value}"
            
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    subkey_path,
                    0,
                    winreg.KEY_WRITE
                )
            except FileNotFoundError:
                key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, subkey_path)
            
            # Set Value to "Deny" (0) or "Allow" (1)
            winreg.SetValueEx(key, "Value", 0, winreg.REG_SZ, "Deny" if not enabled else "Allow")
            winreg.CloseKey(key)
            
            _LOGGER.info("Successfully set %s permission to %s", setting.value, enabled)
            return True
            
        except Exception as e:
            _LOGGER.error("Error setting app permission: %s", e)
            return False
    
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
        ensure_windows()
        
        try:
            import winreg
            
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore"
            subkey_path = f"{key_path}\\{setting.value}"
            
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                subkey_path,
                0,
                winreg.KEY_READ
            )
            
            value, _ = winreg.QueryValueEx(key, "Value")
            winreg.CloseKey(key)
            
            return value.lower() == "allow"
            
        except FileNotFoundError:
            # Key doesn't exist, return default (usually enabled)
            _LOGGER.debug("Permission registry key not found for %s", setting.value)
            return True
        except Exception as e:
            _LOGGER.warning("Error reading app permission: %s", e)
            return True  # Default to enabled
    
    def disable_advertising_id(self) -> bool:
        """Disable Windows advertising ID.
        
        Returns
        -------
        bool
            True if successful
        """
        ensure_windows()
        _LOGGER.info("Disabling advertising ID")
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would disable advertising ID")
            return True
        
        try:
            import winreg
            
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo"
            
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    key_path,
                    0,
                    winreg.KEY_WRITE
                )
            except FileNotFoundError:
                key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
            
            # Set Enabled to 0 (disabled)
            winreg.SetValueEx(key, "Enabled", 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(key)
            
            _LOGGER.info("Successfully disabled advertising ID")
            return True
            
        except Exception as e:
            _LOGGER.error("Error disabling advertising ID: %s", e)
            return False
    
    def disable_cortana(self) -> bool:
        """Disable Cortana.
        
        Returns
        -------
        bool
            True if successful
        """
        ensure_windows()
        _LOGGER.info("Disabling Cortana")
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would disable Cortana")
            return True
        
        try:
            import winreg
            
            # Disable Cortana via group policy registry keys
            key_path = r"SOFTWARE\Policies\Microsoft\Windows\Windows Search"
            
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    key_path,
                    0,
                    winreg.KEY_WRITE
                )
            except FileNotFoundError:
                key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
            
            # Set AllowCortana to 0 (disabled)
            winreg.SetValueEx(key, "AllowCortana", 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(key)
            
            _LOGGER.info("Successfully disabled Cortana")
            return True
            
        except PermissionError:
            _LOGGER.error("Administrator privileges required to disable Cortana")
            return False
        except Exception as e:
            _LOGGER.error("Error disabling Cortana: %s", e)
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
