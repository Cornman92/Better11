"""System information gathering.

This module provides comprehensive system information including hardware,
software, Windows version, and system health details.
"""
from __future__ import annotations

import json
import os
import platform
import subprocess
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from . import get_logger
from .base import SystemTool, ToolMetadata

_LOGGER = get_logger(__name__)


@dataclass
class CPUInfo:
    """CPU information."""
    
    name: str
    manufacturer: str
    cores: int
    logical_processors: int
    max_clock_mhz: int
    architecture: str
    current_usage: float

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "manufacturer": self.manufacturer,
            "cores": self.cores,
            "logical_processors": self.logical_processors,
            "max_clock_mhz": self.max_clock_mhz,
            "architecture": self.architecture,
            "current_usage": self.current_usage
        }


@dataclass
class MemoryInfo:
    """Memory information."""
    
    total_bytes: int
    available_bytes: int
    used_bytes: int
    usage_percent: float
    slots_used: int
    slots_total: int
    speed_mhz: int
    type_name: str

    @property
    def total_gb(self) -> float:
        """Total memory in GB."""
        return self.total_bytes / (1024 ** 3)

    @property
    def available_gb(self) -> float:
        """Available memory in GB."""
        return self.available_bytes / (1024 ** 3)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "total_gb": round(self.total_gb, 2),
            "available_gb": round(self.available_gb, 2),
            "usage_percent": self.usage_percent,
            "slots_used": self.slots_used,
            "slots_total": self.slots_total,
            "speed_mhz": self.speed_mhz,
            "type": self.type_name
        }


@dataclass
class GPUInfo:
    """Graphics card information."""
    
    name: str
    manufacturer: str
    driver_version: str
    driver_date: Optional[datetime]
    video_memory_mb: int
    current_resolution: str

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "manufacturer": self.manufacturer,
            "driver_version": self.driver_version,
            "driver_date": self.driver_date.isoformat() if self.driver_date else None,
            "video_memory_mb": self.video_memory_mb,
            "current_resolution": self.current_resolution
        }


@dataclass
class StorageInfo:
    """Storage device information."""
    
    name: str
    model: str
    media_type: str  # HDD, SSD, NVMe
    size_bytes: int
    interface_type: str
    status: str
    partitions: int

    @property
    def size_gb(self) -> float:
        """Size in GB."""
        return self.size_bytes / (1024 ** 3)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "model": self.model,
            "media_type": self.media_type,
            "size_gb": round(self.size_gb, 2),
            "interface_type": self.interface_type,
            "status": self.status,
            "partitions": self.partitions
        }


@dataclass
class NetworkAdapterInfo:
    """Network adapter information."""
    
    name: str
    description: str
    mac_address: str
    connection_status: str
    speed_mbps: int
    ip_addresses: List[str]
    gateway: Optional[str]

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "mac_address": self.mac_address,
            "connection_status": self.connection_status,
            "speed_mbps": self.speed_mbps,
            "ip_addresses": self.ip_addresses,
            "gateway": self.gateway
        }


@dataclass
class WindowsInfo:
    """Windows version information."""
    
    version: str
    build: str
    edition: str
    product_id: str
    install_date: Optional[datetime]
    last_boot: Optional[datetime]
    uptime_hours: float
    registered_owner: str
    system_root: str
    windows_directory: str

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "version": self.version,
            "build": self.build,
            "edition": self.edition,
            "product_id": self.product_id,
            "install_date": self.install_date.isoformat() if self.install_date else None,
            "last_boot": self.last_boot.isoformat() if self.last_boot else None,
            "uptime_hours": round(self.uptime_hours, 2),
            "registered_owner": self.registered_owner,
            "system_root": self.system_root
        }


@dataclass
class BIOSInfo:
    """BIOS/UEFI information."""
    
    manufacturer: str
    version: str
    release_date: Optional[datetime]
    serial_number: str
    is_uefi: bool

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "manufacturer": self.manufacturer,
            "version": self.version,
            "release_date": self.release_date.isoformat() if self.release_date else None,
            "serial_number": self.serial_number,
            "is_uefi": self.is_uefi
        }


