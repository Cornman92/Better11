"""System backup and restore operations.

This module provides backup and restore functionality for system restore points,
registry, drivers, and configuration settings.
"""
from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from . import get_logger
from .base import SystemTool, ToolMetadata
from .safety import SafetyError

_LOGGER = get_logger(__name__)


@dataclass
class RestorePoint:
    """System restore point information."""
    
    sequence_number: int
    description: str
    creation_time: datetime
    restore_point_type: str
    event_type: str


class BackupManager(SystemTool):
    """Manage system backups and restore operations.
    
    This class provides methods for creating/restoring system restore points,
    backing up registry hives, and managing configuration backups.
    
    Parameters
    ----------
    config : dict, optional
        Configuration dictionary
    dry_run : bool
        If True, simulate operations without making changes
    """
    
    def __init__(self, config: Optional[dict] = None, dry_run: bool = False):
        super().__init__(config, dry_run)
        self._backup_dir = Path.home() / ".better11" / "backups"
        self._backup_dir.mkdir(parents=True, exist_ok=True)
    
    def get_metadata(self) -> ToolMetadata:
        """Return tool metadata."""
        return ToolMetadata(
            name="Backup Manager",
            description="Manage system backups and restore operations",
            version="0.3.0",
            requires_admin=True,
            requires_restart=False,
            category="backup"
        )
    
    def validate_environment(self) -> None:
        """Validate backup prerequisites."""
        pass
    
    def execute(self) -> bool:
        """Execute default restore point listing operation."""
        points = self.list_restore_points()
        _LOGGER.info("Found %d restore points", len(points))
        return True
    
    def create_restore_point(self, description: str) -> Optional[RestorePoint]:
        """Create a system restore point.
        
        Parameters
        ----------
        description : str
            Description for the restore point
        
        Returns
        -------
        RestorePoint, optional
            Created restore point, or None if failed
        """
        _LOGGER.info("Creating system restore point: %s", description)
        
        if self._dry_run:
            _LOGGER.info("[DRY RUN] Would create restore point")
            return RestorePoint(
                sequence_number=0,
                description=description,
                creation_time=datetime.now(),
                restore_point_type="APPLICATION_INSTALL",
                event_type="BEGIN_SYSTEM_CHANGE"
            )
        
        import platform
        if platform.system() != "Windows":
            _LOGGER.error("System restore points only supported on Windows")
            return None
        
        try:
            # Use PowerShell to create restore point
            ps_script = f'''
            Checkpoint-Computer -Description "{description}" -RestorePointType "MODIFY_SETTINGS"
            '''
            
            result = subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True,
                text=True,
                check=True
            )
            
            _LOGGER.info("Restore point created successfully")
            
            # Return the most recent restore point
            points = self.list_restore_points()
            if points:
                return points[0]
            return None
        
        except subprocess.CalledProcessError as exc:
            _LOGGER.error("Failed to create restore point: %s", exc)
            return None
    
    def list_restore_points(self) -> List[RestorePoint]:
        """List all system restore points.
        
        Returns
        -------
        List[RestorePoint]
            List of restore points, most recent first
        """
        _LOGGER.info("Listing system restore points")
        
        import platform
        if platform.system() != "Windows":
            _LOGGER.warning("System restore points only supported on Windows")
            return []
        
        try:
            # Use PowerShell to list restore points
            ps_script = '''
            Get-ComputerRestorePoint |
            Select-Object SequenceNumber, Description, CreationTime, RestorePointType, EventType |
            ConvertTo-Json
            '''
            
            result = subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True,
                text=True,
                check=True
            )
            
            if not result.stdout.strip():
                _LOGGER.info("No restore points found")
                return []
            
            data = json.loads(result.stdout)
            
            # Handle single vs multiple results
            if not isinstance(data, list):
                data = [data]
            
            points = []
            for item in data:
                points.append(RestorePoint(
                    sequence_number=item["SequenceNumber"],
                    description=item["Description"],
                    creation_time=datetime.fromisoformat(item["CreationTime"].replace("Z", "+00:00")),
                    restore_point_type=item["RestorePointType"],
                    event_type=item["EventType"]
                ))
            
            _LOGGER.info("Found %d restore points", len(points))
            return points
        
        except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as exc:
            _LOGGER.error("Failed to list restore points: %s", exc)
            return []
    
    def backup_registry_hive(self, hive: str, backup_path: Path) -> bool:
        """Backup a registry hive to a file.
        
        Parameters
        ----------
        hive : str
            Registry hive to backup (e.g., HKCU, HKLM)
        backup_path : Path
            Path to save backup file
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Backing up registry hive %s to %s", hive, backup_path)
        
        if self._dry_run:
            _LOGGER.info("[DRY RUN] Would backup registry hive")
            return True
        
        import platform
        if platform.system() != "Windows":
            _LOGGER.error("Registry backup only supported on Windows")
            return False
        
        try:
            # Use reg export command
            cmd = ["reg", "export", hive, str(backup_path), "/y"]
            subprocess.run(cmd, check=True, capture_output=True)
            
            _LOGGER.info("Registry hive backed up successfully")
            return True
        
        except subprocess.CalledProcessError as exc:
            _LOGGER.error("Failed to backup registry hive: %s", exc)
            return False
    
    def export_settings(self, export_path: Path) -> bool:
        """Export Better11 configuration settings.
        
        Parameters
        ----------
        export_path : Path
            Path to save settings
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Exporting settings to %s", export_path)
        
        try:
            settings = {
                "version": "0.3.0",
                "export_date": datetime.now().isoformat(),
                "config": self.config,
            }
            
            export_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(export_path, 'w') as f:
                json.dump(settings, f, indent=2)
            
            _LOGGER.info("Settings exported successfully")
            return True
        
        except Exception as exc:
            _LOGGER.error("Failed to export settings: %s", exc)
            return False
    
    def import_settings(self, import_path: Path) -> bool:
        """Import Better11 configuration settings.
        
        Parameters
        ----------
        import_path : Path
            Path to settings file
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Importing settings from %s", import_path)
        
        if self._dry_run:
            _LOGGER.info("[DRY RUN] Would import settings")
            return True
        
        try:
            with open(import_path, 'r') as f:
                settings = json.load(f)
            
            # Validate settings
            if "version" not in settings or "config" not in settings:
                raise ValueError("Invalid settings file format")
            
            # Update config
            self.config.update(settings["config"])
            
            _LOGGER.info("Settings imported successfully")
            return True
        
        except Exception as exc:
            _LOGGER.error("Failed to import settings: %s", exc)
            return False


__all__ = [
    "RestorePoint",
    "BackupManager",
]
