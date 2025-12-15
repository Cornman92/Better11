"""Windows driver management.

This module provides driver backup, restore, and update checking
functionality for Windows systems.
"""
from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

from . import get_logger
from .base import SystemTool, ToolMetadata

_LOGGER = get_logger(__name__)


class DriverStatus(Enum):
    """Driver status."""
    
    OK = "ok"
    PROBLEM = "problem"
    DISABLED = "disabled"
    UNKNOWN = "unknown"


class DriverClass(Enum):
    """Common driver device classes."""
    
    DISPLAY = "Display"
    NET = "Net"
    MEDIA = "Media"
    USB = "USB"
    AUDIO = "AudioEndpoint"
    BLUETOOTH = "Bluetooth"
    STORAGE = "DiskDrive"
    PRINTER = "Printer"
    KEYBOARD = "Keyboard"
    MOUSE = "Mouse"
    SYSTEM = "System"
    OTHER = "Other"


@dataclass
class DriverInfo:
    """Information about an installed driver."""
    
    device_name: str
    device_id: str
    driver_name: str
    driver_version: str
    driver_date: Optional[datetime]
    manufacturer: str
    device_class: str
    status: DriverStatus
    inf_file: Optional[str] = None
    is_signed: bool = True
    signer: Optional[str] = None

    @property
    def is_outdated(self) -> bool:
        """Check if driver is likely outdated (> 2 years old)."""
        if not self.driver_date:
            return False
        age_days = (datetime.now() - self.driver_date).days
        return age_days > 730  # 2 years

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "device_name": self.device_name,
            "device_id": self.device_id,
            "driver_name": self.driver_name,
            "driver_version": self.driver_version,
            "driver_date": self.driver_date.isoformat() if self.driver_date else None,
            "manufacturer": self.manufacturer,
            "device_class": self.device_class,
            "status": self.status.value,
            "inf_file": self.inf_file,
            "is_signed": self.is_signed,
            "signer": self.signer
        }


@dataclass
class DriverBackup:
    """Driver backup information."""
    
    backup_path: Path
    backup_date: datetime
    driver_count: int
    size_bytes: int
    description: str

    @property
    def size_mb(self) -> float:
        """Size in megabytes."""
        return self.size_bytes / (1024 * 1024)


