"""Gaming optimization and performance settings.

This module provides gaming-related optimizations including Game Mode,
GPU settings, memory optimization, and performance tweaks.
"""
from __future__ import annotations

import json
import platform
import subprocess
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

from . import get_logger
from .base import SystemTool, ToolMetadata

# Import winreg for Windows
try:
    import winreg
except ImportError:
    from . import winreg_compat as winreg

_LOGGER = get_logger(__name__)


class GameModeState(Enum):
    """Game Mode state."""
    
    ENABLED = "enabled"
    DISABLED = "disabled"
    UNKNOWN = "unknown"


class GPUScheduling(Enum):
    """Hardware-accelerated GPU scheduling state."""
    
    ENABLED = 2
    DISABLED = 1
    DEFAULT = 0


@dataclass
class GamingSettings:
    """Current gaming-related settings."""
    
    game_mode_enabled: bool
    game_bar_enabled: bool
    gpu_scheduling_enabled: bool
    variable_refresh_rate: bool
    auto_hdr: bool
    fullscreen_optimizations: bool
    mouse_acceleration: bool
    pointer_precision: bool
    nagle_algorithm_disabled: bool
    power_plan: str

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "game_mode": self.game_mode_enabled,
            "game_bar": self.game_bar_enabled,
            "gpu_scheduling": self.gpu_scheduling_enabled,
            "variable_refresh_rate": self.variable_refresh_rate,
            "auto_hdr": self.auto_hdr,
            "fullscreen_optimizations": self.fullscreen_optimizations,
            "mouse_acceleration": self.mouse_acceleration,
            "pointer_precision": self.pointer_precision,
            "nagle_disabled": self.nagle_algorithm_disabled,
            "power_plan": self.power_plan
        }


@dataclass
class GamingPreset:
    """Gaming optimization preset."""
    
    name: str
    description: str
    enable_game_mode: bool
    disable_game_bar: bool
    enable_gpu_scheduling: bool
    disable_fullscreen_optimizations: bool
    disable_mouse_acceleration: bool
    disable_nagle: bool
    high_performance_power: bool
    disable_notifications: bool
    disable_background_apps: bool


