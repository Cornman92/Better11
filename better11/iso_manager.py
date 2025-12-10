"""
ISO Download and USB Creation Module

Provides tools for:
- Downloading Windows ISOs from official sources
- Creating bootable USB drives
- Verifying ISO integrity
- Managing installation media
"""

import os
import re
import hashlib
import requests
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import tempfile
import urllib.parse


class WindowsEdition(Enum):
    """Windows editions available for download"""
    WINDOWS_11_HOME = "Windows 11 Home"
    WINDOWS_11_PRO = "Windows 11 Pro"
    WINDOWS_11_EDUCATION = "Windows 11 Education"
    WINDOWS_11_ENTERPRISE = "Windows 11 Enterprise"
    WINDOWS_10_HOME = "Windows 10 Home"
    WINDOWS_10_PRO = "Windows 10 Pro"
    WINDOWS_SERVER_2022 = "Windows Server 2022"


class Architecture(Enum):
    """System architectures"""
    X64 = "x64"
    X86 = "x86"
    ARM64 = "arm64"


@dataclass
class ISOInfo:
    """Information about a Windows ISO"""
    name: str
    edition: str
    version: str
    build: str
    architecture: Architecture
    language: str
    size: int
    download_url: str
    sha256: Optional[str] = None
    release_date: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'edition': self.edition,
            'version': self.version,
            'build': self.build,
            'architecture': self.architecture.value,
            'language': self.language,
            'size': self.size,
            'download_url': self.download_url,
            'sha256': self.sha256,
            'release_date': self.release_date
        }


@dataclass
class USBDevice:
    """Represents a USB storage device"""
    device_id: str
    name: str
    size: int
    drive_letter: Optional[str]
    removable: bool
    is_bootable: bool = False

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'device_id': self.device_id,
            'name': self.name,
            'size': self.size,
            'drive_letter': self.drive_letter,
            'removable': self.removable,
            'is_bootable': self.is_bootable
        }


