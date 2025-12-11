"""Disk and storage management.

This module provides comprehensive disk and storage management including
space analysis, cleanup, optimization, and health monitoring.
"""
from __future__ import annotations

import shutil
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

from . import get_logger
from .base import SystemTool, ToolMetadata

_LOGGER = get_logger(__name__)


class DriveType(Enum):
    """Type of disk drive."""
    
    HDD = "hdd"
    SSD = "ssd"
    REMOVABLE = "removable"
    NETWORK = "network"
    UNKNOWN = "unknown"


@dataclass
class DiskInfo:
    """Disk/volume information."""
    
    drive_letter: str
    label: str
    file_system: str
    drive_type: DriveType
    total_bytes: int
    used_bytes: int
    free_bytes: int
    
    @property
    def total_gb(self) -> float:
        """Total space in GB."""
        return self.total_bytes / (1024 ** 3)
    
    @property
    def used_gb(self) -> float:
        """Used space in GB."""
        return self.used_bytes / (1024 ** 3)
    
    @property
    def free_gb(self) -> float:
        """Free space in GB."""
        return self.free_bytes / (1024 ** 3)
    
    @property
    def usage_percent(self) -> float:
        """Usage percentage."""
        if self.total_bytes == 0:
            return 0.0
        return (self.used_bytes / self.total_bytes) * 100


@dataclass
class CleanupResult:
    """Result of cleanup operation."""
    
    locations_cleaned: List[str]
    files_removed: int
    space_freed_bytes: int
    
    @property
    def space_freed_mb(self) -> float:
        """Space freed in MB."""
        return self.space_freed_bytes / (1024 ** 2)


