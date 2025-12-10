"""
Advanced System Optimizer Module

Comprehensive Windows optimization including:
- Performance tweaks and tuning
- Service management and optimization
- Startup program management
- Power plan optimization
- Memory and CPU optimization
- Disk optimization
- Network optimization
- Visual effects optimization
- Gaming optimizations
"""

import os
import subprocess
import json
import winreg
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import psutil


class OptimizationLevel(Enum):
    """Optimization presets"""
    CONSERVATIVE = "conservative"  # Minimal changes
    BALANCED = "balanced"  # Moderate optimizations
    AGGRESSIVE = "aggressive"  # Maximum performance
    GAMING = "gaming"  # Gaming-focused
    PRODUCTIVITY = "productivity"  # Work-focused
    BATTERY_SAVER = "battery_saver"  # Laptop battery life


class ServiceStartup(Enum):
    """Service startup types"""
    AUTOMATIC = "Automatic"
    AUTOMATIC_DELAYED = "Automatic (Delayed Start)"
    MANUAL = "Manual"
    DISABLED = "Disabled"


@dataclass
class OptimizationResult:
    """Result of an optimization operation"""
    category: str
    operation: str
    success: bool
    message: str
    reverted: bool = False


@dataclass
class SystemMetrics:
    """Current system performance metrics"""
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    boot_time: str
    running_processes: int
    running_services: int
    startup_programs: int

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'cpu_percent': self.cpu_percent,
            'memory_percent': self.memory_percent,
            'disk_usage_percent': self.disk_usage_percent,
            'boot_time': self.boot_time,
            'running_processes': self.running_processes,
            'running_services': self.running_services,
            'startup_programs': self.startup_programs
        }


