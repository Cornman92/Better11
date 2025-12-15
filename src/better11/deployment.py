"""Deployment utilities for capturing and applying Windows images."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence

from . import windows_ops
from .windows_ops import UnsupportedPlatformError, run_dism, run_powershell


class WindowsDeploymentManager:
    """Wrap DISM/PowerShell workflows for deployment tasks."""

    def __init__(self) -> None:
        if not windows_ops.is_windows():
            raise UnsupportedPlatformError(
                "Windows deployment workflows are only available on Windows hosts."
            )

    def capture_volume_to_image(
        self,
        volume_path: str | Path,
        image_path: str | Path,
        *,
        name: str = "CapturedImage",
        description: str | None = None,
        image_format: str = "wim",
        compression: str = "max",
    ) -> None:
        """Capture a volume into a WIM/ESD image using DISM."""

        fmt = image_format.lower()
        if fmt not in {"wim", "esd"}:
            raise ValueError("image_format must be either 'wim' or 'esd'")

        arguments = [
            "/Capture-Image",
            f"/ImageFile:{Path(image_path)}",
            f"/CaptureDir:{Path(volume_path)}",
            f"/Name:{name}",
        ]
        if description:
            arguments.append(f"/Description:{description}")

        if fmt == "esd":
            arguments.append("/Compress:recovery")
        else:
            arguments.append(f"/Compress:{compression}")

        run_dism(arguments)

    def apply_image(
        self,
        image_path: str | Path,
        target_dir: str | Path,
        *,
        index: int = 1,
    ) -> None:
        """Apply a captured image to a target directory."""

        arguments = [
            "/Apply-Image",
            f"/ImageFile:{Path(image_path)}",
            f"/Index:{index}",
            f"/ApplyDir:{Path(target_dir)}",
        ]
        run_dism(arguments)

    def service_image(
        self,
        image_path: str | Path,
        mount_dir: str | Path,
        *,
        index: int = 1,
        drivers: Sequence[str | Path] | None = None,
        features: Sequence[str] | None = None,
        updates: Sequence[str | Path] | None = None,
    ) -> None:
        """Mount an image, apply servicing steps, and commit the changes."""

        mounted = False
        try:
            run_dism(
                [
                    "/Mount-Image",
                    f"/ImageFile:{Path(image_path)}",
                    f"/Index:{index}",
                    f"/MountDir:{Path(mount_dir)}",
                ]
            )
            mounted = True

            self._add_drivers(mount_dir, drivers or [])
            self._enable_features(mount_dir, features or [])
            self._add_updates(mount_dir, updates or [])

        finally:
            if mounted:
                try:
                    run_dism([
                        "/Unmount-Image",
                        f"/MountDir:{Path(mount_dir)}",
                        "/Commit",
                    ])
                except Exception:
                    # Ensure mounts are not left behind even if commit fails
                    run_dism([
                        "/Unmount-Image",
                        f"/MountDir:{Path(mount_dir)}",
                        "/Discard",
                    ])

    def _add_drivers(self, mount_dir: str | Path, drivers: Iterable[str | Path]) -> None:
        for driver_path in drivers:
            run_dism(
                [
                    f"/Image:{Path(mount_dir)}",
                    "/Add-Driver",
                    f"/Driver:{Path(driver_path)}",
                    "/Recurse",
                ]
            )

    def _enable_features(self, mount_dir: str | Path, features: Iterable[str]) -> None:
        for feature in features:
            run_dism(
                [
                    f"/Image:{Path(mount_dir)}",
                    "/Enable-Feature",
                    f"/FeatureName:{feature}",
                    "/All",
                ]
            )

    def _add_updates(self, mount_dir: str | Path, updates: Iterable[str | Path]) -> None:
        for update_path in updates:
            run_dism(
                [
                    f"/Image:{Path(mount_dir)}",
                    "/Add-Package",
                    f"/PackagePath:{Path(update_path)}",
                ]
            )

        if updates:
            run_powershell(
                [
                    "Get-WindowsPackage",
                    f"-Path {Path(mount_dir)}",
                ]
            )
