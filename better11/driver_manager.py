"""
Driver Manager Module

Comprehensive driver management for Windows:
- Enumerate installed drivers
- Download drivers from manufacturer websites
- Install drivers to live system
- Inject drivers into offline images
- Backup and restore drivers
- Update outdated drivers
- Integrate with major driver databases
"""

import os
import subprocess
import json
import shutil
import tempfile
import requests
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import re
import zipfile


class DriverClass(Enum):
    """Driver device classes"""
    DISPLAY = "Display"
    NETWORK = "Net"
    AUDIO = "Media"
    STORAGE = "HDC"
    USB = "USB"
    BLUETOOTH = "Bluetooth"
    SYSTEM = "System"
    CHIPSET = "Chipset"
    OTHER = "Other"


class DriverStatus(Enum):
    """Driver installation status"""
    INSTALLED = "Installed"
    NOT_INSTALLED = "Not Installed"
    UPDATE_AVAILABLE = "Update Available"
    CORRUPTED = "Corrupted"
    DISABLED = "Disabled"


@dataclass
class Driver:
    """Represents a Windows driver"""
    class_name: str
    device_name: str
    driver_provider: str
    driver_version: str
    driver_date: str
    inf_name: str
    inf_path: Optional[str] = None
    hardware_id: Optional[str] = None
    status: DriverStatus = DriverStatus.INSTALLED
    is_signed: bool = True
    is_inbox: bool = False
    size: int = 0

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'class_name': self.class_name,
            'device_name': self.device_name,
            'driver_provider': self.driver_provider,
            'driver_version': self.driver_version,
            'driver_date': self.driver_date,
            'inf_name': self.inf_name,
            'inf_path': self.inf_path,
            'hardware_id': self.hardware_id,
            'status': self.status.value,
            'is_signed': self.is_signed,
            'is_inbox': self.is_inbox,
            'size': self.size
        }


@dataclass
class DriverPackage:
    """Represents a driver package"""
    name: str
    version: str
    manufacturer: str
    package_path: str
    inf_files: List[str] = field(default_factory=list)
    size: int = 0
    description: str = ""
    supported_hardware: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'version': self.version,
            'manufacturer': self.manufacturer,
            'package_path': self.package_path,
            'inf_files': self.inf_files,
            'size': self.size,
            'description': self.description,
            'supported_hardware': self.supported_hardware
        }


