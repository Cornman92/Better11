"""Windows optional features management.

This module provides control over Windows optional features that can be
enabled or disabled using DISM.
"""
from __future__ import annotations

import platform
import subprocess
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from . import get_logger
from .base import SystemTool, ToolMetadata
from .safety import ensure_windows

_LOGGER = get_logger(__name__)


class FeatureState(Enum):
    """State of a Windows optional feature."""
    
    ENABLED = "enabled"
    DISABLED = "disabled"
    ENABLE_PENDING = "enable_pending"
    DISABLE_PENDING = "disable_pending"


@dataclass
class WindowsFeature:
    """Representation of a Windows optional feature."""
    
    name: str
    display_name: str
    description: str
    state: FeatureState
    restart_required: bool = False
    dependencies: Optional[List[str]] = None


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
        ]
    )
    
    def __init__(self, config: Optional[dict] = None, dry_run: bool = False):
        super().__init__(config, dry_run)
    
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
        ensure_windows()
        
        try:
            result = subprocess.run(
                ["dism", "/?"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                raise RuntimeError("DISM is not available on this system")
        except FileNotFoundError:
            raise RuntimeError("DISM command not found. DISM is required for Windows feature management.")
        except Exception as e:
            _LOGGER.warning("Could not verify DISM availability: %s", e)
    
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
        ensure_windows()
        _LOGGER.info("Listing Windows features")
        
        try:
            # Use DISM to list features
            result = subprocess.run(
                ["dism", "/Online", "/Get-Features", "/Format:Table"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                _LOGGER.error("DISM command failed: %s", result.stderr)
                return []
            
            features: List[WindowsFeature] = []
            lines = result.stdout.split('\n')
            
            # Parse DISM output
            # Format: Feature Name | State
            in_table = False
            for line in lines:
                line = line.strip()
                
                # Skip header lines
                if 'Feature Name' in line and 'State' in line:
                    in_table = True
                    continue
                
                if not in_table or not line or '---' in line:
                    continue
                
                # Parse feature line
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 2:
                    feature_name = parts[0]
                    state_str = parts[1].upper()
                    
                    # Map DISM state to our enum
                    state_map = {
                        "ENABLED": FeatureState.ENABLED,
                        "DISABLED": FeatureState.DISABLED,
                        "ENABLE PENDING": FeatureState.ENABLE_PENDING,
                        "DISABLE PENDING": FeatureState.DISABLE_PENDING,
                    }
                    
                    feature_state = state_map.get(state_str, FeatureState.DISABLED)
                    
                    # Filter by state if requested
                    if state and feature_state != state:
                        continue
                    
                    # Get display name (try to get from DISM /Get-FeatureInfo)
                    display_name = feature_name.replace("-", " ").title()
                    
                    feature = WindowsFeature(
                        name=feature_name,
                        display_name=display_name,
                        description="",  # Would need separate DISM call for description
                        state=feature_state,
                        restart_required=False,  # Would need to check
                        dependencies=None
                    )
                    features.append(feature)
            
            _LOGGER.info("Found %d Windows feature(s)", len(features))
            return features
            
        except subprocess.TimeoutExpired:
            _LOGGER.error("DISM command timed out")
            return []
        except Exception as e:
            _LOGGER.error("Error listing Windows features: %s", e)
            return []
    
    def enable_feature(self, feature_name: str) -> bool:
        """Enable a Windows feature.
        
        Parameters
        ----------
        feature_name : str
            Name of feature to enable
        
        Returns
        -------
        bool
            True if successful
        """
        ensure_windows()
        _LOGGER.info("Enabling feature: %s", feature_name)
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would enable feature: %s", feature_name)
            return True
        
        try:
            # Use DISM to enable feature
            result = subprocess.run(
                ["dism", "/Online", "/Enable-Feature", f"/FeatureName:{feature_name}", "/NoRestart"],
                capture_output=True,
                text=True,
                timeout=600  # Feature installation can take time
            )
            
            if result.returncode == 0:
                _LOGGER.info("Successfully enabled feature: %s", feature_name)
                
                # Check if restart is required
                if "restart" in result.stdout.lower() or "reboot" in result.stdout.lower():
                    _LOGGER.warning("Restart may be required for feature: %s", feature_name)
                
                return True
            else:
                _LOGGER.error("Failed to enable feature %s: %s", feature_name, result.stderr)
                return False
                
        except subprocess.TimeoutExpired:
            _LOGGER.error("Feature enable operation timed out")
            return False
        except Exception as e:
            _LOGGER.error("Error enabling feature: %s", e)
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
        ensure_windows()
        _LOGGER.info("Disabling feature: %s", feature_name)
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would disable feature: %s", feature_name)
            return True
        
        try:
            # Use DISM to disable feature
            result = subprocess.run(
                ["dism", "/Online", "/Disable-Feature", f"/FeatureName:{feature_name}", "/NoRestart"],
                capture_output=True,
                text=True,
                timeout=600  # Feature removal can take time
            )
            
            if result.returncode == 0:
                _LOGGER.info("Successfully disabled feature: %s", feature_name)
                
                # Check if restart is required
                if "restart" in result.stdout.lower() or "reboot" in result.stdout.lower():
                    _LOGGER.warning("Restart may be required for feature: %s", feature_name)
                
                return True
            else:
                _LOGGER.error("Failed to disable feature %s: %s", feature_name, result.stderr)
                return False
                
        except subprocess.TimeoutExpired:
            _LOGGER.error("Feature disable operation timed out")
            return False
        except Exception as e:
            _LOGGER.error("Error disabling feature: %s", e)
            return False
    
    def get_feature_dependencies(self, feature_name: str) -> List[str]:
        """Get feature dependencies.
        
        Parameters
        ----------
        feature_name : str
            Name of feature
        
        Returns
        -------
        List[str]
            List of dependent feature names
        """
        ensure_windows()
        
        try:
            # Use DISM to get feature info
            result = subprocess.run(
                ["dism", "/Online", "/Get-FeatureInfo", f"/FeatureName:{feature_name}"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                _LOGGER.warning("Could not get feature info for %s", feature_name)
                return []
            
            # Parse dependencies from output
            dependencies: List[str] = []
            lines = result.stdout.split('\n')
            
            in_dependencies = False
            for line in lines:
                line = line.strip()
                
                if 'Dependencies' in line or 'Depends On' in line:
                    in_dependencies = True
                    continue
                
                if in_dependencies and line:
                    # Extract feature names from dependency lines
                    if ':' in line:
                        dep_name = line.split(':')[0].strip()
                        if dep_name:
                            dependencies.append(dep_name)
                    elif line and not line.startswith('-'):
                        dependencies.append(line)
            
            return dependencies
            
        except Exception as e:
            _LOGGER.warning("Error getting feature dependencies: %s", e)
            return []
    
    def get_feature_state(self, feature_name: str) -> FeatureState:
        """Get the state of a specific feature.
        
        Parameters
        ----------
        feature_name : str
            Name of feature
        
        Returns
        -------
        FeatureState
            Current state of the feature
        """
        features = self.list_features()
        for feature in features:
            if feature.name == feature_name:
                return feature.state
        
        # Feature not found, assume disabled
        return FeatureState.DISABLED
    
    def apply_preset(self, preset: FeaturePreset) -> bool:
        """Apply a feature preset.
        
        Parameters
        ----------
        preset : FeaturePreset
            Preset to apply
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Applying feature preset: %s", preset.name)
        
        # Enable features
        for feature in preset.features_to_enable:
            self.enable_feature(feature)
        
        # Disable features
        for feature in preset.features_to_disable:
            self.disable_feature(feature)
        
        return True


__all__ = [
    "FeatureState",
    "WindowsFeature",
    "FeaturePreset",
    "WindowsFeaturesManager",
]