class GamingOptimizer(SystemTool):
    """Optimize Windows for gaming performance.
    
    This class provides methods to configure Game Mode, GPU scheduling,
    network optimization, and other gaming-related settings.
    
    Parameters
    ----------
    config : dict, optional
        Configuration dictionary
    dry_run : bool
        If True, simulate operations without making changes
    """
    
    # Registry paths
    GAME_CONFIG_PATH = r"SOFTWARE\Microsoft\GameBar"
    GAME_DVR_PATH = r"SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR"
    GPU_SCHEDULING_PATH = r"SYSTEM\CurrentControlSet\Control\GraphicsDrivers"
    MOUSE_PATH = r"Control Panel\Mouse"
    NETWORK_PATH = r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces"
    
    # Presets
    MAXIMUM_PERFORMANCE = GamingPreset(
        name="Maximum Performance",
        description="All optimizations enabled for best gaming performance",
        enable_game_mode=True,
        disable_game_bar=True,
        enable_gpu_scheduling=True,
        disable_fullscreen_optimizations=True,
        disable_mouse_acceleration=True,
        disable_nagle=True,
        high_performance_power=True,
        disable_notifications=True,
        disable_background_apps=True
    )
    
    BALANCED_GAMING = GamingPreset(
        name="Balanced Gaming",
        description="Good performance while keeping useful features",
        enable_game_mode=True,
        disable_game_bar=False,
        enable_gpu_scheduling=True,
        disable_fullscreen_optimizations=False,
        disable_mouse_acceleration=True,
        disable_nagle=False,
        high_performance_power=False,
        disable_notifications=True,
        disable_background_apps=False
    )
    
    STREAMING_OPTIMIZED = GamingPreset(
        name="Streaming Optimized",
        description="Optimized for game streaming/recording",
        enable_game_mode=True,
        disable_game_bar=False,  # Keep for recording
        enable_gpu_scheduling=True,
        disable_fullscreen_optimizations=False,
        disable_mouse_acceleration=True,
        disable_nagle=False,
        high_performance_power=True,
        disable_notifications=True,
        disable_background_apps=False
    )
    
    DEFAULT_SETTINGS = GamingPreset(
        name="Windows Default",
        description="Reset to Windows default settings",
        enable_game_mode=True,
        disable_game_bar=False,
        enable_gpu_scheduling=False,
        disable_fullscreen_optimizations=False,
        disable_mouse_acceleration=False,
        disable_nagle=False,
        high_performance_power=False,
        disable_notifications=False,
        disable_background_apps=False
    )
    
    def __init__(self, config: Optional[dict] = None, dry_run: bool = False):
        super().__init__(config, dry_run)
    
    def get_metadata(self) -> ToolMetadata:
        """Return tool metadata."""
        return ToolMetadata(
            name="Gaming Optimizer",
            description="Optimize Windows for gaming performance",
            version="0.3.0",
            requires_admin=True,
            requires_restart=False,
            category="gaming"
        )
    
    def validate_environment(self) -> None:
        """Validate gaming optimization prerequisites."""
        pass
    
    def execute(self) -> bool:
        """Execute default gaming status check."""
        settings = self.get_current_settings()
        if settings:
            _LOGGER.info("Game Mode: %s", "Enabled" if settings.game_mode_enabled else "Disabled")
        return True
    
    def get_current_settings(self) -> Optional[GamingSettings]:
        """Get current gaming-related settings.
        
        Returns
        -------
        GamingSettings, optional
            Current settings or None if unavailable
        """
        if platform.system() != "Windows":
            return None
        
        try:
            game_mode = self._get_game_mode_status()
            game_bar = self._get_game_bar_status()
            gpu_scheduling = self._get_gpu_scheduling_status()
            mouse_accel = self._get_mouse_acceleration_status()
            
            # Get power plan
            power_plan = "Unknown"
            try:
                result = subprocess.run(
                    ["powercfg", "/getactivescheme"],
                    capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    output = result.stdout
                    if "High performance" in output:
                        power_plan = "High Performance"
                    elif "Balanced" in output:
                        power_plan = "Balanced"
                    elif "Power saver" in output:
                        power_plan = "Power Saver"
                    elif "Ultimate" in output:
                        power_plan = "Ultimate Performance"
            except Exception:
                pass
            
            return GamingSettings(
                game_mode_enabled=game_mode,
                game_bar_enabled=game_bar,
                gpu_scheduling_enabled=gpu_scheduling,
                variable_refresh_rate=False,  # Would need more complex detection
                auto_hdr=False,
                fullscreen_optimizations=True,  # Default Windows behavior
                mouse_acceleration=mouse_accel,
                pointer_precision=mouse_accel,
                nagle_algorithm_disabled=False,  # Default
                power_plan=power_plan
            )
        
        except Exception as exc:
            _LOGGER.error("Failed to get gaming settings: %s", exc)
            return None
    
    def _get_game_mode_status(self) -> bool:
        """Check if Game Mode is enabled."""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"SOFTWARE\Microsoft\GameBar",
                0,
                winreg.KEY_READ
            )
            value, _ = winreg.QueryValueEx(key, "AutoGameModeEnabled")
            winreg.CloseKey(key)
            return value == 1
        except Exception:
            return True  # Default enabled in Windows 11
    
    def _get_game_bar_status(self) -> bool:
        """Check if Game Bar is enabled."""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR",
                0,
                winreg.KEY_READ
            )
            value, _ = winreg.QueryValueEx(key, "AppCaptureEnabled")
            winreg.CloseKey(key)
            return value == 1
        except Exception:
            return True  # Default enabled
    
    def _get_gpu_scheduling_status(self) -> bool:
        """Check if hardware GPU scheduling is enabled."""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                self.GPU_SCHEDULING_PATH,
                0,
                winreg.KEY_READ
            )
            value, _ = winreg.QueryValueEx(key, "HwSchMode")
            winreg.CloseKey(key)
            return value == 2
        except Exception:
            return False
    
    def _get_mouse_acceleration_status(self) -> bool:
        """Check if mouse acceleration is enabled."""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.MOUSE_PATH,
                0,
                winreg.KEY_READ
            )
            value, _ = winreg.QueryValueEx(key, "MouseSpeed")
            winreg.CloseKey(key)
            return value != "0"
        except Exception:
            return True  # Default enabled
    
    # Game Mode settings
    
    def set_game_mode(self, enabled: bool) -> bool:
        """Enable or disable Game Mode.
        
        Parameters
        ----------
        enabled : bool
            Whether to enable Game Mode
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("%s Game Mode", "Enabling" if enabled else "Disabling")
        return self._set_registry_value(
            winreg.HKEY_CURRENT_USER,
            r"SOFTWARE\Microsoft\GameBar",
            "AutoGameModeEnabled",
            1 if enabled else 0
        )
    
    def set_game_bar(self, enabled: bool) -> bool:
        """Enable or disable Xbox Game Bar.
        
        Parameters
        ----------
        enabled : bool
            Whether to enable Game Bar
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("%s Game Bar", "Enabling" if enabled else "Disabling")
        
        success = True
        success &= self._set_registry_value(
            winreg.HKEY_CURRENT_USER,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR",
            "AppCaptureEnabled",
            1 if enabled else 0
        )
        success &= self._set_registry_value(
            winreg.HKEY_CURRENT_USER,
            r"SOFTWARE\Microsoft\GameBar",
            "UseNexusForGameBarEnabled",
            1 if enabled else 0
        )
        
        return success
    
    def set_gpu_scheduling(self, enabled: bool) -> bool:
        """Enable or disable hardware-accelerated GPU scheduling.
        
        Note: Requires restart to take effect.
        
        Parameters
        ----------
        enabled : bool
            Whether to enable GPU scheduling
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("%s hardware GPU scheduling", "Enabling" if enabled else "Disabling")
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would %s GPU scheduling", "enable" if enabled else "disable")
            return True
        
        success = self._set_registry_value(
            winreg.HKEY_LOCAL_MACHINE,
            self.GPU_SCHEDULING_PATH,
            "HwSchMode",
            2 if enabled else 1
        )
        
        if success:
            _LOGGER.warning("System restart required for GPU scheduling changes")
        
        return success
    
    # Mouse settings
    
    def set_mouse_acceleration(self, enabled: bool) -> bool:
        """Enable or disable mouse acceleration.
        
        Parameters
        ----------
        enabled : bool
            Whether to enable acceleration
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("%s mouse acceleration", "Enabling" if enabled else "Disabling")
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would %s mouse acceleration", "enable" if enabled else "disable")
            return True
        
        if platform.system() != "Windows":
            return False
        
        try:
            key = winreg.CreateKeyEx(
                winreg.HKEY_CURRENT_USER,
                self.MOUSE_PATH,
                0,
                winreg.KEY_WRITE
            )
            
            if enabled:
                # Default Windows acceleration curve
                winreg.SetValueEx(key, "MouseSpeed", 0, winreg.REG_SZ, "1")
                winreg.SetValueEx(key, "MouseThreshold1", 0, winreg.REG_SZ, "6")
                winreg.SetValueEx(key, "MouseThreshold2", 0, winreg.REG_SZ, "10")
            else:
                # Disable acceleration
                winreg.SetValueEx(key, "MouseSpeed", 0, winreg.REG_SZ, "0")
                winreg.SetValueEx(key, "MouseThreshold1", 0, winreg.REG_SZ, "0")
                winreg.SetValueEx(key, "MouseThreshold2", 0, winreg.REG_SZ, "0")
            
            winreg.CloseKey(key)
            
            _LOGGER.info("Mouse acceleration %s. May require logout.", "enabled" if enabled else "disabled")
            return True
        
        except Exception as exc:
            _LOGGER.error("Failed to set mouse acceleration: %s", exc)
            return False
    
    # Network optimizations
    
    def disable_nagle_algorithm(self) -> bool:
        """Disable Nagle's algorithm for reduced network latency.
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Disabling Nagle's algorithm")
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would disable Nagle's algorithm")
            return True
        
        if platform.system() != "Windows":
            return False
        
        try:
            # Find network interfaces
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                self.NETWORK_PATH,
                0,
                winreg.KEY_READ
            )
            
            index = 0
            modified = 0
            
            while True:
                try:
                    interface_id = winreg.EnumKey(key, index)
                    interface_path = f"{self.NETWORK_PATH}\\{interface_id}"
                    
                    # Set TcpAckFrequency and TCPNoDelay
                    iface_key = winreg.OpenKey(
                        winreg.HKEY_LOCAL_MACHINE,
                        interface_path,
                        0,
                        winreg.KEY_WRITE
                    )
                    
                    winreg.SetValueEx(iface_key, "TcpAckFrequency", 0, winreg.REG_DWORD, 1)
                    winreg.SetValueEx(iface_key, "TCPNoDelay", 0, winreg.REG_DWORD, 1)
                    winreg.CloseKey(iface_key)
                    modified += 1
                    
                    index += 1
                except OSError:
                    break
            
            winreg.CloseKey(key)
            
            _LOGGER.info("Nagle's algorithm disabled on %d interfaces", modified)
            return True
        
        except Exception as exc:
            _LOGGER.error("Failed to disable Nagle: %s", exc)
            return False
    
    def enable_nagle_algorithm(self) -> bool:
        """Re-enable Nagle's algorithm (Windows default).
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Re-enabling Nagle's algorithm")
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would enable Nagle's algorithm")
            return True
        
        if platform.system() != "Windows":
            return False
        
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                self.NETWORK_PATH,
                0,
                winreg.KEY_READ
            )
            
            index = 0
            
            while True:
                try:
                    interface_id = winreg.EnumKey(key, index)
                    interface_path = f"{self.NETWORK_PATH}\\{interface_id}"
                    
                    iface_key = winreg.OpenKey(
                        winreg.HKEY_LOCAL_MACHINE,
                        interface_path,
                        0,
                        winreg.KEY_WRITE
                    )
                    
                    # Remove the values to restore defaults
                    try:
                        winreg.DeleteValue(iface_key, "TcpAckFrequency")
                    except FileNotFoundError:
                        pass
                    try:
                        winreg.DeleteValue(iface_key, "TCPNoDelay")
                    except FileNotFoundError:
                        pass
                    
                    winreg.CloseKey(iface_key)
                    index += 1
                except OSError:
                    break
            
            winreg.CloseKey(key)
            return True
        
        except Exception as exc:
            _LOGGER.error("Failed to enable Nagle: %s", exc)
            return False
    
    # Fullscreen optimizations
    
    def disable_fullscreen_optimizations_globally(self) -> bool:
        """Disable fullscreen optimizations for all applications.
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Disabling fullscreen optimizations globally")
        return self._set_registry_value(
            winreg.HKEY_CURRENT_USER,
            r"System\GameConfigStore",
            "GameDVR_FSEBehaviorMode",
            2
        )
    
    def enable_fullscreen_optimizations_globally(self) -> bool:
        """Enable fullscreen optimizations (Windows default).
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Enabling fullscreen optimizations globally")
        return self._set_registry_value(
            winreg.HKEY_CURRENT_USER,
            r"System\GameConfigStore",
            "GameDVR_FSEBehaviorMode",
            0
        )
    
    # Notifications
    
    def disable_focus_assist_for_gaming(self) -> bool:
        """Configure Focus Assist to enable during gaming.
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Configuring Focus Assist for gaming")
        return self._set_registry_value(
            winreg.HKEY_CURRENT_USER,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\CloudStore\Store\Cache\DefaultAccount\$$windows.data.notifications.quiethourssettings\Current",
            "Data",
            1  # Auto-enable during gaming
        )
    
    # Power settings
    
    def set_high_performance_power(self) -> bool:
        """Set power plan to High Performance.
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Setting High Performance power plan")
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would set High Performance power plan")
            return True
        
        if platform.system() != "Windows":
            return False
        
        try:
            # High Performance GUID
            hp_guid = "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"
            
            result = subprocess.run(
                ["powercfg", "/setactive", hp_guid],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                _LOGGER.info("High Performance power plan activated")
                return True
            else:
                # Try Ultimate Performance
                up_guid = "e9a42b02-d5df-448d-aa00-03f14749eb61"
                result = subprocess.run(
                    ["powercfg", "/setactive", up_guid],
                    capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    _LOGGER.info("Ultimate Performance power plan activated")
                    return True
                
            _LOGGER.warning("Could not set High Performance power plan")
            return False
        
        except Exception as exc:
            _LOGGER.error("Failed to set power plan: %s", exc)
            return False
    
    def create_ultimate_performance_plan(self) -> bool:
        """Create Ultimate Performance power plan if not available.
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Creating Ultimate Performance power plan")
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would create Ultimate Performance plan")
            return True
        
        if platform.system() != "Windows":
            return False
        
        try:
            result = subprocess.run(
                ["powercfg", "-duplicatescheme", "e9a42b02-d5df-448d-aa00-03f14749eb61"],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                _LOGGER.info("Ultimate Performance plan created")
                return True
            else:
                _LOGGER.warning("Ultimate Performance plan may already exist or is not supported")
                return False
        
        except Exception as exc:
            _LOGGER.error("Failed to create power plan: %s", exc)
            return False
    
    # Presets
    
    def apply_preset(self, preset: GamingPreset) -> Dict[str, bool]:
        """Apply a gaming optimization preset.
        
        Parameters
        ----------
        preset : GamingPreset
            Preset to apply
        
        Returns
        -------
        Dict[str, bool]
            Results for each setting
        """
        _LOGGER.info("Applying gaming preset: %s", preset.name)
        
        results = {}
        
        results["game_mode"] = self.set_game_mode(preset.enable_game_mode)
        results["game_bar"] = self.set_game_bar(not preset.disable_game_bar)
        results["gpu_scheduling"] = self.set_gpu_scheduling(preset.enable_gpu_scheduling)
        
        if preset.disable_fullscreen_optimizations:
            results["fullscreen_opt"] = self.disable_fullscreen_optimizations_globally()
        else:
            results["fullscreen_opt"] = self.enable_fullscreen_optimizations_globally()
        
        results["mouse_acceleration"] = self.set_mouse_acceleration(not preset.disable_mouse_acceleration)
        
        if preset.disable_nagle:
            results["nagle"] = self.disable_nagle_algorithm()
        
        if preset.high_performance_power:
            results["power_plan"] = self.set_high_performance_power()
        
        success = sum(1 for v in results.values() if v)
        total = len(results)
        _LOGGER.info("Preset applied: %d/%d settings successful", success, total)
        
        return results
    
    def get_presets(self) -> List[GamingPreset]:
        """Get all available gaming presets.
        
        Returns
        -------
        List[GamingPreset]
            Available presets
        """
        return [
            self.MAXIMUM_PERFORMANCE,
            self.BALANCED_GAMING,
            self.STREAMING_OPTIMIZED,
            self.DEFAULT_SETTINGS
        ]
    
    # Helper
    
    def _set_registry_value(
        self,
        root_key,
        key_path: str,
        value_name: str,
        value: int
    ) -> bool:
        """Set a registry DWORD value.
        
        Parameters
        ----------
        root_key
            Root registry key
        key_path : str
            Path to the key
        value_name : str
            Value name
        value : int
            Value to set
        
        Returns
        -------
        bool
            True if successful
        """
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would set %s\\%s to %d", key_path, value_name, value)
            return True
        
        if platform.system() != "Windows":
            _LOGGER.error("Registry operations only available on Windows")
            return False
        
        try:
            key = winreg.CreateKeyEx(
                root_key,
                key_path,
                0,
                winreg.KEY_WRITE
            )
            
            winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, value)
            winreg.CloseKey(key)
            
            return True
        
        except Exception as exc:
            _LOGGER.error("Failed to set registry value: %s", exc)
            return False


__all__ = [
    "GameModeState",
    "GPUScheduling",
    "GamingSettings",
    "GamingPreset",
    "GamingOptimizer",
]