class DriverManager(SystemTool):
    """Manage Windows drivers.
    
    This class provides functionality for listing, backing up, restoring,
    and checking for driver updates.
    
    Parameters
    ----------
    config : dict, optional
        Configuration dictionary
    dry_run : bool
        If True, simulate operations without making changes
    """
    
    DEFAULT_BACKUP_DIR = Path.home() / ".better11" / "driver_backups"
    
    def __init__(self, config: Optional[dict] = None, dry_run: bool = False):
        super().__init__(config, dry_run)
        self._backup_dir = Path(config.get("backup_dir", self.DEFAULT_BACKUP_DIR)) if config else self.DEFAULT_BACKUP_DIR
        self._backup_dir.mkdir(parents=True, exist_ok=True)
    
    def get_metadata(self) -> ToolMetadata:
        """Return tool metadata."""
        return ToolMetadata(
            name="Driver Manager",
            description="Manage Windows device drivers",
            version="0.3.0",
            requires_admin=True,
            requires_restart=False,
            category="drivers"
        )
    
    def validate_environment(self) -> None:
        """Validate driver management prerequisites."""
        if platform.system() != "Windows":
            return
        
        try:
            # Check for pnputil
            subprocess.run(
                ["pnputil", "/?"],
                capture_output=True,
                timeout=10
            )
        except FileNotFoundError:
            _LOGGER.warning("pnputil not found - some features may not work")
    
    def execute(self) -> bool:
        """Execute default driver listing operation."""
        drivers = self.list_drivers()
        _LOGGER.info("Found %d drivers", len(drivers))
        return True
    
    def list_drivers(self, device_class: Optional[str] = None) -> List[DriverInfo]:
        """List all installed drivers.
        
        Parameters
        ----------
        device_class : str, optional
            Filter by device class
        
        Returns
        -------
        List[DriverInfo]
            List of installed drivers
        """
        _LOGGER.info("Listing installed drivers...")
        
        if platform.system() != "Windows":
            _LOGGER.warning("Driver listing only available on Windows")
            return []
        
        try:
            # Use PowerShell to get driver information
            class_filter = f"-Class '{device_class}'" if device_class else ""
            
            ps_script = f'''
            $Drivers = @()
            Get-WmiObject Win32_PnPSignedDriver {class_filter} | ForEach-Object {{
                $Drivers += @{{
                    DeviceName = $_.DeviceName
                    DeviceID = $_.DeviceID
                    DriverName = $_.DriverName
                    DriverVersion = $_.DriverVersion
                    DriverDate = if ($_.DriverDate) {{ $_.DriverDate.Substring(0, 8) }} else {{ $null }}
                    Manufacturer = $_.Manufacturer
                    DeviceClass = $_.DeviceClass
                    InfName = $_.InfName
                    IsSigned = $_.IsSigned
                    Signer = $_.Signer
                }}
            }}
            $Drivers | ConvertTo-Json -Depth 10
            '''
            
            result = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                _LOGGER.error("Failed to list drivers: %s", result.stderr)
                return []
            
            output = result.stdout.strip()
            if not output or output == "null":
                return []
            
            data = json.loads(output)
            if not isinstance(data, list):
                data = [data] if data else []
            
            drivers = []
            for item in data:
                if not item.get("DeviceName"):
                    continue
                
                driver_date = None
                if item.get("DriverDate"):
                    try:
                        driver_date = datetime.strptime(item["DriverDate"], "%Y%m%d")
                    except ValueError:
                        pass
                
                status = DriverStatus.OK
                if not item.get("IsSigned"):
                    status = DriverStatus.PROBLEM
                
                drivers.append(DriverInfo(
                    device_name=item.get("DeviceName", "Unknown"),
                    device_id=item.get("DeviceID", ""),
                    driver_name=item.get("DriverName", ""),
                    driver_version=item.get("DriverVersion", ""),
                    driver_date=driver_date,
                    manufacturer=item.get("Manufacturer", "Unknown"),
                    device_class=item.get("DeviceClass", ""),
                    status=status,
                    inf_file=item.get("InfName"),
                    is_signed=item.get("IsSigned", True),
                    signer=item.get("Signer")
                ))
            
            _LOGGER.info("Found %d drivers", len(drivers))
            return drivers
        
        except subprocess.TimeoutExpired:
            _LOGGER.error("Driver listing timed out")
            return []
        except Exception as exc:
            _LOGGER.error("Failed to list drivers: %s", exc)
            return []
    
    def get_problematic_drivers(self) -> List[DriverInfo]:
        """Get drivers with problems.
        
        Returns
        -------
        List[DriverInfo]
            List of problematic drivers
        """
        _LOGGER.info("Checking for problematic drivers...")
        
        if platform.system() != "Windows":
            return []
        
        try:
            ps_script = '''
            $Problems = @()
            Get-WmiObject Win32_PnPEntity | Where-Object { $_.ConfigManagerErrorCode -ne 0 } | ForEach-Object {
                $Problems += @{
                    DeviceName = $_.Name
                    DeviceID = $_.DeviceID
                    Status = $_.Status
                    ErrorCode = $_.ConfigManagerErrorCode
                    ErrorDescription = switch ($_.ConfigManagerErrorCode) {
                        1 { "Device not configured correctly" }
                        3 { "Driver corrupted" }
                        10 { "Device cannot start" }
                        12 { "Cannot find resources" }
                        14 { "Restart required" }
                        18 { "Reinstall drivers" }
                        19 { "Registry problem" }
                        21 { "Removing device" }
                        22 { "Device disabled" }
                        24 { "Device not present" }
                        28 { "Drivers not installed" }
                        29 { "Disabled by firmware" }
                        31 { "Device not working properly" }
                        default { "Unknown error" }
                    }
                }
            }
            $Problems | ConvertTo-Json -Depth 10
            '''
            
            result = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                return []
            
            output = result.stdout.strip()
            if not output or output == "null":
                return []
            
            data = json.loads(output)
            if not isinstance(data, list):
                data = [data] if data else []
            
            problems = []
            for item in data:
                problems.append(DriverInfo(
                    device_name=item.get("DeviceName", "Unknown"),
                    device_id=item.get("DeviceID", ""),
                    driver_name=item.get("ErrorDescription", ""),
                    driver_version="",
                    driver_date=None,
                    manufacturer="",
                    device_class="",
                    status=DriverStatus.PROBLEM
                ))
            
            _LOGGER.info("Found %d problematic drivers", len(problems))
            return problems
        
        except Exception as exc:
            _LOGGER.error("Failed to check for problems: %s", exc)
            return []
    
    def backup_drivers(self, backup_name: Optional[str] = None) -> Optional[DriverBackup]:
        """Backup all third-party drivers.
        
        Parameters
        ----------
        backup_name : str, optional
            Name for the backup. Auto-generated if not provided.
        
        Returns
        -------
        DriverBackup, optional
            Backup information or None if failed
        """
        if not backup_name:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        _LOGGER.info("Backing up drivers to %s...", backup_name)
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would backup drivers to %s", backup_name)
            return DriverBackup(
                backup_path=self._backup_dir / backup_name,
                backup_date=datetime.now(),
                driver_count=0,
                size_bytes=0,
                description="Dry run backup"
            )
        
        if platform.system() != "Windows":
            _LOGGER.error("Driver backup only available on Windows")
            return None
        
        backup_path = self._backup_dir / backup_name
        
        try:
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Use DISM to export drivers
            result = subprocess.run(
                ["dism", "/Online", "/Export-Driver", f"/Destination:{backup_path}"],
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode != 0:
                _LOGGER.error("Driver backup failed: %s", result.stderr or result.stdout)
                return None
            
            # Count backed up drivers
            driver_count = len(list(backup_path.glob("*.inf")))
            
            # Calculate size
            size = sum(f.stat().st_size for f in backup_path.rglob("*") if f.is_file())
            
            backup = DriverBackup(
                backup_path=backup_path,
                backup_date=datetime.now(),
                driver_count=driver_count,
                size_bytes=size,
                description=f"Driver backup created on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
            
            # Save backup info
            info_file = backup_path / "backup_info.json"
            with open(info_file, 'w') as f:
                json.dump({
                    "backup_date": backup.backup_date.isoformat(),
                    "driver_count": backup.driver_count,
                    "size_bytes": backup.size_bytes,
                    "description": backup.description
                }, f, indent=2)
            
            _LOGGER.info("Backed up %d drivers (%.2f MB)", driver_count, backup.size_mb)
            return backup
        
        except subprocess.TimeoutExpired:
            _LOGGER.error("Driver backup timed out")
            return None
        except Exception as exc:
            _LOGGER.error("Driver backup failed: %s", exc)
            return None
    
    def list_backups(self) -> List[DriverBackup]:
        """List available driver backups.
        
        Returns
        -------
        List[DriverBackup]
            List of available backups
        """
        backups = []
        
        if not self._backup_dir.exists():
            return backups
        
        for item in self._backup_dir.iterdir():
            if not item.is_dir():
                continue
            
            info_file = item / "backup_info.json"
            if info_file.exists():
                try:
                    with open(info_file, 'r') as f:
                        info = json.load(f)
                    
                    backups.append(DriverBackup(
                        backup_path=item,
                        backup_date=datetime.fromisoformat(info["backup_date"]),
                        driver_count=info.get("driver_count", 0),
                        size_bytes=info.get("size_bytes", 0),
                        description=info.get("description", "")
                    ))
                except Exception:
                    # Old format backup without info file
                    driver_count = len(list(item.glob("*.inf")))
                    size = sum(f.stat().st_size for f in item.rglob("*") if f.is_file())
                    
                    backups.append(DriverBackup(
                        backup_path=item,
                        backup_date=datetime.fromtimestamp(item.stat().st_mtime),
                        driver_count=driver_count,
                        size_bytes=size,
                        description="Legacy backup"
                    ))
        
        return sorted(backups, key=lambda x: x.backup_date, reverse=True)
    
    def restore_driver(self, inf_path: Path) -> bool:
        """Restore a driver from backup.
        
        Parameters
        ----------
        inf_path : Path
            Path to the driver INF file
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Restoring driver from %s", inf_path)
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would restore driver from %s", inf_path)
            return True
        
        if platform.system() != "Windows":
            _LOGGER.error("Driver restore only available on Windows")
            return False
        
        if not inf_path.exists():
            _LOGGER.error("INF file not found: %s", inf_path)
            return False
        
        try:
            # Use pnputil to add driver
            result = subprocess.run(
                ["pnputil", "/add-driver", str(inf_path), "/install"],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                _LOGGER.info("Driver restored successfully")
                return True
            else:
                _LOGGER.error("Driver restore failed: %s", result.stderr or result.stdout)
                return False
        
        except Exception as exc:
            _LOGGER.error("Driver restore failed: %s", exc)
            return False
    
    def restore_all_from_backup(self, backup: DriverBackup) -> Dict[str, bool]:
        """Restore all drivers from a backup.
        
        Parameters
        ----------
        backup : DriverBackup
            Backup to restore from
        
        Returns
        -------
        Dict[str, bool]
            Dictionary of INF file -> success status
        """
        _LOGGER.info("Restoring all drivers from %s", backup.backup_path)
        
        results = {}
        
        for inf_file in backup.backup_path.glob("**/*.inf"):
            results[inf_file.name] = self.restore_driver(inf_file)
        
        success = sum(1 for v in results.values() if v)
        _LOGGER.info("Restored %d/%d drivers", success, len(results))
        
        return results
    
    def delete_backup(self, backup: DriverBackup) -> bool:
        """Delete a driver backup.
        
        Parameters
        ----------
        backup : DriverBackup
            Backup to delete
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Deleting backup: %s", backup.backup_path)
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would delete backup")
            return True
        
        try:
            shutil.rmtree(backup.backup_path)
            _LOGGER.info("Backup deleted successfully")
            return True
        except Exception as exc:
            _LOGGER.error("Failed to delete backup: %s", exc)
            return False
    
    def get_outdated_drivers(self) -> List[DriverInfo]:
        """Get drivers that may need updates.
        
        Returns
        -------
        List[DriverInfo]
            List of potentially outdated drivers
        """
        drivers = self.list_drivers()
        outdated = [d for d in drivers if d.is_outdated]
        _LOGGER.info("Found %d potentially outdated drivers", len(outdated))
        return outdated
    
    def update_driver(self, device_id: str) -> bool:
        """Attempt to update a driver via Windows Update.
        
        Parameters
        ----------
        device_id : str
            Device ID to update
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Updating driver for device: %s", device_id)
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would update driver for %s", device_id)
            return True
        
        if platform.system() != "Windows":
            _LOGGER.error("Driver update only available on Windows")
            return False
        
        try:
            # Use pnputil to scan for driver updates
            result = subprocess.run(
                ["pnputil", "/scan-devices"],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                _LOGGER.info("Driver scan completed. Updates may be available via Windows Update.")
                return True
            else:
                _LOGGER.warning("Driver scan completed with warnings")
                return True
        
        except Exception as exc:
            _LOGGER.error("Driver update failed: %s", exc)
            return False
    
    def get_driver_summary(self) -> Dict:
        """Get a summary of installed drivers.
        
        Returns
        -------
        Dict
            Summary information
        """
        drivers = self.list_drivers()
        problems = self.get_problematic_drivers()
        
        # Count by class
        by_class: Dict[str, int] = {}
        for driver in drivers:
            cls = driver.device_class or "Unknown"
            by_class[cls] = by_class.get(cls, 0) + 1
        
        # Count unsigned
        unsigned = sum(1 for d in drivers if not d.is_signed)
        
        # Count outdated
        outdated = sum(1 for d in drivers if d.is_outdated)
        
        return {
            "total_drivers": len(drivers),
            "problematic": len(problems),
            "unsigned": unsigned,
            "potentially_outdated": outdated,
            "by_class": by_class,
            "backups_available": len(self.list_backups())
        }


__all__ = [
    "DriverStatus",
    "DriverClass",
    "DriverInfo",
    "DriverBackup",
    "DriverManager",
]