class RegistryOptimizer:
    """Optimize Windows through registry tweaks"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.backups: List[Dict] = []

    def _set_registry_value(
        self,
        hive: int,
        key_path: str,
        value_name: str,
        value: any,
        value_type: int
    ) -> bool:
        """Set registry value with backup"""
        try:
            # Backup current value
            try:
                with winreg.OpenKey(hive, key_path, 0, winreg.KEY_READ) as key:
                    old_value, old_type = winreg.QueryValueEx(key, value_name)
                    self.backups.append({
                        'hive': hive,
                        'key_path': key_path,
                        'value_name': value_name,
                        'value': old_value,
                        'type': old_type
                    })
            except:
                pass

            # Set new value
            with winreg.CreateKey(hive, key_path) as key:
                winreg.SetValueEx(key, value_name, 0, value_type, value)

            return True
        except Exception as e:
            if self.verbose:
                print(f"Error setting registry value: {e}")
            return False

    def optimize_visual_effects(self, level: OptimizationLevel) -> List[OptimizationResult]:
        """Optimize visual effects for performance"""
        results = []

        # Disable animations based on level
        if level in [OptimizationLevel.AGGRESSIVE, OptimizationLevel.GAMING]:
            tweaks = [
                (r"Control Panel\Desktop", "UserPreferencesMask", bytes([0x90, 0x12, 0x03, 0x80, 0x10, 0x00, 0x00, 0x00]), winreg.REG_BINARY),
                (r"Control Panel\Desktop\WindowMetrics", "MinAnimate", "0", winreg.REG_SZ),
                (r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects", "VisualFXSetting", 2, winreg.REG_DWORD),
            ]

            for key_path, value_name, value, value_type in tweaks:
                success = self._set_registry_value(
                    winreg.HKEY_CURRENT_USER,
                    key_path,
                    value_name,
                    value,
                    value_type
                )
                results.append(OptimizationResult(
                    category="Visual Effects",
                    operation=f"Set {value_name}",
                    success=success,
                    message="Disabled animations" if success else "Failed"
                ))

        return results

    def optimize_system_responsiveness(self) -> List[OptimizationResult]:
        """Optimize system responsiveness"""
        results = []

        tweaks = [
            # Reduce menu show delay
            (winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop", "MenuShowDelay", "0", winreg.REG_SZ),
            # Disable program compatibility assistant
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\AppCompat", "DisablePCA", 1, winreg.REG_DWORD),
            # Optimize foreground lock timeout
            (winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop", "ForegroundLockTimeout", 0, winreg.REG_DWORD),
        ]

        for hive, key_path, value_name, value, value_type in tweaks:
            success = self._set_registry_value(hive, key_path, value_name, value, value_type)
            results.append(OptimizationResult(
                category="System Responsiveness",
                operation=f"Set {value_name}",
                success=success,
                message="Optimized" if success else "Failed"
            ))

        return results

    def optimize_gaming(self) -> List[OptimizationResult]:
        """Gaming-specific optimizations"""
        results = []

        tweaks = [
            # Enable Game Mode
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\GameBar", "AutoGameModeEnabled", 1, winreg.REG_DWORD),
            # Disable fullscreen optimizations
            (winreg.HKEY_CURRENT_USER, r"System\GameConfigStore", "GameDVR_FSEBehaviorMode", 2, winreg.REG_DWORD),
            # Disable Game DVR
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\GameDVR", "AppCaptureEnabled", 0, winreg.REG_DWORD),
        ]

        for hive, key_path, value_name, value, value_type in tweaks:
            success = self._set_registry_value(hive, key_path, value_name, value, value_type)
            results.append(OptimizationResult(
                category="Gaming",
                operation=f"Set {value_name}",
                success=success,
                message="Optimized" if success else "Failed"
            ))

        return results

    def disable_telemetry(self, aggressive: bool = False) -> List[OptimizationResult]:
        """Disable Windows telemetry"""
        results = []

        tweaks = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\DataCollection", "AllowTelemetry", 0, winreg.REG_DWORD),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection", "AllowTelemetry", 0, winreg.REG_DWORD),
        ]

        if aggressive:
            tweaks.extend([
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\DataCollection", "AllowDeviceNameInTelemetry", 0, winreg.REG_DWORD),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\AppCompat", "AITEnable", 0, winreg.REG_DWORD),
            ])

        for hive, key_path, value_name, value, value_type in tweaks:
            success = self._set_registry_value(hive, key_path, value_name, value, value_type)
            results.append(OptimizationResult(
                category="Privacy",
                operation=f"Disable {value_name}",
                success=success,
                message="Disabled" if success else "Failed"
            ))

        return results


class ServiceOptimizer:
    """Optimize Windows services"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

        # Services safe to disable for performance
        self.safe_to_disable = {
            OptimizationLevel.CONSERVATIVE: [
                "DiagTrack",  # Connected User Experiences and Telemetry
                "dmwappushservice",  # Device Management Wireless Application Protocol
            ],
            OptimizationLevel.BALANCED: [
                "DiagTrack",
                "dmwappushservice",
                "SysMain",  # Superfetch
                "WSearch",  # Windows Search (if not needed)
            ],
            OptimizationLevel.AGGRESSIVE: [
                "DiagTrack",
                "dmwappushservice",
                "SysMain",
                "WSearch",
                "TabletInputService",
                "PrintSpooler",  # If no printer
                "Fax",
                "RemoteRegistry",
            ]
        }

    def _run_powershell(self, script: str) -> subprocess.CompletedProcess:
        """Execute PowerShell script"""
        return subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-Command", script],
            capture_output=True,
            text=True
        )

    def set_service_startup(self, service_name: str, startup_type: ServiceStartup) -> bool:
        """Set service startup type"""
        ps_script = f"""
        try {{
            Set-Service -Name '{service_name}' -StartupType {startup_type.value.split()[0]}
            $true
        }} catch {{
            $false
        }}
        """

        result = self._run_powershell(ps_script)
        return result.stdout.strip().lower() == "true"

    def disable_service(self, service_name: str) -> bool:
        """Disable a Windows service"""
        return self.set_service_startup(service_name, ServiceStartup.DISABLED)

    def optimize_services(self, level: OptimizationLevel) -> List[OptimizationResult]:
        """Optimize services based on level"""
        results = []

        services_to_disable = self.safe_to_disable.get(level, [])

        for service in services_to_disable:
            success = self.disable_service(service)
            results.append(OptimizationResult(
                category="Services",
                operation=f"Disable {service}",
                success=success,
                message=f"Disabled {service}" if success else f"Failed to disable {service}"
            ))

        return results

    def list_services(self) -> List[Dict]:
        """List all Windows services"""
        ps_script = """
        Get-Service | ForEach-Object {
            [PSCustomObject]@{
                Name = $_.Name
                DisplayName = $_.DisplayName
                Status = $_.Status.ToString()
                StartType = $_.StartType.ToString()
            }
        } | ConvertTo-Json
        """

        result = self._run_powershell(ps_script)

        try:
            data = json.loads(result.stdout)
            if isinstance(data, dict):
                data = [data]
            return data
        except:
            return []


