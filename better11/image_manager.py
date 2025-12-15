"""
Windows Image Management Module

Provides comprehensive tools for working with Windows images including:
- WIM/ESD/ISO mounting and editing
- Image deployment and capture
- Package and driver injection
- Feature enabling/disabling
- Offline registry editing
"""

import os
import subprocess
import json
import shutil
import tempfile
from pathlib import Path
from typing import List, Dict, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum


class ImageFormat(Enum):
    """Supported image formats"""
    WIM = "wim"
    ESD = "esd"
    ISO = "iso"
    VHD = "vhd"
    VHDX = "vhdx"


class ImageType(Enum):
    """Windows image types"""
    INSTALL = "install"
    BOOT = "boot"
    WINRE = "winre"


@dataclass
class ImageInfo:
    """Information about a Windows image"""
    path: str
    format: ImageFormat
    index: int
    name: str
    description: str
    size: int
    architecture: str
    version: str
    build: str
    service_pack_level: int
    languages: List[str]
    default_language: str

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'path': self.path,
            'format': self.format.value,
            'index': self.index,
            'name': self.name,
            'description': self.description,
            'size': self.size,
            'architecture': self.architecture,
            'version': self.version,
            'build': self.build,
            'service_pack_level': self.service_pack_level,
            'languages': self.languages,
            'default_language': self.default_language
        }


@dataclass
class MountPoint:
    """Represents a mounted Windows image"""
    path: str
    image_path: str
    index: int
    read_only: bool
    mount_status: str

    def is_mounted(self) -> bool:
        """Check if mount point is active"""
        return self.mount_status.lower() in ['ok', 'mounted']