class DriverEnumerator:
    """Enumerate and query installed drivers"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def _run_powershell(self, script: str, check: bool = True) -> subprocess.CompletedProcess:
        """Execute PowerShell script"""
        if self.verbose:
            print(f"Executing PowerShell:\n{script}")

        result = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-Command", script],
            capture_output=True,
            text=True,
            check=False
        )

        if check and result.returncode != 0:
            raise RuntimeError(f"PowerShell script failed: {result.stderr}")

        return result

    def list_installed_drivers(self, class_filter: Optional[str] = None) -> List[Driver]:
        """List all installed drivers"""
        ps_script = """
        $drivers = Get-WindowsDriver -Online

        $drivers | ForEach-Object {
            [PSCustomObject]@{
                ClassName = $_.ClassName
                DeviceName = $_.ProviderName
                DriverProvider = $_.ProviderName
                DriverVersion = $_.Version
                DriverDate = $_.Date.ToString("yyyy-MM-dd")
                InfName = $_.OriginalFileName
                InfPath = $_.DriverPath
                IsSigned = $_.DriverSignature -eq "Signed"
                IsInbox = $_.InBox
            }
        } | ConvertTo-Json
        """

        result = self._run_powershell(ps_script, check=False)

        if not result.stdout.strip():
            return []

        try:
            data = json.loads(result.stdout)
            if isinstance(data, dict):
                data = [data]

            drivers = []
            for item in data:
                if class_filter and item.get('ClassName', '').lower() != class_filter.lower():
                    continue

                driver = Driver(
                    class_name=item.get('ClassName', 'Unknown'),
                    device_name=item.get('DeviceName', 'Unknown'),
                    driver_provider=item.get('DriverProvider', 'Unknown'),
                    driver_version=item.get('DriverVersion', '0.0.0.0'),
                    driver_date=item.get('DriverDate', ''),
                    inf_name=item.get('InfName', ''),
                    inf_path=item.get('InfPath'),
                    is_signed=item.get('IsSigned', False),
                    is_inbox=item.get('IsInbox', False)
                )
                drivers.append(driver)

            return drivers
        except json.JSONDecodeError:
            return []

    def list_devices(self, include_hidden: bool = False) -> List[Dict]:
        """List all devices in Device Manager"""
        ps_script = f"""
        $devices = Get-PnpDevice {"-PresentOnly" if not include_hidden else ""}

        $devices | ForEach-Object {{
            [PSCustomObject]@{{
                FriendlyName = $_.FriendlyName
                InstanceId = $_.InstanceId
                Class = $_.Class
                Status = $_.Status
                Manufacturer = $_.Manufacturer
                DriverVersion = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName "DEVPKEY_Device_DriverVersion" -ErrorAction SilentlyContinue).Data
            }}
        }} | ConvertTo-Json
        """

        result = self._run_powershell(ps_script, check=False)

        if not result.stdout.strip():
            return []

        try:
            data = json.loads(result.stdout)
            if isinstance(data, dict):
                data = [data]
            return data
        except:
            return []

    def get_driver_store_packages(self) -> List[DriverPackage]:
        """Get drivers from the driver store"""
        ps_script = """
        $packages = pnputil /enum-drivers

        # Parse pnputil output
        # This is a simplified version - actual implementation would parse the output
        $packages
        """

        result = self._run_powershell(ps_script, check=False)

        # Placeholder - actual implementation would parse pnputil output
        return []

    def get_missing_drivers(self) -> List[Dict]:
        """Find devices with missing or problematic drivers"""
        ps_script = """
        Get-PnpDevice -Status Error,Degraded,Unknown | ForEach-Object {
            [PSCustomObject]@{
                Name = $_.FriendlyName
                InstanceId = $_.InstanceId
                Class = $_.Class
                Status = $_.Status
                Problem = $_.Problem
                HardwareId = (Get-PnpDeviceProperty -InstanceId $_.InstanceId -KeyName "DEVPKEY_Device_HardwareIds").Data[0]
            }
        } | ConvertTo-Json
        """

        result = self._run_powershell(ps_script, check=False)

        if not result.stdout.strip():
            return []

        try:
            data = json.loads(result.stdout)
            if isinstance(data, dict):
                data = [data]
            return data
        except:
            return []


class DriverInstaller:
    """Install and manage drivers on live system"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def _run_command(self, cmd: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Execute command"""
        if self.verbose:
            print(f"Executing: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )

        if check and result.returncode != 0:
            raise RuntimeError(f"Command failed: {result.stderr}")

        return result

    def install_driver(
        self,
        inf_path: str,
        force: bool = False,
        install_subdir: bool = True
    ) -> bool:
        """Install a driver using pnputil"""
        cmd = ["pnputil", "/add-driver", inf_path]

        if install_subdir:
            cmd.append("/subdirs")

        if force:
            cmd.append("/install")

        result = self._run_command(cmd, check=False)
        return result.returncode == 0

    def uninstall_driver(self, inf_name: str, force: bool = False) -> bool:
        """Uninstall a driver from driver store"""
        cmd = ["pnputil", "/delete-driver", inf_name]

        if force:
            cmd.append("/force")

        result = self._run_command(cmd, check=False)
        return result.returncode == 0

    def update_driver(self, device_instance_id: str, inf_path: str) -> bool:
        """Update driver for a specific device"""
        ps_script = f"""
        $device = Get-PnpDevice -InstanceId '{device_instance_id}'
        if ($device) {{
            pnputil /add-driver "{inf_path}" /install
            $devcon = "$env:SystemRoot\\System32\\pnputil.exe"
            Update-PnpDriver -InstanceId '{device_instance_id}' -DriverPath "{inf_path}"
            $?
        }} else {{
            $false
        }}
        """

        result = subprocess.run(
            ["powershell", "-Command", ps_script],
            capture_output=True,
            text=True
        )

        return result.returncode == 0

    def install_driver_package(self, package_path: str) -> Tuple[int, int]:
        """
        Install all drivers from a package/folder

        Returns:
            (success_count, fail_count)
        """
        success = 0
        fail = 0

        # Find all INF files
        inf_files = list(Path(package_path).rglob("*.inf"))

        for inf_file in inf_files:
            if self.install_driver(str(inf_file), force=True):
                success += 1
            else:
                fail += 1

        return (success, fail)

    def scan_hardware_changes(self) -> bool:
        """Trigger hardware scan to detect new devices"""
        ps_script = """
        $devcon = "$env:SystemRoot\\System32\\pnputil.exe"
        pnputil /scan-devices
        $?
        """

        result = subprocess.run(
            ["powershell", "-Command", ps_script],
            capture_output=True
        )

        return result.returncode == 0


class DriverDownloader:
    """Download drivers from various sources"""

    def __init__(self, download_dir: Optional[str] = None):
        self.download_dir = download_dir or os.path.join(tempfile.gettempdir(), "drivers")
        os.makedirs(self.download_dir, exist_ok=True)
        self.session = requests.Session()

    def download_from_url(
        self,
        url: str,
        output_path: Optional[str] = None,
        progress_callback=None
    ) -> str:
        """Download driver package from URL"""
        if output_path is None:
            filename = os.path.basename(url)
            output_path = os.path.join(self.download_dir, filename)

        response = self.session.get(url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0

        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback:
                        progress_callback(downloaded, total_size)

        return output_path

    def extract_driver_package(self, package_path: str, extract_path: Optional[str] = None) -> str:
        """Extract driver package (ZIP, CAB, EXE)"""
        if extract_path is None:
            extract_path = os.path.join(
                self.download_dir,
                f"extracted_{os.path.basename(package_path)}"
            )

        os.makedirs(extract_path, exist_ok=True)

        # Handle ZIP files
        if package_path.lower().endswith('.zip'):
            with zipfile.ZipFile(package_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            return extract_path

        # Handle CAB files
        if package_path.lower().endswith('.cab'):
            subprocess.run(
                ["expand", package_path, "-F:*", extract_path],
                check=True
            )
            return extract_path

        # Handle self-extracting EXEs
        if package_path.lower().endswith('.exe'):
            # Try common silent extraction switches
            extract_switches = [
                [package_path, "/s", f"/e:{extract_path}"],
                [package_path, "-s", f"-d{extract_path}"],
                [package_path, "/silent", f"/extract:{extract_path}"],
                [package_path, "-y", f"-o{extract_path}"]
            ]

            for switches in extract_switches:
                result = subprocess.run(switches, capture_output=True)
                if result.returncode == 0 and os.listdir(extract_path):
                    return extract_path

        return extract_path

    def download_intel_driver(self, device_id: str) -> Optional[str]:
        """Download driver from Intel Download Center"""
        # This would integrate with Intel's driver API
        # Placeholder implementation
        raise NotImplementedError("Intel driver download not yet implemented")

    def download_nvidia_driver(self, gpu_id: str) -> Optional[str]:
        """Download driver from NVIDIA"""
        # This would integrate with NVIDIA's driver API
        # Placeholder implementation
        raise NotImplementedError("NVIDIA driver download not yet implemented")

    def download_amd_driver(self, gpu_id: str) -> Optional[str]:
        """Download driver from AMD"""
        # This would integrate with AMD's driver API
        # Placeholder implementation
        raise NotImplementedError("AMD driver download not yet implemented")


class DriverBackup:
    """Backup and restore drivers"""

    def __init__(self, backup_dir: Optional[str] = None):
        self.backup_dir = backup_dir or os.path.join(os.path.expanduser("~"), "DriverBackup")
        os.makedirs(self.backup_dir, exist_ok=True)

    def backup_drivers(self, include_inbox: bool = False) -> Tuple[int, str]:
        """
        Backup all third-party drivers

        Returns:
            (driver_count, backup_path)
        """
        backup_path = os.path.join(
            self.backup_dir,
            f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        os.makedirs(backup_path, exist_ok=True)

        ps_script = f"""
        $drivers = Get-WindowsDriver -Online
        $count = 0

        foreach ($driver in $drivers) {{
            if ({str(include_inbox).lower()} -or -not $driver.InBox) {{
                $destPath = Join-Path '{backup_path}' $driver.OriginalFileName
                $destDir = Split-Path $destPath
                if (-not (Test-Path $destDir)) {{
                    New-Item -ItemType Directory -Path $destDir -Force | Out-Null
                }}

                Export-WindowsDriver -Online -Destination '{backup_path}' -Driver $driver.Driver
                $count++
            }}
        }}

        $count
        """

        result = subprocess.run(
            ["powershell", "-Command", ps_script],
            capture_output=True,
            text=True
        )

        try:
            count = int(result.stdout.strip())
        except:
            count = 0

        return (count, backup_path)

    def restore_drivers(self, backup_path: str) -> Tuple[int, int]:
        """
        Restore drivers from backup

        Returns:
            (success_count, fail_count)
        """
        installer = DriverInstaller()
        return installer.install_driver_package(backup_path)


class DriverInjector:
    """Inject drivers into offline Windows images"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.dism_path = self._find_dism()

    def _find_dism(self) -> str:
        """Locate DISM executable"""
        dism = r"C:\Windows\System32\dism.exe"
        if os.path.exists(dism):
            return dism

        dism_path = shutil.which("dism.exe")
        if dism_path:
            return dism_path

        raise FileNotFoundError("DISM.exe not found")

    def inject_drivers(
        self,
        image_path: str,
        driver_path: str,
        recurse: bool = True,
        force_unsigned: bool = False
    ) -> bool:
        """Inject drivers into mounted image or WIM file"""
        cmd = [
            self.dism_path,
            f"/Image:{image_path}",
            "/Add-Driver",
            f"/Driver:{driver_path}"
        ]

        if recurse:
            cmd.append("/Recurse")

        if force_unsigned:
            cmd.append("/ForceUnsigned")

        if self.verbose:
            print(f"Executing: {' '.join(cmd)}")

        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0

    def list_drivers_in_image(self, image_path: str) -> List[Driver]:
        """List drivers in offline image"""
        cmd = [
            self.dism_path,
            f"/Image:{image_path}",
            "/Get-Drivers"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        # Parse DISM output
        drivers = []
        # Placeholder - actual implementation would parse output
        return drivers


class DriverManager:
    """High-level driver management"""

    def __init__(self, work_dir: Optional[str] = None, verbose: bool = False):
        self.work_dir = work_dir or tempfile.gettempdir()
        self.verbose = verbose
        self.enumerator = DriverEnumerator(verbose)
        self.installer = DriverInstaller(verbose)
        self.downloader = DriverDownloader(os.path.join(self.work_dir, "drivers"))
        self.backup = DriverBackup()
        self.injector = DriverInjector(verbose)

    def get_all_drivers(self) -> List[Driver]:
        """Get all installed drivers"""
        return self.enumerator.list_installed_drivers()

    def get_missing_drivers(self) -> List[Dict]:
        """Find devices missing drivers"""
        return self.enumerator.get_missing_drivers()

    def backup_all_drivers(self) -> Tuple[int, str]:
        """Backup all drivers"""
        return self.backup.backup_drivers()

    def install_driver_from_package(self, package_path: str) -> Tuple[int, int]:
        """Install drivers from package"""
        # Extract if needed
        if package_path.lower().endswith(('.zip', '.cab', '.exe')):
            extract_path = self.downloader.extract_driver_package(package_path)
            package_path = extract_path

        return self.installer.install_driver_package(package_path)

    def inject_drivers_to_image(
        self,
        image_path: str,
        driver_path: str
    ) -> bool:
        """Inject drivers into offline image"""
        return self.injector.inject_drivers(image_path, driver_path)


# Convenience functions
def list_drivers() -> List[Driver]:
    """Quick list all drivers"""
    manager = DriverManager()
    return manager.get_all_drivers()


def backup_drivers() -> Tuple[int, str]:
    """Quick backup drivers"""
    manager = DriverManager()
    return manager.backup_all_drivers()


def install_driver(driver_path: str) -> bool:
    """Quick install driver"""
    installer = DriverInstaller()
    return installer.install_driver(driver_path, force=True)


def find_missing_drivers() -> List[Dict]:
    """Quick find missing drivers"""
    enumerator = DriverEnumerator()
    return enumerator.get_missing_drivers()


# Fix import
from datetime import datetime
