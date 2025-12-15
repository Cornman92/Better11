"""Windows optional features management.

This module provides control over Windows optional features that can be
enabled or disabled using DISM.
"""
from __future__ import annotations

import json
import platform
import subprocess
import re
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

from . import get_logger
from .base import SystemTool, ToolMetadata
from .safety import SafetyError, ensure_windows

_LOGGER = get_logger(__name__)


class FeatureState(Enum):
    """State of a Windows optional feature."""
    
    ENABLED = "enabled"
    DISABLED = "disabled"
    ENABLE_PENDING = "enable_pending"
    DISABLE_PENDING = "disable_pending"
    PARTIALLY_ENABLED = "partially_enabled"
    UNKNOWN = "unknown"


@dataclass
class WindowsFeature:
    """Representation of a Windows optional feature."""
    
    name: str
    display_name: str
    description: str
    state: FeatureState
    restart_required: bool = False
    dependencies: Optional[List[str]] = None
    parent: Optional[str] = None

    @property
    def is_enabled(self) -> bool:
        """Check if feature is currently enabled."""
        return self.state in (FeatureState.ENABLED, FeatureState.ENABLE_PENDING)


@dataclass
class FeaturePreset:
    """Predefined feature configuration preset."""
    
    name: str
    description: str
    features_to_enable: List[str]
    features_to_disable: List[str]