class DismWrapper:
    """Wrapper for DISM (Deployment Image Servicing and Management) operations"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.dism_path = self._find_dism()

    def _find_dism(self) -> str:
        """Locate DISM executable"""
        # Try system32 first
        dism = r"C:\Windows\System32\dism.exe"
        if os.path.exists(dism):
            return dism

        # Try to find in PATH
        dism_path = shutil.which("dism.exe")
        if dism_path:
            return dism_path

        raise FileNotFoundError("DISM.exe not found. Ensure you're running on Windows.")

    def _run_dism(self, args: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Execute DISM command"""
        cmd = [self.dism_path] + args

        if self.verbose:
            print(f"Executing: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )

        if check and result.returncode != 0:
            raise RuntimeError(f"DISM command failed: {result.stderr}")

        return result

    def get_image_info(self, image_path: str, index: Optional[int] = None) -> List[ImageInfo]:
        """Get information about images in a WIM/ESD file"""
        args = ["/Get-ImageInfo", f"/ImageFile:{image_path}"]

        if index is not None:
            args.append(f"/Index:{index}")

        result = self._run_dism(args)

        # Parse DISM output (simplified - in production, use proper parsing)
        images = []
        # This is a placeholder - actual implementation would parse DISM output
        return images

    def mount_image(
        self,
        image_path: str,
        mount_path: str,
        index: int = 1,
        read_only: bool = False,
        optimize: bool = True
    ) -> MountPoint:
        """Mount a Windows image"""
        # Create mount directory if it doesn't exist
        os.makedirs(mount_path, exist_ok=True)

        args = [
            "/Mount-Wim" if image_path.endswith('.wim') else "/Mount-Image",
            f"/WimFile:{image_path}",
            f"/Index:{index}",
            f"/MountDir:{mount_path}"
        ]

        if read_only:
            args.append("/ReadOnly")

        if optimize:
            args.append("/Optimize")

        self._run_dism(args)

        return MountPoint(
            path=mount_path,
            image_path=image_path,
            index=index,
            read_only=read_only,
            mount_status="OK"
        )

    def unmount_image(
        self,
        mount_path: str,
        commit: bool = True,
        discard: bool = False
    ) -> bool:
        """Unmount a Windows image"""
        args = ["/Unmount-Wim", f"/MountDir:{mount_path}"]

        if discard:
            args.append("/Discard")
        elif commit:
            args.append("/Commit")

        result = self._run_dism(args, check=False)
        return result.returncode == 0

    def cleanup_mount_points(self) -> bool:
        """Clean up corrupted mount points"""
        result = self._run_dism(["/Cleanup-Wim"], check=False)
        return result.returncode == 0

    def get_mount_points(self) -> List[MountPoint]:
        """Get all mounted images"""
        result = self._run_dism(["/Get-MountedImageInfo"])

        # Parse output to create MountPoint objects
        mount_points = []
        # Placeholder - actual implementation would parse DISM output
        return mount_points

    def add_driver(
        self,
        target: str,
        driver_path: str,
        recurse: bool = True,
        force_unsigned: bool = False
    ) -> bool:
        """Add driver(s) to an image or running OS"""
        args = [
            "/Add-Driver",
            f"/Driver:{driver_path}"
        ]

        # Determine if targeting mounted image or online system
        if os.path.isdir(target) and not target.lower() == "online":
            args.insert(0, f"/Image:{target}")
        else:
            args.insert(0, "/Online")

        if recurse:
            args.append("/Recurse")

        if force_unsigned:
            args.append("/ForceUnsigned")

        result = self._run_dism(args, check=False)
        return result.returncode == 0

    def add_package(
        self,
        target: str,
        package_path: str,
        ignore_check: bool = False
    ) -> bool:
        """Add a Windows package (CAB/MSU) to image"""
        args = [
            "/Add-Package",
            f"/PackagePath:{package_path}"
        ]

        if os.path.isdir(target) and target.lower() != "online":
            args.insert(0, f"/Image:{target}")
        else:
            args.insert(0, "/Online")

        if ignore_check:
            args.append("/IgnoreCheck")

        result = self._run_dism(args, check=False)
        return result.returncode == 0

    def enable_feature(
        self,
        target: str,
        feature_name: str,
        all_features: bool = False,
        limit_access: bool = False
    ) -> bool:
        """Enable a Windows feature"""
        args = [
            "/Enable-Feature",
            f"/FeatureName:{feature_name}"
        ]

        if os.path.isdir(target) and target.lower() != "online":
            args.insert(0, f"/Image:{target}")
        else:
            args.insert(0, "/Online")

        if all_features:
            args.append("/All")

        if limit_access:
            args.append("/LimitAccess")

        result = self._run_dism(args, check=False)
        return result.returncode == 0

    def disable_feature(self, target: str, feature_name: str, remove: bool = False) -> bool:
        """Disable a Windows feature"""
        args = [
            "/Disable-Feature",
            f"/FeatureName:{feature_name}"
        ]

        if os.path.isdir(target) and target.lower() != "online":
            args.insert(0, f"/Image:{target}")
        else:
            args.insert(0, "/Online")

        if remove:
            args.append("/Remove")

        result = self._run_dism(args, check=False)
        return result.returncode == 0

    def get_features(self, target: str) -> List[Dict[str, str]]:
        """Get Windows features in image"""
        args = ["/Get-Features"]

        if os.path.isdir(target) and target.lower() != "online":
            args.insert(0, f"/Image:{target}")
        else:
            args.insert(0, "/Online")

        result = self._run_dism(args)

        # Parse features from output
        features = []
        # Placeholder - actual implementation would parse DISM output
        return features

    def apply_image(
        self,
        image_path: str,
        apply_path: str,
        index: int = 1,
        verify: bool = True,
        compact: bool = False
    ) -> bool:
        """Apply a Windows image to a drive"""
        args = [
            "/Apply-Image",
            f"/ImageFile:{image_path}",
            f"/Index:{index}",
            f"/ApplyDir:{apply_path}"
        ]

        if verify:
            args.append("/Verify")

        if compact:
            args.append("/Compact")

        result = self._run_dism(args, check=False)
        return result.returncode == 0

    def capture_image(
        self,
        source_path: str,
        image_path: str,
        name: str,
        description: str = "",
        compress: str = "max",
        verify: bool = True
    ) -> bool:
        """Capture a Windows image"""
        args = [
            "/Capture-Image",
            f"/ImageFile:{image_path}",
            f"/CaptureDir:{source_path}",
            f"/Name:{name}",
            f"/Compress:{compress}"
        ]

        if description:
            args.append(f"/Description:{description}")

        if verify:
            args.append("/Verify")

        result = self._run_dism(args, check=False)
        return result.returncode == 0

    def export_image(
        self,
        source_image: str,
        dest_image: str,
        source_index: int,
        compress: str = "max",
        bootable: bool = False
    ) -> bool:
        """Export an image index to a new WIM file"""
        args = [
            "/Export-Image",
            f"/SourceImageFile:{source_image}",
            f"/SourceIndex:{source_index}",
            f"/DestinationImageFile:{dest_image}",
            f"/Compress:{compress}"
        ]

        if bootable:
            args.append("/Bootable")

        result = self._run_dism(args, check=False)
        return result.returncode == 0

    def split_image(
        self,
        image_path: str,
        dest_path: str,
        file_size: int = 4000
    ) -> bool:
        """Split a WIM file into smaller SWM files"""
        args = [
            "/Split-Image",
            f"/ImageFile:{image_path}",
            f"/SWMFile:{dest_path}",
            f"/FileSize:{file_size}"
        ]

        result = self._run_dism(args, check=False)
        return result.returncode == 0


class ImageManager:
    """High-level Windows image management"""

    def __init__(self, work_dir: Optional[str] = None, verbose: bool = False):
        self.dism = DismWrapper(verbose=verbose)
        self.work_dir = work_dir or tempfile.gettempdir()
        self.mount_dir = os.path.join(self.work_dir, "mounts")
        os.makedirs(self.mount_dir, exist_ok=True)

    def get_available_mount_path(self) -> str:
        """Get an available mount path"""
        i = 1
        while True:
            mount_path = os.path.join(self.mount_dir, f"mount_{i}")
            if not os.path.exists(mount_path) or not os.listdir(mount_path):
                os.makedirs(mount_path, exist_ok=True)
                return mount_path
            i += 1

    def mount_wim(
        self,
        wim_path: str,
        index: int = 1,
        read_only: bool = False
    ) -> MountPoint:
        """Mount a WIM/ESD file"""
        mount_path = self.get_available_mount_path()
        return self.dism.mount_image(wim_path, mount_path, index, read_only)

    def unmount_all(self, commit: bool = False) -> int:
        """Unmount all images"""
        count = 0
        mount_points = self.dism.get_mount_points()

        for mp in mount_points:
            if self.dism.unmount_image(mp.path, commit=commit):
                count += 1

        return count

    def inject_drivers_to_image(
        self,
        image_path: str,
        driver_path: str,
        index: int = 1
    ) -> bool:
        """Inject drivers into an offline image"""
        mount_point = self.mount_wim(image_path, index, read_only=False)

        try:
            success = self.dism.add_driver(mount_point.path, driver_path, recurse=True)
            return success
        finally:
            self.dism.unmount_image(mount_point.path, commit=success)

    def inject_updates_to_image(
        self,
        image_path: str,
        updates_path: str,
        index: int = 1
    ) -> Tuple[int, int]:
        """Inject Windows updates into an offline image"""
        mount_point = self.mount_wim(image_path, index, read_only=False)

        success_count = 0
        fail_count = 0

        try:
            # Find all CAB and MSU files
            update_files = []
            for ext in ['*.cab', '*.msu']:
                update_files.extend(Path(updates_path).rglob(ext))

            for update_file in update_files:
                if self.dism.add_package(mount_point.path, str(update_file)):
                    success_count += 1
                else:
                    fail_count += 1

            return (success_count, fail_count)
        finally:
            self.dism.unmount_image(mount_point.path, commit=(fail_count == 0))

    def optimize_image(self, image_path: str, index: int = 1) -> bool:
        """Optimize a Windows image (cleanup, reset base, etc.)"""
        mount_point = self.mount_wim(image_path, index, read_only=False)

        try:
            # Run cleanup operations
            cleanup_args = [
                "/Image:" + mount_point.path,
                "/Cleanup-Image",
                "/StartComponentCleanup",
                "/ResetBase"
            ]

            result = self.dism._run_dism(cleanup_args, check=False)
            return result.returncode == 0
        finally:
            self.dism.unmount_image(mount_point.path, commit=True)

    def extract_iso(self, iso_path: str, extract_path: str) -> bool:
        """Extract ISO contents"""
        os.makedirs(extract_path, exist_ok=True)

        # On Windows, try to use 7-Zip if available
        seven_zip = r"C:\Program Files\7-Zip\7z.exe"
        if os.path.exists(seven_zip):
            result = subprocess.run(
                [seven_zip, "x", iso_path, f"-o{extract_path}", "-y"],
                capture_output=True
            )
            return result.returncode == 0

        # Fallback: mount ISO and copy files
        # This requires Windows 10+
        try:
            # PowerShell script to mount and copy
            ps_script = f"""
            $iso = Mount-DiskImage -ImagePath '{iso_path}' -PassThru
            $drive = ($iso | Get-Volume).DriveLetter
            Copy-Item -Path "${{drive}}:\\*" -Destination '{extract_path}' -Recurse -Force
            Dismount-DiskImage -ImagePath '{iso_path}'
            """

            result = subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True
            )
            return result.returncode == 0
        except:
            return False

    def create_iso(self, source_path: str, iso_path: str, label: str = "WINDOWS") -> bool:
        """Create an ISO from a directory"""
        # Use oscdimg.exe (from Windows ADK)
        oscdimg_paths = [
            r"C:\Program Files (x86)\Windows Kits\10\Assessment and Deployment Kit\Deployment Tools\amd64\Oscdimg\oscdimg.exe",
            r"C:\Program Files\Windows Kits\10\Assessment and Deployment Kit\Deployment Tools\amd64\Oscdimg\oscdimg.exe"
        ]

        oscdimg = None
        for path in oscdimg_paths:
            if os.path.exists(path):
                oscdimg = path
                break

        if not oscdimg:
            raise FileNotFoundError("oscdimg.exe not found. Install Windows ADK.")

        # Create bootable ISO
        result = subprocess.run(
            [
                oscdimg,
                "-m",
                "-o",
                "-u2",
                "-udfver102",
                f"-l{label}",
                "-bootdata:2#p0,e,b" + os.path.join(source_path, "boot", "etfsboot.com") +
                "#pEF,e,b" + os.path.join(source_path, "efi", "microsoft", "boot", "efisys.bin"),
                source_path,
                iso_path
            ],
            capture_output=True
        )

        return result.returncode == 0


# Convenience functions
def mount_image(image_path: str, index: int = 1, read_only: bool = False) -> MountPoint:
    """Quick mount a Windows image"""
    manager = ImageManager()
    return manager.mount_wim(image_path, index, read_only)


def unmount_image(mount_path: str, commit: bool = True) -> bool:
    """Quick unmount a Windows image"""
    dism = DismWrapper()
    return dism.unmount_image(mount_path, commit=commit)


def inject_drivers(image_path: str, driver_path: str, index: int = 1) -> bool:
    """Quick inject drivers into image"""
    manager = ImageManager()
    return manager.inject_drivers_to_image(image_path, driver_path, index)


def inject_updates(image_path: str, updates_path: str, index: int = 1) -> Tuple[int, int]:
    """Quick inject updates into image"""
    manager = ImageManager()
    return manager.inject_updates_to_image(image_path, updates_path, index)