class ISODownloader:
    """Download Windows ISOs from official sources"""

    def __init__(self, download_dir: Optional[str] = None):
        self.download_dir = download_dir or os.path.join(tempfile.gettempdir(), "iso_downloads")
        os.makedirs(self.download_dir, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def get_available_windows_versions(self) -> List[Dict[str, str]]:
        """Get available Windows versions for download"""
        # This would integrate with Microsoft's download API or web scraping
        # For now, return a curated list
        return [
            {
                'id': 'win11_22h2',
                'name': 'Windows 11 22H2',
                'version': '22H2',
                'build': '22621'
            },
            {
                'id': 'win11_23h2',
                'name': 'Windows 11 23H2',
                'version': '23H2',
                'build': '22631'
            },
            {
                'id': 'win10_22h2',
                'name': 'Windows 10 22H2',
                'version': '22H2',
                'build': '19045'
            }
        ]

    def get_download_links(
        self,
        version_id: str,
        edition: str = "Professional",
        language: str = "en-US",
        architecture: Architecture = Architecture.X64
    ) -> List[ISOInfo]:
        """Get download links for a specific Windows version"""
        # This would use the Microsoft Software Download API
        # For demonstration, return placeholder data
        iso_info = ISOInfo(
            name=f"Windows 11 {edition} {architecture.value}",
            edition=edition,
            version="23H2",
            build="22631",
            architecture=architecture,
            language=language,
            size=5_000_000_000,  # ~5GB
            download_url="https://example.com/windows11.iso",
            sha256="placeholder_hash",
            release_date="2024-01-01"
        )
        return [iso_info]

    def download_iso(
        self,
        iso_info: ISOInfo,
        output_path: Optional[str] = None,
        progress_callback=None,
        verify_hash: bool = True
    ) -> str:
        """
        Download a Windows ISO

        Args:
            iso_info: ISO information including download URL
            output_path: Where to save the ISO
            progress_callback: Function to call with (bytes_downloaded, total_bytes)
            verify_hash: Whether to verify SHA256 hash after download

        Returns:
            Path to downloaded ISO
        """
        if output_path is None:
            filename = self._get_filename_from_url(iso_info.download_url)
            output_path = os.path.join(self.download_dir, filename)

        # Download with progress tracking
        response = self.session.get(iso_info.download_url, stream=True)
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

        # Verify hash if provided
        if verify_hash and iso_info.sha256:
            if not self.verify_iso_hash(output_path, iso_info.sha256):
                os.remove(output_path)
                raise ValueError("ISO hash verification failed!")

        return output_path

    def _get_filename_from_url(self, url: str) -> str:
        """Extract filename from URL"""
        parsed = urllib.parse.urlparse(url)
        filename = os.path.basename(parsed.path)
        if not filename:
            filename = "windows.iso"
        return filename

    def verify_iso_hash(self, iso_path: str, expected_hash: str) -> bool:
        """Verify ISO file hash"""
        sha256_hash = hashlib.sha256()

        with open(iso_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)

        calculated_hash = sha256_hash.hexdigest()
        return calculated_hash.lower() == expected_hash.lower()

    def get_iso_info_from_file(self, iso_path: str) -> Dict:
        """Get information from an ISO file"""
        info = {
            'path': iso_path,
            'size': os.path.getsize(iso_path),
            'filename': os.path.basename(iso_path)
        }

        # Calculate hash
        info['sha256'] = self._calculate_file_hash(iso_path)

        return info

    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of file"""
        sha256_hash = hashlib.sha256()

        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)

        return sha256_hash.hexdigest()


class USBBootCreator:
    """Create bootable USB drives from Windows ISOs"""

    def __init__(self):
        self.diskpart_script_path = None

    def list_usb_devices(self) -> List[USBDevice]:
        """List all removable USB devices"""
        devices = []

        # Use PowerShell to get USB devices
        ps_script = """
        Get-Disk | Where-Object {$_.BusType -eq 'USB'} | ForEach-Object {
            $disk = $_
            $partition = Get-Partition -DiskNumber $disk.Number -ErrorAction SilentlyContinue | Select-Object -First 1
            $volume = if ($partition) { Get-Volume -Partition $partition -ErrorAction SilentlyContinue } else { $null }

            [PSCustomObject]@{
                DeviceId = $disk.Number
                Name = $disk.FriendlyName
                Size = $disk.Size
                DriveLetter = if ($volume) { $volume.DriveLetter } else { $null }
                Removable = $true
            }
        } | ConvertTo-Json
        """

        try:
            result = subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True,
                text=True,
                check=True
            )

            if result.stdout.strip():
                data = json.loads(result.stdout)
                if isinstance(data, dict):
                    data = [data]

                for item in data:
                    devices.append(USBDevice(
                        device_id=str(item['DeviceId']),
                        name=item['Name'],
                        size=item['Size'],
                        drive_letter=item.get('DriveLetter'),
                        removable=item['Removable']
                    ))
        except Exception as e:
            print(f"Error listing USB devices: {e}")

        return devices

    def format_usb(
        self,
        device: USBDevice,
        filesystem: str = "NTFS",
        label: str = "WINDOWS11",
        quick: bool = True
    ) -> bool:
        """
        Format USB drive

        Args:
            device: USB device to format
            filesystem: FAT32 or NTFS
            label: Volume label
            quick: Quick format

        Returns:
            True if successful
        """
        if not device.removable:
            raise ValueError("Device is not removable!")

        # Create DiskPart script
        script = f"""
select disk {device.device_id}
clean
create partition primary
select partition 1
active
format fs={filesystem} label="{label}" {'quick' if quick else ''}
assign
exit
"""

        script_path = os.path.join(tempfile.gettempdir(), "diskpart_script.txt")
        with open(script_path, 'w') as f:
            f.write(script)

        try:
            # Run DiskPart
            result = subprocess.run(
                ["diskpart", "/s", script_path],
                capture_output=True,
                text=True
            )

            return result.returncode == 0
        finally:
            if os.path.exists(script_path):
                os.remove(script_path)

    def create_bootable_usb_rufus_style(
        self,
        iso_path: str,
        device: USBDevice,
        partition_scheme: str = "GPT",
        filesystem: str = "NTFS",
        progress_callback=None
    ) -> bool:
        """
        Create bootable USB using Rufus-style method

        Args:
            iso_path: Path to Windows ISO
            device: Target USB device
            partition_scheme: GPT or MBR
            filesystem: NTFS or FAT32
            progress_callback: Progress callback function

        Returns:
            True if successful
        """
        # Step 1: Format USB
        if progress_callback:
            progress_callback("Formatting USB drive...", 10)

        if not self.format_usb(device, filesystem):
            return False

        # Step 2: Extract ISO contents to USB
        if progress_callback:
            progress_callback("Extracting ISO to USB...", 30)

        # Get the new drive letter after format
        devices = self.list_usb_devices()
        target_device = next((d for d in devices if d.device_id == device.device_id), None)

        if not target_device or not target_device.drive_letter:
            return False

        usb_path = f"{target_device.drive_letter}:\\"

        # Extract ISO
        if not self._extract_iso_to_usb(iso_path, usb_path, progress_callback):
            return False

        # Step 3: Make bootable
        if progress_callback:
            progress_callback("Making USB bootable...", 80)

        if not self._make_bootable(usb_path, partition_scheme):
            return False

        if progress_callback:
            progress_callback("Bootable USB created successfully!", 100)

        return True

    def _extract_iso_to_usb(self, iso_path: str, usb_path: str, progress_callback=None) -> bool:
        """Extract ISO contents to USB"""
        # Try 7-Zip first
        seven_zip = r"C:\Program Files\7-Zip\7z.exe"
        if os.path.exists(seven_zip):
            result = subprocess.run(
                [seven_zip, "x", iso_path, f"-o{usb_path}", "-y"],
                capture_output=True
            )
            return result.returncode == 0

        # Fallback: PowerShell method
        ps_script = f"""
        $iso = Mount-DiskImage -ImagePath '{iso_path}' -PassThru
        $drive = ($iso | Get-Volume).DriveLetter
        Copy-Item -Path "${{drive}}:\\*" -Destination '{usb_path}' -Recurse -Force
        Dismount-DiskImage -ImagePath '{iso_path}'
        """

        try:
            result = subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True
            )
            return result.returncode == 0
        except:
            return False

    def _make_bootable(self, usb_path: str, partition_scheme: str) -> bool:
        """Make USB bootable using bootsect or bcdboot"""
        # For UEFI (GPT)
        if partition_scheme.upper() == "GPT":
            # No additional action needed for UEFI if files are copied correctly
            return True

        # For Legacy BIOS (MBR)
        # Use bootsect to make it bootable
        bootsect_paths = [
            os.path.join(usb_path, "boot", "bootsect.exe"),
            r"C:\Program Files (x86)\Windows Kits\10\Assessment and Deployment Kit\Deployment Tools\amd64\Bootsect\bootsect.exe"
        ]

        bootsect = None
        for path in bootsect_paths:
            if os.path.exists(path):
                bootsect = path
                break

        if bootsect:
            drive_letter = usb_path.rstrip("\\")
            result = subprocess.run(
                [bootsect, "/nt60", drive_letter, "/force", "/mbr"],
                capture_output=True
            )
            return result.returncode == 0

        return False

    def create_bootable_usb_simple(
        self,
        iso_path: str,
        usb_drive_letter: str,
        progress_callback=None
    ) -> bool:
        """
        Simple method: Copy ISO contents to USB (requires pre-formatted USB)

        Args:
            iso_path: Path to Windows ISO
            usb_drive_letter: Target USB drive letter (e.g., 'E')
            progress_callback: Progress callback function

        Returns:
            True if successful
        """
        usb_path = f"{usb_drive_letter.upper()}:\\"

        if not os.path.exists(usb_path):
            raise ValueError(f"Drive {usb_path} does not exist!")

        if progress_callback:
            progress_callback("Extracting ISO...", 10)

        # Extract ISO to USB
        return self._extract_iso_to_usb(iso_path, usb_path, progress_callback)

    def create_ventoy_usb(self, device: USBDevice, ventoy_path: Optional[str] = None) -> bool:
        """
        Install Ventoy to USB (allows multiple ISOs on one drive)

        Args:
            device: Target USB device
            ventoy_path: Path to Ventoy installation

        Returns:
            True if successful
        """
        # This would integrate with Ventoy
        # For now, return a placeholder
        raise NotImplementedError("Ventoy integration not yet implemented")


class MediaCreationTool:
    """Wrapper for Windows Media Creation Tool"""

    def __init__(self):
        self.tool_path = None

    def download_media_creation_tool(self, output_dir: str) -> str:
        """Download official Media Creation Tool"""
        # URL for Media Creation Tool
        urls = {
            'windows11': 'https://go.microsoft.com/fwlink/?linkid=2156295',
            'windows10': 'https://go.microsoft.com/fwlink/?LinkId=691209'
        }

        tool_path = os.path.join(output_dir, "MediaCreationTool.exe")

        # Download Windows 11 tool by default
        response = requests.get(urls['windows11'], stream=True)
        response.raise_for_status()

        with open(tool_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        self.tool_path = tool_path
        return tool_path

    def run_tool(self, auto_mode: bool = False) -> bool:
        """Run the Media Creation Tool"""
        if not self.tool_path or not os.path.exists(self.tool_path):
            raise FileNotFoundError("Media Creation Tool not found")

        args = [self.tool_path]
        if auto_mode:
            args.append("/auto")

        result = subprocess.run(args)
        return result.returncode == 0


# Convenience functions
def download_windows_iso(
    version: str = "win11_23h2",
    edition: str = "Professional",
    language: str = "en-US",
    output_dir: Optional[str] = None
) -> str:
    """Quick download Windows ISO"""
    downloader = ISODownloader(download_dir=output_dir)
    available = downloader.get_available_windows_versions()

    # Get download links
    iso_info_list = downloader.get_download_links(version, edition, language)

    if not iso_info_list:
        raise ValueError(f"No ISOs found for {version}")

    # Download first available
    iso_path = downloader.download_iso(iso_info_list[0])
    return iso_path


def create_bootable_usb(iso_path: str, usb_drive: str) -> bool:
    """Quick create bootable USB"""
    creator = USBBootCreator()

    # If usb_drive is a drive letter, use simple method
    if len(usb_drive) == 1:
        return creator.create_bootable_usb_simple(iso_path, usb_drive)

    return False


def list_usb_drives() -> List[USBDevice]:
    """Quick list USB drives"""
    creator = USBBootCreator()
    return creator.list_usb_devices()