class WindowsFeaturesManager(SystemTool):
    """Manage Windows optional features.
    
    This class provides methods to list, enable, and disable Windows
    optional features using DISM.
    
    Parameters
    ----------
    config : dict, optional
        Configuration dictionary
    dry_run : bool
        If True, simulate operations without making changes
    """
    
    # Predefined presets
    DEVELOPER_PRESET = FeaturePreset(
        name="Developer",
        description="Enable features useful for software developers",
        features_to_enable=[
            "Microsoft-Windows-Subsystem-Linux",
            "VirtualMachinePlatform",
            "Microsoft-Hyper-V-All",
            "Containers",
            "TelnetClient",
            "NetFx3",
        ],
        features_to_disable=[]
    )
    
    MINIMAL_PRESET = FeaturePreset(
        name="Minimal",
        description="Disable unnecessary features for minimal installation",
        features_to_enable=[],
        features_to_disable=[
            "WorkFolders-Client",
            "Printing-XPSServices-Features",
            "MediaPlayback",
            "WindowsMediaPlayer",
            "Internet-Explorer-Optional-amd64",
            "MSRDC-Infrastructure",
        ]
    )
    
    GAMING_PRESET = FeaturePreset(
        name="Gaming",
        description="Optimize features for gaming",
        features_to_enable=[
            "DirectPlay",
            "NetFx3",
        ],
        features_to_disable=[
            "WorkFolders-Client",
            "Printing-XPSServices-Features",
            "Internet-Explorer-Optional-amd64",
        ]
    )
    
    SERVER_PRESET = FeaturePreset(
        name="Server-like",
        description="Enable server-oriented features",
        features_to_enable=[
            "TelnetClient",
            "TFTP",
            "NetFx3",
            "Containers",
        ],
        features_to_disable=[
            "MediaPlayback",
            "WindowsMediaPlayer",
        ]
    )
    
    # Common feature descriptions
    FEATURE_DESCRIPTIONS: Dict[str, str] = {
        "Microsoft-Windows-Subsystem-Linux": "Windows Subsystem for Linux (WSL) - Run Linux distributions",
        "VirtualMachinePlatform": "Virtual Machine Platform - Required for WSL 2",
        "Microsoft-Hyper-V-All": "Hyper-V virtualization platform",
        "Containers": "Windows Containers support",
        "NetFx3": ".NET Framework 3.5 - Required for older applications",
        "TelnetClient": "Telnet client for remote connections",
        "TFTP": "TFTP client for file transfers",
        "DirectPlay": "Legacy gaming API",
        "WindowsMediaPlayer": "Windows Media Player",
        "MediaPlayback": "Media playback features",
        "Internet-Explorer-Optional-amd64": "Internet Explorer 11",
        "Printing-XPSServices-Features": "XPS document services",
        "WorkFolders-Client": "Work Folders sync client",
        "SmbDirect": "SMB Direct (RDMA) support",
        "IIS-WebServerRole": "Internet Information Services (IIS)",
    }
    
    def __init__(self, config: Optional[dict] = None, dry_run: bool = False):
        super().__init__(config, dry_run)
        self._feature_cache: Dict[str, WindowsFeature] = {}
    
    def get_metadata(self) -> ToolMetadata:
        """Return tool metadata."""
        return ToolMetadata(
            name="Windows Features Manager",
            description="Manage Windows optional features",
            version="0.3.0",
            requires_admin=True,
            requires_restart=True,  # Many features require restart
            category="features"
        )
    
    def validate_environment(self) -> None:
        """Validate DISM availability."""
        if platform.system() != "Windows":
            return
        
        try:
            result = subprocess.run(
                ["dism", "/?"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                _LOGGER.warning("DISM may not be available")
        except FileNotFoundError:
            _LOGGER.error("DISM not found in PATH")
        except Exception as exc:
            _LOGGER.warning("Could not verify DISM: %s", exc)
    
    def execute(self) -> bool:
        """Execute default feature listing operation."""
        features = self.list_features()
        _LOGGER.info("Found %d Windows features", len(features))
        return True
    
    def list_features(self, state: Optional[FeatureState] = None) -> List[WindowsFeature]:
        """List available Windows features.
        
        Parameters
        ----------
        state : FeatureState, optional
            Filter by feature state
        
        Returns
        -------
        List[WindowsFeature]
            List of Windows features
        """
        _LOGGER.info("Listing Windows features")
        
        if platform.system() != "Windows":
            _LOGGER.warning("Windows features only available on Windows")
            return []
        
        try:
            # Use DISM to list features
            result = subprocess.run(
                ["dism", "/Online", "/Get-Features", "/Format:Table"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                _LOGGER.error("DISM failed: %s", result.stderr)
                return []
            
            features = self._parse_dism_output(result.stdout)
            
            # Filter by state if specified
            if state is not None:
                features = [f for f in features if f.state == state]
            
            _LOGGER.info("Found %d features", len(features))
            return features
        
        except subprocess.TimeoutExpired:
            _LOGGER.error("DISM command timed out")
            return []
        except Exception as exc:
            _LOGGER.error("Failed to list features: %s", exc)
            return []
    
    def _parse_dism_output(self, output: str) -> List[WindowsFeature]:
        """Parse DISM /Get-Features output.
        
        Parameters
        ----------
        output : str
            DISM command output
        
        Returns
        -------
        List[WindowsFeature]
            Parsed features
        """
        features = []
        
        # Parse table format output
        lines = output.splitlines()
        in_table = False
        
        for line in lines:
            line = line.strip()
            
            # Skip header lines
            if "Feature Name" in line and "State" in line:
                in_table = True
                continue
            
            if not in_table or not line:
                continue
            
            # Skip separator lines
            if line.startswith("-"):
                continue
            
            # Parse feature line (format: "Feature Name | State")
            parts = re.split(r'\s*\|\s*', line)
            if len(parts) >= 2:
                feature_name = parts[0].strip()
                state_str = parts[1].strip().lower()
                
                # Map state string to enum
                state = FeatureState.UNKNOWN
                if state_str in ("enabled", "enable"):
                    state = FeatureState.ENABLED
                elif state_str in ("disabled", "disable"):
                    state = FeatureState.DISABLED
                elif "pending" in state_str:
                    if "enable" in state_str:
                        state = FeatureState.ENABLE_PENDING
                    else:
                        state = FeatureState.DISABLE_PENDING
                
                description = self.FEATURE_DESCRIPTIONS.get(feature_name, "")
                
                feature = WindowsFeature(
                    name=feature_name,
                    display_name=feature_name.replace("-", " "),
                    description=description,
                    state=state
                )
                features.append(feature)
        
        return features
    
    def get_feature(self, feature_name: str) -> Optional[WindowsFeature]:
        """Get detailed information about a specific feature.
        
        Parameters
        ----------
        feature_name : str
            Name of the feature
        
        Returns
        -------
        WindowsFeature, optional
            Feature details or None if not found
        """
        _LOGGER.debug("Getting feature details: %s", feature_name)
        
        if platform.system() != "Windows":
            return None
        
        try:
            result = subprocess.run(
                ["dism", "/Online", "/Get-FeatureInfo", f"/FeatureName:{feature_name}"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return None
            
            return self._parse_feature_info(result.stdout, feature_name)
        
        except Exception as exc:
            _LOGGER.error("Failed to get feature info: %s", exc)
            return None
    
    def _parse_feature_info(self, output: str, feature_name: str) -> Optional[WindowsFeature]:
        """Parse DISM /Get-FeatureInfo output.
        
        Parameters
        ----------
        output : str
            DISM command output
        feature_name : str
            Feature name
        
        Returns
        -------
        WindowsFeature, optional
            Parsed feature
        """
        lines = output.splitlines()
        
        display_name = feature_name
        description = ""
        state = FeatureState.UNKNOWN
        restart_required = False
        
        for line in lines:
            line = line.strip()
            
            if line.startswith("Display Name :"):
                display_name = line.split(":", 1)[1].strip()
            elif line.startswith("Description :"):
                description = line.split(":", 1)[1].strip()
            elif line.startswith("State :"):
                state_str = line.split(":", 1)[1].strip().lower()
                if state_str == "enabled":
                    state = FeatureState.ENABLED
                elif state_str == "disabled":
                    state = FeatureState.DISABLED
                elif "pending" in state_str:
                    if "enable" in state_str:
                        state = FeatureState.ENABLE_PENDING
                    else:
                        state = FeatureState.DISABLE_PENDING
            elif line.startswith("Restart Required :"):
                restart_str = line.split(":", 1)[1].strip().lower()
                restart_required = restart_str in ("yes", "possible")
        
        return WindowsFeature(
            name=feature_name,
            display_name=display_name,
            description=description,
            state=state,
            restart_required=restart_required
        )
    
    def enable_feature(self, feature_name: str, include_dependencies: bool = True) -> bool:
        """Enable a Windows feature.
        
        Parameters
        ----------
        feature_name : str
            Name of feature to enable
        include_dependencies : bool
            Whether to enable parent/dependency features automatically
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Enabling feature: %s", feature_name)
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would enable feature: %s", feature_name)
            return True
        
        if platform.system() != "Windows":
            _LOGGER.error("Feature management only available on Windows")
            return False
        
        try:
            cmd = ["dism", "/Online", "/Enable-Feature", f"/FeatureName:{feature_name}", "/NoRestart"]
            
            if include_dependencies:
                cmd.append("/All")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # Features can take a while to enable
            )
            
            if result.returncode == 0:
                _LOGGER.info("Feature %s enabled successfully", feature_name)
                if "restart" in result.stdout.lower():
                    _LOGGER.warning("System restart may be required")
                return True
            elif result.returncode == 3010:
                _LOGGER.info("Feature %s enabled. Restart required.", feature_name)
                return True
            else:
                _LOGGER.error("Failed to enable feature: %s", result.stderr or result.stdout)
                return False
        
        except subprocess.TimeoutExpired:
            _LOGGER.error("Feature enable timed out")
            return False
        except Exception as exc:
            _LOGGER.error("Failed to enable feature: %s", exc)
            return False
    
    def disable_feature(self, feature_name: str) -> bool:
        """Disable a Windows feature.
        
        Parameters
        ----------
        feature_name : str
            Name of feature to disable
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Disabling feature: %s", feature_name)
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would disable feature: %s", feature_name)
            return True
        
        if platform.system() != "Windows":
            _LOGGER.error("Feature management only available on Windows")
            return False
        
        try:
            result = subprocess.run(
                ["dism", "/Online", "/Disable-Feature", f"/FeatureName:{feature_name}", "/NoRestart"],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                _LOGGER.info("Feature %s disabled successfully", feature_name)
                if "restart" in result.stdout.lower():
                    _LOGGER.warning("System restart may be required")
                return True
            elif result.returncode == 3010:
                _LOGGER.info("Feature %s disabled. Restart required.", feature_name)
                return True
            else:
                _LOGGER.error("Failed to disable feature: %s", result.stderr or result.stdout)
                return False
        
        except subprocess.TimeoutExpired:
            _LOGGER.error("Feature disable timed out")
            return False
        except Exception as exc:
            _LOGGER.error("Failed to disable feature: %s", exc)
            return False
    
    def apply_preset(self, preset: FeaturePreset) -> dict:
        """Apply a feature preset.
        
        Parameters
        ----------
        preset : FeaturePreset
            Preset to apply
        
        Returns
        -------
        dict
            Results with 'enabled', 'disabled', 'failed' lists
        """
        _LOGGER.info("Applying feature preset: %s", preset.name)
        
        results = {
            "enabled": [],
            "disabled": [],
            "failed": [],
            "restart_required": False
        }
        
        # Enable features
        for feature in preset.features_to_enable:
            if self.enable_feature(feature):
                results["enabled"].append(feature)
            else:
                results["failed"].append(feature)
        
        # Disable features
        for feature in preset.features_to_disable:
            if self.disable_feature(feature):
                results["disabled"].append(feature)
            else:
                results["failed"].append(feature)
        
        # Check if restart is needed
        if results["enabled"] or results["disabled"]:
            results["restart_required"] = True
        
        _LOGGER.info(
            "Preset applied: %d enabled, %d disabled, %d failed",
            len(results["enabled"]),
            len(results["disabled"]),
            len(results["failed"])
        )
        
        return results
    
    def check_wsl_status(self) -> dict:
        """Check WSL (Windows Subsystem for Linux) status.
        
        Returns
        -------
        dict
            WSL status information
        """
        _LOGGER.info("Checking WSL status")
        
        if platform.system() != "Windows":
            return {"available": False, "reason": "Not on Windows"}
        
        result = {
            "available": False,
            "wsl_enabled": False,
            "vm_platform_enabled": False,
            "wsl2_capable": False,
            "distributions": []
        }
        
        try:
            # Check WSL feature
            features = self.list_features()
            for f in features:
                if f.name == "Microsoft-Windows-Subsystem-Linux":
                    result["wsl_enabled"] = f.is_enabled
                elif f.name == "VirtualMachinePlatform":
                    result["vm_platform_enabled"] = f.is_enabled
            
            result["wsl2_capable"] = result["wsl_enabled"] and result["vm_platform_enabled"]
            result["available"] = result["wsl_enabled"]
            
            # List distributions if WSL is enabled
            if result["wsl_enabled"]:
                try:
                    wsl_result = subprocess.run(
                        ["wsl", "--list", "--verbose"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if wsl_result.returncode == 0:
                        # Parse distribution list
                        lines = wsl_result.stdout.strip().split("\n")[1:]  # Skip header
                        for line in lines:
                            if line.strip():
                                parts = line.split()
                                if len(parts) >= 3:
                                    name = parts[0].replace("*", "").strip()
                                    state = parts[1].strip()
                                    version = parts[2].strip() if len(parts) > 2 else "1"
                                    result["distributions"].append({
                                        "name": name,
                                        "state": state,
                                        "version": version
                                    })
                except Exception:
                    pass
        
        except Exception as exc:
            _LOGGER.error("Failed to check WSL status: %s", exc)
        
        return result
    
    def enable_wsl(self, wsl2: bool = True) -> bool:
        """Enable WSL (Windows Subsystem for Linux).
        
        Parameters
        ----------
        wsl2 : bool
            Enable WSL 2 (requires VM Platform)
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Enabling WSL%s", " 2" if wsl2 else "")
        
        success = True
        
        # Enable WSL feature
        if not self.enable_feature("Microsoft-Windows-Subsystem-Linux"):
            success = False
        
        # Enable VM Platform for WSL 2
        if wsl2 and not self.enable_feature("VirtualMachinePlatform"):
            success = False
        
        if success:
            _LOGGER.info("WSL enabled. Restart required to complete setup.")
        
        return success
    
    def enable_hyper_v(self) -> bool:
        """Enable Hyper-V virtualization.
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Enabling Hyper-V")
        return self.enable_feature("Microsoft-Hyper-V-All")
    
    def get_presets(self) -> List[FeaturePreset]:
        """Get all available feature presets.
        
        Returns
        -------
        List[FeaturePreset]
            Available presets
        """
        return [
            self.DEVELOPER_PRESET,
            self.MINIMAL_PRESET,
            self.GAMING_PRESET,
            self.SERVER_PRESET
        ]


__all__ = [
    "FeatureState",
    "WindowsFeature",
    "FeaturePreset",
    "WindowsFeaturesManager",
]
