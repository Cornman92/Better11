"""Windows optional features management.

This module provides control over Windows optional features that can be
enabled or disabled using DISM.
"""
from __future__ import annotations

import shutil
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

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

        # Check if DISM is available
        if shutil.which("dism") is None:
            raise SafetyError(
                "DISM (Deployment Image Servicing and Management) is not available. "
                "This tool is required for managing Windows features."
            )
    
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
        # TODO: Use DISM /Online /Get-Features
        raise NotImplementedError("List features - coming in v0.3.0")
    
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
        _LOGGER.info("Enabling feature: %s", feature_name)
        # TODO: Use DISM /Online /Enable-Feature
        raise NotImplementedError("Enable feature - coming in v0.3.0")
    
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
        # TODO: Use DISM /Online /Disable-Feature
        raise NotImplementedError("Disable feature - coming in v0.3.0")
    
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