class DiskManager(SystemTool):
    """Manage disk and storage operations.
    
    This class provides methods for disk space analysis, cleanup,
    optimization, and health monitoring.
    
    Parameters
    ----------
    config : dict, optional
        Configuration dictionary
    dry_run : bool
        If True, simulate operations without making changes
    """
    
    # Common temporary file locations
    TEMP_LOCATIONS = [
        Path(r"C:\Windows\Temp"),
        Path.home() / "AppData" / "Local" / "Temp",
        Path(r"C:\Windows\Prefetch"),
        Path.home() / "AppData" / "Local" / "Microsoft" / "Windows" / "INetCache",
        Path(r"C:\Windows\SoftwareDistribution\Download"),
    ]
    
    def __init__(self, config: Optional[dict] = None, dry_run: bool = False):
        super().__init__(config, dry_run)
    
    def get_metadata(self) -> ToolMetadata:
        """Return tool metadata."""
        return ToolMetadata(
            name="Disk Manager",
            description="Manage disk space, cleanup, and optimization",
            version="0.3.0",
            requires_admin=False,  # Most operations don't need admin
            requires_restart=False,
            category="storage"
        )
    
    def validate_environment(self) -> None:
        """Validate disk management prerequisites."""
        pass
    
    def execute(self) -> bool:
        """Execute default disk analysis operation."""
        disks = self.analyze_disk_space()
        _LOGGER.info("Found %d disk volumes", len(disks))
        return True
    
    def analyze_disk_space(self) -> Dict[str, DiskInfo]:
        """Analyze disk space for all volumes.
        
        Returns
        -------
        Dict[str, DiskInfo]
            Dictionary mapping drive letters to disk information
        """
        _LOGGER.info("Analyzing disk space for all volumes")
        
        disks: Dict[str, DiskInfo] = {}
        
        import platform
        if platform.system() != "Windows":
            _LOGGER.warning("Disk analysis limited on non-Windows platforms")
            # Still return root filesystem info
            usage = shutil.disk_usage("/")
            disks["/"] = DiskInfo(
                drive_letter="/",
                label="Root",
                file_system="unknown",
                drive_type=DriveType.UNKNOWN,
                total_bytes=usage.total,
                used_bytes=usage.used,
                free_bytes=usage.free
            )
            return disks
        
        # On Windows, enumerate drives A-Z
        import string
        for letter in string.ascii_uppercase:
            drive_path = f"{letter}:\\"
            drive = Path(drive_path)
            
            if not drive.exists():
                continue
            
            try:
                usage = shutil.disk_usage(drive_path)
                
                disks[letter] = DiskInfo(
                    drive_letter=letter,
                    label=self._get_volume_label(drive_path),
                    file_system=self._get_file_system(drive_path),
                    drive_type=self._get_drive_type(drive_path),
                    total_bytes=usage.total,
                    used_bytes=usage.used,
                    free_bytes=usage.free
                )
                
                _LOGGER.debug(
                    "Drive %s: %.2f GB / %.2f GB (%.1f%% used)",
                    letter,
                    usage.used / (1024 ** 3),
                    usage.total / (1024 ** 3),
                    (usage.used / usage.total * 100) if usage.total > 0 else 0
                )
            
            except (PermissionError, OSError) as exc:
                _LOGGER.debug("Cannot access drive %s: %s", letter, exc)
                continue
        
        return disks
    
    def _get_volume_label(self, drive_path: str) -> str:
        """Get volume label for drive."""
        try:
            import win32api
            return win32api.GetVolumeInformation(drive_path)[0] or "Local Disk"
        except Exception:
            return "Local Disk"
    
    def _get_file_system(self, drive_path: str) -> str:
        """Get file system type for drive."""
        try:
            import win32api
            return win32api.GetVolumeInformation(drive_path)[4]
        except Exception:
            return "unknown"
    
    def _get_drive_type(self, drive_path: str) -> DriveType:
        """Get drive type."""
        try:
            import win32file
            drive_type_num = win32file.GetDriveType(drive_path)
            
            type_map = {
                0: DriveType.UNKNOWN,
                1: DriveType.UNKNOWN,
                2: DriveType.REMOVABLE,
                3: DriveType.HDD,  # Fixed disk
                4: DriveType.NETWORK,
                5: DriveType.REMOVABLE,  # CD-ROM
                6: DriveType.REMOVABLE,  # RAM disk
            }
            
            return type_map.get(drive_type_num, DriveType.UNKNOWN)
        except Exception:
            return DriveType.UNKNOWN
    
    def cleanup_temp_files(self, age_days: int = 7) -> CleanupResult:
        """Clean up temporary files older than specified days.
        
        Parameters
        ----------
        age_days : int
            Delete files older than this many days
        
        Returns
        -------
        CleanupResult
            Result of cleanup operation
        """
        _LOGGER.info("Cleaning temporary files older than %d days", age_days)
        
        if self._dry_run:
            _LOGGER.info("[DRY RUN] Would clean temporary files")
            return CleanupResult(
                locations_cleaned=[],
                files_removed=0,
                space_freed_bytes=0
            )
        
        import time
        from datetime import datetime, timedelta
        
        cutoff_time = time.time() - (age_days * 86400)
        locations_cleaned = []
        files_removed = 0
        space_freed = 0
        
        for temp_dir in self.TEMP_LOCATIONS:
            if not temp_dir.exists():
                _LOGGER.debug("Temp directory does not exist: %s", temp_dir)
                continue
            
            _LOGGER.info("Cleaning: %s", temp_dir)
            try:
                for item in temp_dir.rglob("*"):
                    if not item.is_file():
                        continue
                    
                    try:
                        # Check if file is old enough
                        if item.stat().st_mtime > cutoff_time:
                            continue
                        
                        file_size = item.stat().st_size
                        item.unlink()
                        files_removed += 1
                        space_freed += file_size
                        
                    except (PermissionError, OSError) as exc:
                        _LOGGER.debug("Cannot delete %s: %s", item, exc)
                        continue
                
                locations_cleaned.append(str(temp_dir))
            
            except (PermissionError, OSError) as exc:
                _LOGGER.warning("Cannot access %s: %s", temp_dir, exc)
        
        result = CleanupResult(
            locations_cleaned=locations_cleaned,
            files_removed=files_removed,
            space_freed_bytes=space_freed
        )
        
        _LOGGER.info(
            "Cleanup complete: %d files removed, %.2f MB freed",
            files_removed,
            result.space_freed_mb
        )
        
        return result
    
    def get_disk_usage_by_folder(self, root_path: Path, max_depth: int = 2) -> Dict[str, int]:
        """Analyze disk usage by folder.
        
        Parameters
        ----------
        root_path : Path
            Root path to analyze
        max_depth : int
            Maximum depth to analyze
        
        Returns
        -------
        Dict[str, int]
            Dictionary mapping folder paths to sizes in bytes
        """
        _LOGGER.info("Analyzing disk usage for: %s", root_path)
        
        usage: Dict[str, int] = {}
        
        try:
            for item in root_path.iterdir():
                if item.is_dir():
                    try:
                        size = sum(f.stat().st_size for f in item.rglob("*") if f.is_file())
                        usage[str(item)] = size
                    except (PermissionError, OSError):
                        continue
        
        except (PermissionError, OSError) as exc:
            _LOGGER.error("Cannot analyze %s: %s", root_path, exc)
        
        return dict(sorted(usage.items(), key=lambda x: x[1], reverse=True))


__all__ = [
    "DriveType",
    "DiskInfo",
    "CleanupResult",
    "DiskManager",
]