@dataclass
class SystemSummary:
    """Complete system summary."""
    
    computer_name: str
    domain: str
    manufacturer: str
    model: str
    system_type: str
    windows: WindowsInfo
    cpu: CPUInfo
    memory: MemoryInfo
    gpus: List[GPUInfo]
    storage: List[StorageInfo]
    network: List[NetworkAdapterInfo]
    bios: BIOSInfo

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "computer_name": self.computer_name,
            "domain": self.domain,
            "manufacturer": self.manufacturer,
            "model": self.model,
            "system_type": self.system_type,
            "windows": self.windows.to_dict(),
            "cpu": self.cpu.to_dict(),
            "memory": self.memory.to_dict(),
            "gpus": [g.to_dict() for g in self.gpus],
            "storage": [s.to_dict() for s in self.storage],
            "network": [n.to_dict() for n in self.network],
            "bios": self.bios.to_dict()
        }


class SystemInfoManager(SystemTool):
    """Gather comprehensive system information.
    
    This class provides methods to collect detailed information about
    the system hardware, software, and configuration.
    
    Parameters
    ----------
    config : dict, optional
        Configuration dictionary
    dry_run : bool
        If True, return cached/mock data
    """
    
    def __init__(self, config: Optional[dict] = None, dry_run: bool = False):
        super().__init__(config, dry_run)
        self._cache: Dict[str, Any] = {}
    
    def get_metadata(self) -> ToolMetadata:
        """Return tool metadata."""
        return ToolMetadata(
            name="System Information",
            description="Gather detailed system information",
            version="0.3.0",
            requires_admin=False,
            requires_restart=False,
            category="information"
        )
    
    def validate_environment(self) -> None:
        """Validate system info prerequisites."""
        pass
    
    def execute(self) -> bool:
        """Execute default info gathering operation."""
        summary = self.get_system_summary()
        if summary:
            _LOGGER.info("System: %s %s", summary.manufacturer, summary.model)
        return True
    
    def get_system_summary(self) -> Optional[SystemSummary]:
        """Get complete system summary.
        
        Returns
        -------
        SystemSummary, optional
            Complete system information
        """
        _LOGGER.info("Gathering system information...")
        
        try:
            windows = self.get_windows_info()
            cpu = self.get_cpu_info()
            memory = self.get_memory_info()
            gpus = self.get_gpu_info()
            storage = self.get_storage_info()
            network = self.get_network_info()
            bios = self.get_bios_info()
            
            # Get computer/system info
            computer_name = platform.node()
            domain = ""
            manufacturer = ""
            model = ""
            system_type = platform.machine()
            
            if platform.system() == "Windows":
                try:
                    result = subprocess.run(
                        ["powershell", "-NoProfile", "-Command",
                         "Get-CimInstance Win32_ComputerSystem | Select-Object Domain, Manufacturer, Model | ConvertTo-Json"],
                        capture_output=True, text=True, timeout=10
                    )
                    if result.returncode == 0:
                        data = json.loads(result.stdout)
                        domain = data.get("Domain", "")
                        manufacturer = data.get("Manufacturer", "")
                        model = data.get("Model", "")
                except Exception:
                    pass
            
            return SystemSummary(
                computer_name=computer_name,
                domain=domain,
                manufacturer=manufacturer,
                model=model,
                system_type=system_type,
                windows=windows,
                cpu=cpu,
                memory=memory,
                gpus=gpus,
                storage=storage,
                network=network,
                bios=bios
            )
        
        except Exception as exc:
            _LOGGER.error("Failed to gather system info: %s", exc)
            return None
    
    def get_windows_info(self) -> WindowsInfo:
        """Get Windows version information.
        
        Returns
        -------
        WindowsInfo
            Windows information
        """
        version = platform.version()
        build = platform.release()
        edition = ""
        product_id = ""
        install_date = None
        last_boot = None
        uptime = 0.0
        owner = ""
        system_root = os.environ.get("SystemRoot", "C:\\Windows")
        
        if platform.system() == "Windows":
            try:
                ps_script = '''
                $OS = Get-CimInstance Win32_OperatingSystem
                @{
                    Version = $OS.Version
                    Build = $OS.BuildNumber
                    Edition = $OS.Caption
                    ProductId = $OS.SerialNumber
                    InstallDate = $OS.InstallDate.ToString("o")
                    LastBoot = $OS.LastBootUpTime.ToString("o")
                    Owner = $OS.RegisteredUser
                } | ConvertTo-Json
                '''
                
                result = subprocess.run(
                    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                    capture_output=True, text=True, timeout=15
                )
                
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    version = data.get("Version", version)
                    build = data.get("Build", build)
                    edition = data.get("Edition", "")
                    product_id = data.get("ProductId", "")
                    owner = data.get("Owner", "")
                    
                    if data.get("InstallDate"):
                        try:
                            install_date = datetime.fromisoformat(data["InstallDate"].replace("Z", "+00:00"))
                        except ValueError:
                            pass
                    
                    if data.get("LastBoot"):
                        try:
                            last_boot = datetime.fromisoformat(data["LastBoot"].replace("Z", "+00:00"))
                            uptime = (datetime.now(last_boot.tzinfo) - last_boot).total_seconds() / 3600
                        except ValueError:
                            pass
            except Exception:
                pass
        
        return WindowsInfo(
            version=version,
            build=build,
            edition=edition,
            product_id=product_id,
            install_date=install_date,
            last_boot=last_boot,
            uptime_hours=uptime,
            registered_owner=owner,
            system_root=system_root,
            windows_directory=system_root
        )
    
    def get_cpu_info(self) -> CPUInfo:
        """Get CPU information.
        
        Returns
        -------
        CPUInfo
            CPU information
        """
        name = platform.processor() or "Unknown CPU"
        manufacturer = ""
        cores = os.cpu_count() or 1
        logical = cores
        max_clock = 0
        arch = platform.machine()
        usage = 0.0
        
        if platform.system() == "Windows":
            try:
                ps_script = '''
                $CPU = Get-CimInstance Win32_Processor
                @{
                    Name = $CPU.Name
                    Manufacturer = $CPU.Manufacturer
                    Cores = $CPU.NumberOfCores
                    Logical = $CPU.NumberOfLogicalProcessors
                    MaxClock = $CPU.MaxClockSpeed
                    Usage = $CPU.LoadPercentage
                } | ConvertTo-Json
                '''
                
                result = subprocess.run(
                    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                    capture_output=True, text=True, timeout=15
                )
                
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    name = data.get("Name", name).strip()
                    manufacturer = data.get("Manufacturer", "")
                    cores = data.get("Cores", cores)
                    logical = data.get("Logical", logical)
                    max_clock = data.get("MaxClock", 0)
                    usage = float(data.get("Usage", 0) or 0)
            except Exception:
                pass
        
        return CPUInfo(
            name=name,
            manufacturer=manufacturer,
            cores=cores,
            logical_processors=logical,
            max_clock_mhz=max_clock,
            architecture=arch,
            current_usage=usage
        )
    
    def get_memory_info(self) -> MemoryInfo:
        """Get memory information.
        
        Returns
        -------
        MemoryInfo
            Memory information
        """
        total = 0
        available = 0
        used = 0
        usage = 0.0
        slots_used = 0
        slots_total = 0
        speed = 0
        mem_type = ""
        
        if platform.system() == "Windows":
            try:
                ps_script = '''
                $OS = Get-CimInstance Win32_OperatingSystem
                $Mem = Get-CimInstance Win32_PhysicalMemory
                $MemArray = Get-CimInstance Win32_PhysicalMemoryArray
                
                @{
                    Total = $OS.TotalVisibleMemorySize * 1024
                    Available = $OS.FreePhysicalMemory * 1024
                    SlotsUsed = ($Mem | Measure-Object).Count
                    SlotsTotal = $MemArray.MemoryDevices
                    Speed = ($Mem | Select-Object -First 1).Speed
                    Type = ($Mem | Select-Object -First 1).MemoryType
                } | ConvertTo-Json
                '''
                
                result = subprocess.run(
                    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                    capture_output=True, text=True, timeout=15
                )
                
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    total = int(data.get("Total", 0))
                    available = int(data.get("Available", 0))
                    used = total - available
                    usage = (used / total * 100) if total > 0 else 0
                    slots_used = data.get("SlotsUsed", 0)
                    slots_total = data.get("SlotsTotal", 0)
                    speed = data.get("Speed", 0)
                    
                    # Map memory type codes
                    type_map = {24: "DDR3", 26: "DDR4", 30: "DDR5"}
                    mem_type = type_map.get(data.get("Type", 0), "Unknown")
            except Exception:
                pass
        
        return MemoryInfo(
            total_bytes=total,
            available_bytes=available,
            used_bytes=used,
            usage_percent=usage,
            slots_used=slots_used,
            slots_total=slots_total,
            speed_mhz=speed,
            type_name=mem_type
        )
    
    def get_gpu_info(self) -> List[GPUInfo]:
        """Get graphics card information.
        
        Returns
        -------
        List[GPUInfo]
            List of graphics cards
        """
        gpus = []
        
        if platform.system() == "Windows":
            try:
                ps_script = '''
                Get-CimInstance Win32_VideoController | ForEach-Object {
                    @{
                        Name = $_.Name
                        Manufacturer = $_.AdapterCompatibility
                        DriverVersion = $_.DriverVersion
                        DriverDate = if ($_.DriverDate) { $_.DriverDate.ToString("o") } else { $null }
                        VideoMemory = [math]::Round($_.AdapterRAM / 1MB, 0)
                        Resolution = "$($_.CurrentHorizontalResolution)x$($_.CurrentVerticalResolution)"
                    }
                } | ConvertTo-Json
                '''
                
                result = subprocess.run(
                    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                    capture_output=True, text=True, timeout=15
                )
                
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    if not isinstance(data, list):
                        data = [data] if data else []
                    
                    for item in data:
                        driver_date = None
                        if item.get("DriverDate"):
                            try:
                                driver_date = datetime.fromisoformat(item["DriverDate"].replace("Z", "+00:00"))
                            except ValueError:
                                pass
                        
                        gpus.append(GPUInfo(
                            name=item.get("Name", "Unknown"),
                            manufacturer=item.get("Manufacturer", ""),
                            driver_version=item.get("DriverVersion", ""),
                            driver_date=driver_date,
                            video_memory_mb=item.get("VideoMemory", 0),
                            current_resolution=item.get("Resolution", "")
                        ))
            except Exception:
                pass
        
        return gpus
    
    def get_storage_info(self) -> List[StorageInfo]:
        """Get storage device information.
        
        Returns
        -------
        List[StorageInfo]
            List of storage devices
        """
        storage = []
        
        if platform.system() == "Windows":
            try:
                ps_script = '''
                Get-CimInstance Win32_DiskDrive | ForEach-Object {
                    @{
                        Name = $_.DeviceID
                        Model = $_.Model
                        MediaType = $_.MediaType
                        Size = $_.Size
                        Interface = $_.InterfaceType
                        Status = $_.Status
                        Partitions = $_.Partitions
                    }
                } | ConvertTo-Json
                '''
                
                result = subprocess.run(
                    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                    capture_output=True, text=True, timeout=15
                )
                
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    if not isinstance(data, list):
                        data = [data] if data else []
                    
                    for item in data:
                        # Determine media type
                        media_type = item.get("MediaType", "Unknown")
                        model = item.get("Model", "").lower()
                        if "nvme" in model:
                            media_type = "NVMe"
                        elif "ssd" in model or media_type == "Solid state drive":
                            media_type = "SSD"
                        elif media_type in ("Fixed hard disk media", ""):
                            media_type = "HDD"
                        
                        storage.append(StorageInfo(
                            name=item.get("Name", ""),
                            model=item.get("Model", "Unknown"),
                            media_type=media_type,
                            size_bytes=int(item.get("Size", 0) or 0),
                            interface_type=item.get("Interface", ""),
                            status=item.get("Status", ""),
                            partitions=item.get("Partitions", 0)
                        ))
            except Exception:
                pass
        
        return storage
    
    def get_network_info(self) -> List[NetworkAdapterInfo]:
        """Get network adapter information.
        
        Returns
        -------
        List[NetworkAdapterInfo]
            List of network adapters
        """
        adapters = []
        
        if platform.system() == "Windows":
            try:
                ps_script = '''
                Get-NetAdapter | Where-Object { $_.Status -eq 'Up' } | ForEach-Object {
                    $IPConfig = Get-NetIPAddress -InterfaceIndex $_.ifIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue
                    $Gateway = Get-NetRoute -InterfaceIndex $_.ifIndex -DestinationPrefix "0.0.0.0/0" -ErrorAction SilentlyContinue
                    
                    @{
                        Name = $_.Name
                        Description = $_.InterfaceDescription
                        MacAddress = $_.MacAddress
                        Status = $_.Status
                        SpeedMbps = [math]::Round($_.LinkSpeed / 1000000, 0)
                        IPAddresses = @($IPConfig.IPAddress)
                        Gateway = if ($Gateway) { $Gateway.NextHop } else { $null }
                    }
                } | ConvertTo-Json
                '''
                
                result = subprocess.run(
                    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                    capture_output=True, text=True, timeout=15
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    data = json.loads(result.stdout)
                    if not isinstance(data, list):
                        data = [data] if data else []
                    
                    for item in data:
                        adapters.append(NetworkAdapterInfo(
                            name=item.get("Name", ""),
                            description=item.get("Description", ""),
                            mac_address=item.get("MacAddress", ""),
                            connection_status=item.get("Status", ""),
                            speed_mbps=item.get("SpeedMbps", 0),
                            ip_addresses=item.get("IPAddresses", []),
                            gateway=item.get("Gateway")
                        ))
            except Exception:
                pass
        
        return adapters
    
    def get_bios_info(self) -> BIOSInfo:
        """Get BIOS/UEFI information.
        
        Returns
        -------
        BIOSInfo
            BIOS information
        """
        manufacturer = ""
        version = ""
        release_date = None
        serial = ""
        is_uefi = False
        
        if platform.system() == "Windows":
            try:
                # Use raw string to avoid escape sequence warnings
                ps_script = r'''
                $BIOS = Get-CimInstance Win32_BIOS
                @{
                    Manufacturer = $BIOS.Manufacturer
                    Version = $BIOS.SMBIOSBIOSVersion
                    ReleaseDate = if ($BIOS.ReleaseDate) { $BIOS.ReleaseDate.ToString("o") } else { $null }
                    Serial = $BIOS.SerialNumber
                    IsUEFI = (Test-Path "HKLM:\System\CurrentControlSet\Control\SecureBoot\State")
                } | ConvertTo-Json
                '''
                
                result = subprocess.run(
                    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                    capture_output=True, text=True, timeout=15
                )
                
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    manufacturer = data.get("Manufacturer", "")
                    version = data.get("Version", "")
                    serial = data.get("Serial", "")
                    is_uefi = data.get("IsUEFI", False)
                    
                    if data.get("ReleaseDate"):
                        try:
                            release_date = datetime.fromisoformat(data["ReleaseDate"].replace("Z", "+00:00"))
                        except ValueError:
                            pass
            except Exception:
                pass
        
        return BIOSInfo(
            manufacturer=manufacturer,
            version=version,
            release_date=release_date,
            serial_number=serial,
            is_uefi=is_uefi
        )
    
    def export_to_file(self, file_path: str) -> bool:
        """Export system information to a JSON file.
        
        Parameters
        ----------
        file_path : str
            Path to save the file
        
        Returns
        -------
        bool
            True if successful
        """
        summary = self.get_system_summary()
        if not summary:
            return False
        
        try:
            with open(file_path, 'w') as f:
                json.dump(summary.to_dict(), f, indent=2)
            _LOGGER.info("System info exported to %s", file_path)
            return True
        except Exception as exc:
            _LOGGER.error("Failed to export system info: %s", exc)
            return False
    
    def get_quick_summary(self) -> Dict[str, str]:
        """Get a quick human-readable summary.
        
        Returns
        -------
        Dict[str, str]
            Quick summary
        """
        summary = self.get_system_summary()
        if not summary:
            return {}
        
        return {
            "Computer": f"{summary.manufacturer} {summary.model}",
            "Windows": f"{summary.windows.edition} (Build {summary.windows.build})",
            "CPU": summary.cpu.name,
            "RAM": f"{summary.memory.total_gb:.1f} GB ({summary.memory.usage_percent:.0f}% used)",
            "GPU": summary.gpus[0].name if summary.gpus else "Unknown",
            "Storage": f"{len(summary.storage)} drive(s)",
            "Uptime": f"{summary.windows.uptime_hours:.1f} hours"
        }


__all__ = [
    "CPUInfo",
    "MemoryInfo",
    "GPUInfo",
    "StorageInfo",
    "NetworkAdapterInfo",
    "WindowsInfo",
    "BIOSInfo",
    "SystemSummary",
    "SystemInfoManager",
]