class StartupOptimizer:
    """Manage startup programs"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def _run_powershell(self, script: str) -> subprocess.CompletedProcess:
        """Execute PowerShell script"""
        return subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-Command", script],
            capture_output=True,
            text=True
        )

    def list_startup_programs(self) -> List[Dict]:
        """List all startup programs"""
        ps_script = """
        Get-CimInstance Win32_StartupCommand | ForEach-Object {
            [PSCustomObject]@{
                Name = $_.Name
                Command = $_.Command
                Location = $_.Location
                User = $_.User
            }
        } | ConvertTo-Json
        """

        result = self._run_powershell(ps_script)

        try:
            data = json.loads(result.stdout)
            if isinstance(data, dict):
                data = [data]
            return data
        except:
            return []

    def disable_startup_program(self, name: str) -> bool:
        """Disable a startup program"""
        # This requires editing registry and startup folders
        # Simplified implementation
        common_startup_paths = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce",
        ]

        for key_path in common_startup_paths:
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS) as key:
                    try:
                        winreg.DeleteValue(key, name)
                        return True
                    except:
                        pass
            except:
                pass

        return False


class DiskOptimizer:
    """Optimize disk performance"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def defragment_drive(self, drive: str) -> bool:
        """Defragment a drive"""
        result = subprocess.run(
            ["defrag", drive, "/O"],
            capture_output=True
        )
        return result.returncode == 0

    def optimize_ssd(self, drive: str) -> bool:
        """Optimize SSD (TRIM)"""
        result = subprocess.run(
            ["defrag", drive, "/L"],
            capture_output=True
        )
        return result.returncode == 0

    def clean_temp_files(self) -> int:
        """Clean temporary files"""
        import shutil

        temp_dirs = [
            os.environ.get('TEMP', ''),
            os.environ.get('TMP', ''),
            r"C:\Windows\Temp",
        ]

        cleaned_bytes = 0

        for temp_dir in temp_dirs:
            if os.path.exists(temp_dir):
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        try:
                            file_path = os.path.join(root, file)
                            file_size = os.path.getsize(file_path)
                            os.remove(file_path)
                            cleaned_bytes += file_size
                        except:
                            pass

        return cleaned_bytes

    def run_disk_cleanup(self) -> bool:
        """Run Windows Disk Cleanup utility"""
        result = subprocess.run(
            ["cleanmgr", "/sagerun:1"],
            capture_output=True
        )
        return result.returncode == 0


