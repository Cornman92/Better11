"""Application auto-update system.

This module provides automatic update checking and installation for
applications managed by Better11, as well as Better11 self-update functionality.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.request import urlopen
from urllib.error import URLError

from ..interfaces import Updatable, Version
from . import get_logger

_LOGGER = get_logger(__name__)


class UpdateChannel(Enum):
    """Update channel/release type."""
    
    STABLE = "stable"
    BETA = "beta"
    NIGHTLY = "nightly"


class UpdateStatus(Enum):
    """Status of an update check/install."""
    
    UP_TO_DATE = "up_to_date"
    UPDATE_AVAILABLE = "update_available"
    DOWNLOADING = "downloading"
    READY_TO_INSTALL = "ready_to_install"
    INSTALLING = "installing"
    INSTALLED = "installed"
    FAILED = "failed"
    CHECKING = "checking"


@dataclass
class UpdateInfo:
    """Information about an available update."""
    
    current_version: Version
    new_version: Version
    download_url: str
    changelog: str
    release_date: datetime
    size_bytes: int
    hash_sha256: str
    is_mandatory: bool = False
    requires_restart: bool = True
    min_python_version: Optional[str] = None

    @property
    def size_mb(self) -> float:
        """Size in megabytes."""
        return self.size_bytes / (1024 * 1024)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "current_version": str(self.current_version),
            "new_version": str(self.new_version),
            "download_url": self.download_url,
            "changelog": self.changelog,
            "release_date": self.release_date.isoformat(),
            "size_bytes": self.size_bytes,
            "hash_sha256": self.hash_sha256,
            "is_mandatory": self.is_mandatory,
            "requires_restart": self.requires_restart,
        }


@dataclass
class AppUpdateInfo:
    """Update information for a catalog application."""
    
    app_id: str
    app_name: str
    current_version: str
    new_version: str
    download_url: str
    hash_sha256: str
    changelog: str
    size_bytes: int


class ApplicationUpdater:
    """Check for and install updates for catalog applications.
    
    This class monitors installed applications for updates and can
    automatically download and install them.
    
    Parameters
    ----------
    catalog_path : Path
        Path to the application catalog JSON file
    state_path : Path, optional
        Path to the installation state file
    update_url : str, optional
        URL for the remote update manifest
    """
    
    def __init__(
        self,
        catalog_path: Path,
        state_path: Optional[Path] = None,
        update_url: Optional[str] = None
    ):
        self.catalog_path = catalog_path
        self.state_path = state_path or Path.home() / ".better11" / "state.json"
        self.update_url = update_url
        self._pending_updates: List[AppUpdateInfo] = []
    
    def check_for_updates(self, app_ids: Optional[List[str]] = None) -> List[AppUpdateInfo]:
        """Check for available updates for installed applications.
        
        Parameters
        ----------
        app_ids : List[str], optional
            Specific app IDs to check. If None, check all installed apps.
        
        Returns
        -------
        List[AppUpdateInfo]
            List of available updates
        """
        _LOGGER.info("Checking for application updates...")
        
        updates = []
        
        try:
            # Load current catalog
            with open(self.catalog_path, 'r') as f:
                catalog = json.load(f)
            
            # Load installation state
            if not self.state_path.exists():
                _LOGGER.info("No installation state found")
                return []
            
            with open(self.state_path, 'r') as f:
                state = json.load(f)
            
            installed = state.get("installed", {})
            
            # Filter by app_ids if specified
            if app_ids:
                installed = {k: v for k, v in installed.items() if k in app_ids}
            
            # Check each installed app against catalog
            for app_id, install_info in installed.items():
                installed_version = install_info.get("version", "0.0.0")
                
                # Find app in catalog
                for app in catalog.get("applications", []):
                    if app.get("id") == app_id:
                        catalog_version = app.get("version", "0.0.0")
                        
                        # Compare versions
                        if self._version_compare(catalog_version, installed_version) > 0:
                            update = AppUpdateInfo(
                                app_id=app_id,
                                app_name=app.get("name", app_id),
                                current_version=installed_version,
                                new_version=catalog_version,
                                download_url=app.get("download_url", ""),
                                hash_sha256=app.get("sha256", ""),
                                changelog=app.get("changelog", ""),
                                size_bytes=app.get("size", 0)
                            )
                            updates.append(update)
                            _LOGGER.info(
                                "Update available for %s: %s -> %s",
                                app_id, installed_version, catalog_version
                            )
                        break
            
            self._pending_updates = updates
            _LOGGER.info("Found %d updates available", len(updates))
            return updates
        
        except Exception as exc:
            _LOGGER.error("Failed to check for updates: %s", exc)
            return []
    
    def _version_compare(self, v1: str, v2: str) -> int:
        """Compare two version strings.
        
        Returns: 1 if v1 > v2, -1 if v1 < v2, 0 if equal
        """
        try:
            parts1 = [int(x) for x in v1.split('.')]
            parts2 = [int(x) for x in v2.split('.')]
            
            # Pad shorter version
            while len(parts1) < len(parts2):
                parts1.append(0)
            while len(parts2) < len(parts1):
                parts2.append(0)
            
            for p1, p2 in zip(parts1, parts2):
                if p1 > p2:
                    return 1
                elif p1 < p2:
                    return -1
            return 0
        except ValueError:
            # Fall back to string comparison
            return (v1 > v2) - (v1 < v2)
    
    def install_update(self, app_id: str) -> bool:
        """Install an available update for an application.
        
        Parameters
        ----------
        app_id : str
            Application ID to update
        
        Returns
        -------
        bool
            True if update was successful
        """
        _LOGGER.info("Installing update for %s", app_id)
        
        # Find the update
        update = None
        for u in self._pending_updates:
            if u.app_id == app_id:
                update = u
                break
        
        if not update:
            _LOGGER.error("No pending update found for %s", app_id)
            return False
        
        try:
            # Import app manager for installation
            from .manager import AppManager
            
            manager = AppManager(self.catalog_path)
            status, result = manager.install(app_id)
            
            if status == "installed":
                _LOGGER.info("Successfully updated %s to version %s", 
                            app_id, update.new_version)
                # Remove from pending updates
                self._pending_updates = [u for u in self._pending_updates if u.app_id != app_id]
                return True
            else:
                _LOGGER.error("Update failed for %s: %s", app_id, result)
                return False
        
        except Exception as exc:
            _LOGGER.error("Failed to install update: %s", exc)
            return False
    
    def install_all_updates(self) -> Dict[str, bool]:
        """Install all pending updates.
        
        Returns
        -------
        Dict[str, bool]
            Dictionary of app_id -> success status
        """
        results = {}
        for update in self._pending_updates.copy():
            results[update.app_id] = self.install_update(update.app_id)
        return results
    
    def get_pending_updates(self) -> List[AppUpdateInfo]:
        """Get list of pending updates.
        
        Returns
        -------
        List[AppUpdateInfo]
            Pending updates
        """
        return self._pending_updates.copy()


class Better11Updater(Updatable):
    """Self-update functionality for Better11.
    
    This class handles checking for and installing Better11 updates,
    including proper handling of the running application replacement.
    
    Parameters
    ----------
    update_url : str
        URL to check for updates (JSON manifest)
    channel : UpdateChannel
        Update channel to use
    """
    
    BETTER11_VERSION = "0.3.0"
    DEFAULT_UPDATE_URL = "https://api.github.com/repos/better11/better11/releases/latest"
    
    def __init__(
        self,
        update_url: Optional[str] = None,
        channel: UpdateChannel = UpdateChannel.STABLE
    ):
        self.update_url = update_url or self.DEFAULT_UPDATE_URL
        self.channel = channel
        self._update_info: Optional[UpdateInfo] = None
        self._download_path: Optional[Path] = None
        self._status = UpdateStatus.UP_TO_DATE
    
    def get_version(self) -> Version:
        """Get current Better11 version.
        
        Returns
        -------
        Version
            Current version
        """
        return Version.from_string(self.BETTER11_VERSION)
    
    def check_update(self) -> Optional[Version]:
        """Check if update is available.
        
        Returns
        -------
        Optional[Version]
            New version if available, None otherwise
        """
        _LOGGER.info("Checking for Better11 updates...")
        self._status = UpdateStatus.CHECKING
        
        try:
            update_info = self._fetch_update_manifest()
            
            if update_info is None:
                self._status = UpdateStatus.UP_TO_DATE
                return None
            
            current = self.get_version()
            new = update_info.new_version
            
            if new > current:
                _LOGGER.info("Update available: %s -> %s", current, new)
                self._update_info = update_info
                self._status = UpdateStatus.UPDATE_AVAILABLE
                return new
            else:
                _LOGGER.info("Better11 is up to date (%s)", current)
                self._status = UpdateStatus.UP_TO_DATE
                return None
        
        except Exception as exc:
            _LOGGER.error("Failed to check for updates: %s", exc)
            self._status = UpdateStatus.FAILED
            return None
    
    def _fetch_update_manifest(self) -> Optional[UpdateInfo]:
        """Fetch update manifest from update URL.
        
        Returns
        -------
        Optional[UpdateInfo]
            Update information if available
        """
        try:
            # Check if URL is GitHub API
            if "api.github.com" in self.update_url:
                return self._fetch_github_release()
            else:
                return self._fetch_json_manifest()
        
        except Exception as exc:
            _LOGGER.error("Failed to fetch update manifest: %s", exc)
            return None
    
    def _fetch_github_release(self) -> Optional[UpdateInfo]:
        """Fetch latest release from GitHub API.
        
        Returns
        -------
        Optional[UpdateInfo]
            Update information if available
        """
        try:
            with urlopen(self.update_url, timeout=30) as response:
                data = json.loads(response.read().decode())
            
            # Parse GitHub release response
            tag_name = data.get("tag_name", "").lstrip("v")
            body = data.get("body", "")
            published_at = data.get("published_at", "")
            
            # Find appropriate asset
            assets = data.get("assets", [])
            download_url = ""
            size = 0
            sha256 = ""
            
            for asset in assets:
                name = asset.get("name", "")
                if "better11" in name.lower() and name.endswith(".zip"):
                    download_url = asset.get("browser_download_url", "")
                    size = asset.get("size", 0)
                    break
            
            if not download_url:
                # Use source archive as fallback
                download_url = data.get("zipball_url", "")
                size = 0
            
            release_date = datetime.now()
            if published_at:
                try:
                    release_date = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                except ValueError:
                    pass
            
            return UpdateInfo(
                current_version=self.get_version(),
                new_version=Version.from_string(tag_name),
                download_url=download_url,
                changelog=body,
                release_date=release_date,
                size_bytes=size,
                hash_sha256=sha256,  # Would need separate fetch
                is_mandatory=False,
                requires_restart=True
            )
        
        except URLError as exc:
            _LOGGER.error("Network error: %s", exc)
            return None
        except Exception as exc:
            _LOGGER.error("Failed to parse GitHub release: %s", exc)
            return None
    
    def _fetch_json_manifest(self) -> Optional[UpdateInfo]:
        """Fetch update manifest from JSON URL.
        
        Returns
        -------
        Optional[UpdateInfo]
            Update information if available
        """
        try:
            with urlopen(self.update_url, timeout=30) as response:
                data = json.loads(response.read().decode())
            
            return UpdateInfo(
                current_version=self.get_version(),
                new_version=Version.from_string(data.get("version", "0.0.0")),
                download_url=data.get("download_url", ""),
                changelog=data.get("changelog", ""),
                release_date=datetime.fromisoformat(data.get("release_date", datetime.now().isoformat())),
                size_bytes=data.get("size_bytes", 0),
                hash_sha256=data.get("sha256", ""),
                is_mandatory=data.get("mandatory", False),
                requires_restart=data.get("requires_restart", True),
                min_python_version=data.get("min_python_version")
            )
        
        except Exception as exc:
            _LOGGER.error("Failed to fetch JSON manifest: %s", exc)
            return None
    
    def apply_update(self) -> bool:
        """Download and apply the available update.
        
        Returns
        -------
        bool
            True if update was successful
        """
        if self._update_info is None:
            _LOGGER.error("No update available to apply")
            return False
        
        _LOGGER.info("Applying update to version %s", self._update_info.new_version)
        
        try:
            # Step 1: Download update
            self._status = UpdateStatus.DOWNLOADING
            download_path = self._download_update()
            
            if not download_path:
                self._status = UpdateStatus.FAILED
                return False
            
            # Step 2: Verify hash if provided
            if self._update_info.hash_sha256:
                if not self._verify_download(download_path):
                    self._status = UpdateStatus.FAILED
                    return False
            
            self._status = UpdateStatus.READY_TO_INSTALL
            
            # Step 3: Install update
            self._status = UpdateStatus.INSTALLING
            if self._install_update(download_path):
                self._status = UpdateStatus.INSTALLED
                _LOGGER.info("Update installed successfully. Restart required.")
                return True
            else:
                self._status = UpdateStatus.FAILED
                return False
        
        except Exception as exc:
            _LOGGER.error("Failed to apply update: %s", exc)
            self._status = UpdateStatus.FAILED
            return False
    
    def _download_update(self) -> Optional[Path]:
        """Download the update package.
        
        Returns
        -------
        Optional[Path]
            Path to downloaded file
        """
        if not self._update_info:
            return None
        
        try:
            _LOGGER.info("Downloading update from %s", self._update_info.download_url)
            
            # Create temp directory
            temp_dir = Path(tempfile.mkdtemp(prefix="better11_update_"))
            download_path = temp_dir / "update.zip"
            
            with urlopen(self._update_info.download_url, timeout=300) as response:
                with open(download_path, 'wb') as f:
                    shutil.copyfileobj(response, f)
            
            _LOGGER.info("Download complete: %s", download_path)
            self._download_path = download_path
            return download_path
        
        except Exception as exc:
            _LOGGER.error("Download failed: %s", exc)
            return None
    
    def _verify_download(self, file_path: Path) -> bool:
        """Verify downloaded file hash.
        
        Parameters
        ----------
        file_path : Path
            Path to downloaded file
        
        Returns
        -------
        bool
            True if hash matches
        """
        if not self._update_info or not self._update_info.hash_sha256:
            return True
        
        _LOGGER.info("Verifying download hash...")
        
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        
        calculated = sha256.hexdigest()
        expected = self._update_info.hash_sha256.lower()
        
        if calculated == expected:
            _LOGGER.info("Hash verification passed")
            return True
        else:
            _LOGGER.error("Hash mismatch! Expected: %s, Got: %s", expected, calculated)
            return False
    
    def _install_update(self, update_path: Path) -> bool:
        """Install the downloaded update.
        
        This method handles extracting the update and setting up
        the replacement process for the next restart.
        
        Parameters
        ----------
        update_path : Path
            Path to downloaded update package
        
        Returns
        -------
        bool
            True if installation was successful
        """
        try:
            import zipfile
            
            # Determine installation directory
            install_dir = Path(__file__).parent.parent.parent
            backup_dir = install_dir.parent / f"better11_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            _LOGGER.info("Preparing update installation...")
            _LOGGER.info("Install directory: %s", install_dir)
            
            # Create extraction directory
            extract_dir = update_path.parent / "extracted"
            
            # Extract update package
            with zipfile.ZipFile(update_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # Find the actual content directory (may be nested)
            content_dir = extract_dir
            for item in extract_dir.iterdir():
                if item.is_dir() and (item / "better11").exists():
                    content_dir = item
                    break
            
            # Create update script for safe replacement
            update_script = self._create_update_script(
                str(content_dir),
                str(install_dir),
                str(backup_dir)
            )
            
            _LOGGER.info("Update prepared. Run the following to complete:\n%s", update_script)
            
            # Save update script
            script_path = Path.home() / ".better11" / "pending_update.py"
            script_path.parent.mkdir(parents=True, exist_ok=True)
            with open(script_path, 'w') as f:
                f.write(update_script)
            
            return True
        
        except Exception as exc:
            _LOGGER.error("Installation failed: %s", exc)
            return False
    
    def _create_update_script(self, source: str, dest: str, backup: str) -> str:
        """Create a Python script for completing the update.
        
        Parameters
        ----------
        source : str
            Source directory with new files
        dest : str
            Destination directory
        backup : str
            Backup directory
        
        Returns
        -------
        str
            Python script content
        """
        return f'''#!/usr/bin/env python3
"""Better11 Update Script - Auto-generated"""
import shutil
import sys
from pathlib import Path

def apply_update():
    source = Path(r"{source}")
    dest = Path(r"{dest}")
    backup = Path(r"{backup}")
    
    print(f"Backing up current installation to {{backup}}...")
    if dest.exists():
        shutil.copytree(dest, backup)
    
    print(f"Installing update from {{source}}...")
    for item in source.iterdir():
        dest_item = dest / item.name
        if dest_item.exists():
            if dest_item.is_dir():
                shutil.rmtree(dest_item)
            else:
                dest_item.unlink()
        shutil.copytree(item, dest_item) if item.is_dir() else shutil.copy2(item, dest_item)
    
    print("Update complete! You may delete the backup directory if everything works.")
    print(f"Backup location: {{backup}}")

if __name__ == "__main__":
    apply_update()
'''
    
    def get_update_info(self) -> Optional[UpdateInfo]:
        """Get current update information.
        
        Returns
        -------
        Optional[UpdateInfo]
            Update info if available
        """
        return self._update_info
    
    def get_status(self) -> UpdateStatus:
        """Get current update status.
        
        Returns
        -------
        UpdateStatus
            Current status
        """
        return self._status


def check_for_updates() -> Optional[Version]:
    """Convenience function to check for Better11 updates.
    
    Returns
    -------
    Optional[Version]
        New version if available
    """
    updater = Better11Updater()
    return updater.check_update()


def get_logger(name: str):
    """Get a logger instance."""
    import logging
    return logging.getLogger(name)


__all__ = [
    "UpdateChannel",
    "UpdateStatus",
    "UpdateInfo",
    "AppUpdateInfo",
    "ApplicationUpdater",
    "Better11Updater",
    "check_for_updates",
]
