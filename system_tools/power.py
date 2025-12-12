"""Power and energy management.

This module provides control over Windows power plans, sleep settings,
and power management features.
"""
from __future__ import annotations

import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional

from . import get_logger
from .base import SystemTool, ToolMetadata

_LOGGER = get_logger(__name__)


class PowerPlanType(Enum):
    """Type of power plan."""
    
    BALANCED = "balanced"
    HIGH_PERFORMANCE = "high_performance"
    POWER_SAVER = "power_saver"
    ULTIMATE_PERFORMANCE = "ultimate_performance"
    CUSTOM = "custom"


@dataclass
class PowerPlan:
    """Power plan information."""
    
    guid: str
    name: str
    plan_type: PowerPlanType
    is_active: bool


class PowerManager(SystemTool):
    """Manage power and energy settings.
    
    This class provides methods for managing power plans, sleep settings,
    hibernation, and battery reporting.
    
    Parameters
    ----------
    config : dict, optional
        Configuration dictionary
    dry_run : bool
        If True, simulate operations without making changes
    """
    
    # Well-known power plan GUIDs
    BALANCED_GUID = "381b4222-f694-41f0-9685-ff5bb260df2e"
    HIGH_PERFORMANCE_GUID = "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"
    POWER_SAVER_GUID = "a1841308-3541-4fab-bc81-f71556f20b4a"
    ULTIMATE_PERFORMANCE_GUID = "e9a42b02-d5df-448d-aa00-03f14749eb61"
    
    def __init__(self, config: Optional[dict] = None, dry_run: bool = False):
        super().__init__(config, dry_run)
    
    def get_metadata(self) -> ToolMetadata:
        """Return tool metadata."""
        return ToolMetadata(
            name="Power Manager",
            description="Manage power and energy settings",
            version="0.3.0",
            requires_admin=True,
            requires_restart=False,
            category="power"
        )
    
    def validate_environment(self) -> None:
        """Validate power management prerequisites."""
        pass
    
    def execute(self) -> bool:
        """Execute default power plan listing operation."""
        plans = self.list_power_plans()
        _LOGGER.info("Found %d power plans", len(plans))
        return True
    
    def list_power_plans(self) -> List[PowerPlan]:
        """List all available power plans.
        
        Returns
        -------
        List[PowerPlan]
            List of power plans
        """
        _LOGGER.info("Listing power plans")
        
        import platform
        if platform.system() != "Windows":
            _LOGGER.warning("Power plans only supported on Windows")
            return []
        
        try:
            result = subprocess.run(
                ["powercfg", "/list"],
                capture_output=True,
                text=True,
                check=True
            )
            
            plans = []
            
            for line in result.stdout.splitlines():
                if "Power Scheme GUID:" in line:
                    parts = line.split()
                    guid = parts[3]
                    name = " ".join(parts[4:]).strip("()")
                    is_active = "*" in line
                    
                    # Determine plan type
                    plan_type = PowerPlanType.CUSTOM
                    if guid == self.BALANCED_GUID:
                        plan_type = PowerPlanType.BALANCED
                    elif guid == self.HIGH_PERFORMANCE_GUID:
                        plan_type = PowerPlanType.HIGH_PERFORMANCE
                    elif guid == self.POWER_SAVER_GUID:
                        plan_type = PowerPlanType.POWER_SAVER
                    elif guid == self.ULTIMATE_PERFORMANCE_GUID:
                        plan_type = PowerPlanType.ULTIMATE_PERFORMANCE
                    
                    plans.append(PowerPlan(
                        guid=guid,
                        name=name,
                        plan_type=plan_type,
                        is_active=is_active
                    ))
            
            _LOGGER.info("Found %d power plans", len(plans))
            return plans
        
        except subprocess.CalledProcessError as exc:
            _LOGGER.error("Failed to list power plans: %s", exc)
            return []
    
    def get_active_plan(self) -> Optional[PowerPlan]:
        """Get the currently active power plan.
        
        Returns
        -------
        PowerPlan, optional
            Active power plan, or None if not found
        """
        plans = self.list_power_plans()
        for plan in plans:
            if plan.is_active:
                return plan
        return None
    
    def set_active_plan(self, plan_guid: str) -> bool:
        """Set the active power plan.
        
        Parameters
        ----------
        plan_guid : str
            GUID of plan to activate
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Setting active power plan: %s", plan_guid)
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would set active power plan")
            return True
        
        import platform
        if platform.system() != "Windows":
            _LOGGER.error("Power plans only supported on Windows")
            return False
        
        try:
            subprocess.run(
                ["powercfg", "/setactive", plan_guid],
                check=True,
                capture_output=True
            )
            _LOGGER.info("Power plan activated successfully")
            return True
        
        except subprocess.CalledProcessError as exc:
            _LOGGER.error("Failed to set active power plan: %s", exc)
            return False
    
    def enable_hibernation(self) -> bool:
        """Enable hibernation.
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Enabling hibernation")
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would enable hibernation")
            return True
        
        import platform
        if platform.system() != "Windows":
            _LOGGER.error("Hibernation only supported on Windows")
            return False
        
        try:
            subprocess.run(
                ["powercfg", "/hibernate", "on"],
                check=True,
                capture_output=True
            )
            _LOGGER.info("Hibernation enabled successfully")
            return True
        
        except subprocess.CalledProcessError as exc:
            _LOGGER.error("Failed to enable hibernation: %s", exc)
            return False
    
    def disable_hibernation(self) -> bool:
        """Disable hibernation.
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Disabling hibernation")
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would disable hibernation")
            return True
        
        import platform
        if platform.system() != "Windows":
            _LOGGER.error("Hibernation only supported on Windows")
            return False
        
        try:
            subprocess.run(
                ["powercfg", "/hibernate", "off"],
                check=True,
                capture_output=True
            )
            _LOGGER.info("Hibernation disabled successfully")
            return True
        
        except subprocess.CalledProcessError as exc:
            _LOGGER.error("Failed to disable hibernation: %s", exc)
            return False
    
    def generate_battery_report(self, output_path: Optional[Path] = None) -> Optional[Path]:
        """Generate battery health report.
        
        Parameters
        ----------
        output_path : Path, optional
            Path to save report. If None, uses default location.
        
        Returns
        -------
        Path, optional
            Path to generated report, or None if failed
        """
        _LOGGER.info("Generating battery report")
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would generate battery report")
            return Path("battery-report.html")
        
        import platform
        if platform.system() != "Windows":
            _LOGGER.error("Battery report only supported on Windows")
            return None
        
        if output_path is None:
            output_path = Path.home() / "battery-report.html"
        
        try:
            subprocess.run(
                ["powercfg", "/batteryreport", "/output", str(output_path)],
                check=True,
                capture_output=True
            )
            _LOGGER.info("Battery report generated: %s", output_path)
            return output_path
        
        except subprocess.CalledProcessError as exc:
            _LOGGER.error("Failed to generate battery report: %s", exc)
            return None


__all__ = [
    "PowerPlanType",
    "PowerPlan",
    "PowerManager",
]