class PowerOptimizer:
    """Optimize power settings"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def set_power_plan(self, plan: str) -> bool:
        """Set Windows power plan"""
        # High Performance GUID
        plans = {
            "high_performance": "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c",
            "balanced": "381b4222-f694-41f0-9685-ff5bb260df2e",
            "power_saver": "a1841308-3541-4fab-bc81-f71556f20b4a",
            "ultimate_performance": "e9a42b02-d5df-448d-aa00-03f14749eb61"
        }

        guid = plans.get(plan.lower())
        if not guid:
            return False

        result = subprocess.run(
            ["powercfg", "/setactive", guid],
            capture_output=True
        )

        return result.returncode == 0

    def disable_hibernation(self) -> bool:
        """Disable hibernation"""
        result = subprocess.run(
            ["powercfg", "/hibernate", "off"],
            capture_output=True
        )
        return result.returncode == 0

    def disable_fast_startup(self) -> bool:
        """Disable fast startup"""
        try:
            key_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Power"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, "HiberbootEnabled", 0, winreg.REG_DWORD, 0)
            return True
        except:
            return False


class SystemOptimizer:
    """Comprehensive system optimizer"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.registry_optimizer = RegistryOptimizer(verbose)
        self.service_optimizer = ServiceOptimizer(verbose)
        self.startup_optimizer = StartupOptimizer(verbose)
        self.disk_optimizer = DiskOptimizer(verbose)
        self.power_optimizer = PowerOptimizer(verbose)

    def get_system_metrics(self) -> SystemMetrics:
        """Get current system performance metrics"""
        import psutil
        from datetime import datetime

        boot_time = datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")

        return SystemMetrics(
            cpu_percent=psutil.cpu_percent(interval=1),
            memory_percent=psutil.virtual_memory().percent,
            disk_usage_percent=psutil.disk_usage('/').percent,
            boot_time=boot_time,
            running_processes=len(psutil.pids()),
            running_services=len(self.service_optimizer.list_services()),
            startup_programs=len(self.startup_optimizer.list_startup_programs())
        )

    def optimize_system(self, level: OptimizationLevel) -> List[OptimizationResult]:
        """Perform comprehensive system optimization"""
        results = []

        # Visual effects
        results.extend(self.registry_optimizer.optimize_visual_effects(level))

        # System responsiveness
        results.extend(self.registry_optimizer.optimize_system_responsiveness())

        # Services
        results.extend(self.service_optimizer.optimize_services(level))

        # Gaming optimizations
        if level == OptimizationLevel.GAMING:
            results.extend(self.registry_optimizer.optimize_gaming())

        # Power settings
        if level in [OptimizationLevel.AGGRESSIVE, OptimizationLevel.GAMING]:
            power_success = self.power_optimizer.set_power_plan("high_performance")
            results.append(OptimizationResult(
                category="Power",
                operation="Set High Performance plan",
                success=power_success,
                message="Enabled" if power_success else "Failed"
            ))

        return results

    def optimize_for_gaming(self) -> List[OptimizationResult]:
        """Quick gaming optimization"""
        return self.optimize_system(OptimizationLevel.GAMING)

    def optimize_for_productivity(self) -> List[OptimizationResult]:
        """Quick productivity optimization"""
        return self.optimize_system(OptimizationLevel.PRODUCTIVITY)

    def clean_system(self) -> Dict[str, any]:
        """Clean system files and optimize disk"""
        results = {
            'temp_files_cleaned': self.disk_optimizer.clean_temp_files(),
            'disk_cleanup_success': self.disk_optimizer.run_disk_cleanup()
        }

        return results


# Convenience functions
def optimize_for_gaming() -> List[OptimizationResult]:
    """Quick gaming optimization"""
    optimizer = SystemOptimizer()
    return optimizer.optimize_for_gaming()


def optimize_for_productivity() -> List[OptimizationResult]:
    """Quick productivity optimization"""
    optimizer = SystemOptimizer()
    return optimizer.optimize_for_productivity()


def get_system_health() -> SystemMetrics:
    """Quick system health check"""
    optimizer = SystemOptimizer()
    return optimizer.get_system_metrics()


def clean_system() -> Dict:
    """Quick system cleanup"""
    optimizer = SystemOptimizer()
    return optimizer.clean_system()
