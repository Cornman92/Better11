from __future__ import annotations

import logging
import shutil
from pathlib import Path
from typing import Iterable, Sequence

from better11.windows_ops import (
    UnsupportedPlatformError,
    is_windows,
    resolve_path,
    run_dism,
    run_powershell,
)

LOGGER = logging.getLogger(__name__)


class WindowsDeploymentManager:
    """Manage Windows image capture, application, and servicing operations."""

    def __init__(self, *, dry_run: bool = False) -> None:
        self.dry_run = dry_run

    def _ensure_supported(self) -> None:
        if not is_windows():
            raise UnsupportedPlatformError("Deployment operations require a Windows host.")

    def capture_image(
        self,
        source_volume: str | Path,
        destination_image: str | Path,
        image_name: str,
        *,
        description: str | None = None,
        compress_to_esd: bool = False,
    ) -> None:
        """Capture a volume into a WIM or ESD image using DISM."""

        self._ensure_supported()
        source = resolve_path(source_volume)
        destination = Path(destination_image).expanduser().resolve()
        destination.parent.mkdir(parents=True, exist_ok=True)
        compress = "/Compress:recovery" if compress_to_esd else "/Compress:max"
        args = [
            "/Capture-Image",
            f"/ImageFile:{destination}",
            f"/CaptureDir:{source}",
            f"/Name:{image_name}",
            compress,
            "/CheckIntegrity",
        ]
        if description:
            args.append(f"/Description:{description}")
        LOGGER.info("Capturing %s to %s", source, destination)
        if self.dry_run:
            return
        run_dism(args)

    def apply_image(
        self, image_path: str | Path, target_partition: str | Path, *, index: int = 1, verify: bool = True
    ) -> None:
        """Apply a WIM/ESD image to a target partition."""

        self._ensure_supported()
        image = resolve_path(image_path)
        target_dir = Path(target_partition).expanduser().resolve()
        target_dir.mkdir(parents=True, exist_ok=True)
        args = [
            "/Apply-Image",
            f"/ImageFile:{image}",
            f"/Index:{index}",
            f"/ApplyDir:{target_dir}",
        ]
        if verify:
            args.append("/CheckIntegrity")
        LOGGER.info("Applying image %s (index %s) to %s", image, index, target_dir)
        if self.dry_run:
            return
        run_dism(args)

    def service_image(
        self,
        image_path: str | Path,
        mount_dir: str | Path,
        *,
        index: int = 1,
        drivers: Sequence[str | Path] | None = None,
        features: Sequence[str] | None = None,
        updates: Sequence[str | Path] | None = None,
        commit: bool = True,
    ) -> None:
        """Mount and service an offline image by adding drivers, features, and updates."""

        self._ensure_supported()
        image = resolve_path(image_path)
        mount_point = Path(mount_dir).expanduser().resolve()
        mount_point.mkdir(parents=True, exist_ok=True)
        LOGGER.info("Mounting image %s (index %s) to %s", image, index, mount_point)
        if not self.dry_run:
            run_dism(["/Mount-Image", f"/ImageFile:{image}", f"/Index:{index}", f"/MountDir:{mount_point}"])
        try:
            self._add_drivers(mount_point, drivers)
            self._enable_features(mount_point, features)
            self._apply_updates(mount_point, updates)
        finally:
            self._unmount_image(mount_point, commit=commit)

    def _add_drivers(self, mount_point: Path, drivers: Sequence[str | Path] | None) -> None:
        if not drivers:
            return
        for driver in drivers:
            driver_path = resolve_path(driver)
            args = [
                f"/Image:{mount_point}",
                "/Add-Driver",
                f"/Driver:{driver_path}",
                "/Recurse",
            ]
            LOGGER.info("Injecting driver %s", driver_path)
            if self.dry_run:
                continue
            run_dism(args)

    def _enable_features(self, mount_point: Path, features: Sequence[str] | None) -> None:
        if not features:
            return
        for feature in features:
            args = [
                f"/Image:{mount_point}",
                "/Enable-Feature",
                f"/FeatureName:{feature}",
                "/All",
            ]
            LOGGER.info("Enabling feature %s", feature)
            if self.dry_run:
                continue
            run_dism(args)

    def _apply_updates(self, mount_point: Path, updates: Sequence[str | Path] | None) -> None:
        if not updates:
            return
        for update in updates:
            package_path = resolve_path(update)
            args = [
                f"/Image:{mount_point}",
                "/Add-Package",
                f"/PackagePath:{package_path}",
            ]
            LOGGER.info("Adding update package %s", package_path)
            if self.dry_run:
                continue
            run_dism(args)

    def _unmount_image(self, mount_point: Path, *, commit: bool) -> None:
        flags: Iterable[str] = ["/Commit"] if commit else ["/Discard"]
        args = ["/Unmount-Image", f"/MountDir:{mount_point}", *flags]
        LOGGER.info("Unmounting image at %s (%s)", mount_point, "commit" if commit else "discard")
        if self.dry_run:
            return
        try:
            run_dism(args)
        finally:
            if mount_point.exists() and not any(mount_point.iterdir()):
                shutil.rmtree(mount_point, ignore_errors=True)

    def verify_image(self, image_path: str | Path) -> None:
        """Run a PowerShell integrity check on the captured image."""

        self._ensure_supported()
        image = resolve_path(image_path)
        LOGGER.info("Verifying image integrity for %s", image)
        if self.dry_run:
            return
        run_powershell([f"Get-WindowsImage -ImagePath '{image}' | Format-List *"])
