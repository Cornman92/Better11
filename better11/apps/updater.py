"""Application update management for Better11.

This module provides functionality to check for application updates,
compare versions, download and install updates, and manage Better11
self-updates.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse

import requests
from packaging import version

from .catalog import AppCatalog
from .manager import AppManager
from .models import AppMetadata, AppStatus
from .state_store import InstallationStateStore
from ..interfaces import Updatable, Version

_LOGGER = logging.getLogger(__name__)


@dataclass
class UpdateInfo:
    """Information about an available update."""
    
    app_id: str
    current_version: Version
    available_version: Version
    download_url: str
    release_notes: str = ""
    release_date: Optional[datetime] = None
    is_security_update: bool = False
    is_mandatory: bool = False
    size_mb: float = 0.0
    
    def __str__(self) -> str:
        return f"{self.app_id}: {self.current_version} -> {self.available_version}"


class ApplicationUpdater:
    """Manage application updates.
    
    This class checks for updates to installed applications by comparing
    versions in the catalog with installed versions.
    
    Parameters
    ----------
    app_manager : AppManager
        Application manager instance
    catalog_url : Optional[str]
        URL to fetch latest catalog from (optional)
    """
    
    def __init__(
        self,
        app_manager: AppManager,
        catalog_url: Optional[str] = None
    ):
        self.app_manager = app_manager
        self.catalog_url = catalog_url
        self.state_store: InstallationStateStore = app_manager.state_store
    
    def check_for_updates(self, app_id: Optional[str] = None) -> List[UpdateInfo]:
        """Check for updates for installed applications.
        
        Parameters
        ----------
        app_id : Optional[str]
            Specific app ID to check, or None for all installed apps
        
        Returns
        -------
        List[UpdateInfo]
            List of available updates
        """
        _LOGGER.info("Checking for updates%s", f" for {app_id}" if app_id else "")
        
        # Get installed applications
        installed = self.state_store.list_installed()
        
        if app_id:
            installed = [app for app in installed if app.app_id == app_id]
        
        if not installed:
            _LOGGER.info("No installed applications to check")
            return []
        
        # Fetch latest catalog if URL provided
        catalog = self.app_manager.catalog
        if self.catalog_url:
            try:
                catalog = self._fetch_latest_catalog()
            except Exception as e:
                _LOGGER.warning("Failed to fetch latest catalog, using local: %s", e)
        
        updates: List[UpdateInfo] = []
        
        for installed_app in installed:
            try:
                # Get latest version from catalog
                latest_metadata = catalog.get(installed_app.app_id)
                
                # Compare versions
                current_ver = Version.parse(installed_app.version)
                available_ver = Version.parse(latest_metadata.version)
                
                if available_ver > current_ver:
                    update_info = UpdateInfo(
                        app_id=installed_app.app_id,
                        current_version=current_ver,
                        available_version=available_ver,
                        download_url=latest_metadata.uri,
                        release_notes=getattr(latest_metadata, 'release_notes', ''),
                        release_date=getattr(latest_metadata, 'release_date', None),
                        is_security_update=getattr(latest_metadata, 'is_security_update', False),
                        is_mandatory=getattr(latest_metadata, 'is_mandatory', False),
                        size_mb=getattr(latest_metadata, 'size_mb', 0.0)
                    )
                    updates.append(update_info)
                    _LOGGER.info(
                        "Update available: %s (%s -> %s)",
                        installed_app.app_id,
                        current_ver,
                        available_ver
                    )
            except KeyError:
                _LOGGER.debug("App %s not found in catalog", installed_app.app_id)
            except Exception as e:
                _LOGGER.error("Error checking update for %s: %s", installed_app.app_id, e)
        
        _LOGGER.info("Found %d update(s)", len(updates))
        return updates
    
    def install_update(self, update_info: UpdateInfo) -> bool:
        """Install an application update.
        
        Parameters
        ----------
        update_info : UpdateInfo
            Update information
        
        Returns
        -------
        bool
            True if installation successful
        """
        _LOGGER.info("Installing update: %s", update_info)
        
        try:
            # Use AppManager to install (which handles dependencies, verification, etc.)
            status, result = self.app_manager.install(update_info.app_id)
            
            if status.installed and status.version == str(update_info.available_version):
                _LOGGER.info("Successfully updated %s to %s", update_info.app_id, update_info.available_version)
                return True
            else:
                _LOGGER.error("Update installation failed for %s", update_info.app_id)
                return False
        except Exception as e:
            _LOGGER.error("Error installing update for %s: %s", update_info.app_id, e)
            return False
    
    def install_all_updates(self, updates: Optional[List[UpdateInfo]] = None) -> List[bool]:
        """Install all available updates.
        
        Parameters
        ----------
        updates : Optional[List[UpdateInfo]]
            List of updates to install. If None, checks for updates first.
        
        Returns
        -------
        List[bool]
            List of success status for each update
        """
        if updates is None:
            updates = self.check_for_updates()
        
        results: List[bool] = []
        for update in updates:
            success = self.install_update(update)
            results.append(success)
        
        return results
    
    def _fetch_latest_catalog(self) -> AppCatalog:
        """Fetch latest catalog from URL.
        
        Returns
        -------
        AppCatalog
            Latest catalog
        
        Raises
        ------
        requests.RequestException
            If catalog fetch fails
        """
        if not self.catalog_url:
            raise ValueError("No catalog URL configured")
        
        _LOGGER.info("Fetching latest catalog from %s", self.catalog_url)
        
        response = requests.get(self.catalog_url, timeout=30)
        response.raise_for_status()
        
        # Parse catalog
        catalog_data = response.json()
        catalog_path = Path(self.catalog_url)
        
        # Create temporary catalog file
        temp_catalog = Path.home() / ".better11" / "temp_catalog.json"
        temp_catalog.parent.mkdir(parents=True, exist_ok=True)
        
        with open(temp_catalog, 'w') as f:
            json.dump(catalog_data, f, indent=2)
        
        return AppCatalog.from_file(temp_catalog)


class Better11Updater(Updatable):
    """Self-update capability for Better11.
    
    This class manages Better11's own updates by checking a version
    endpoint and downloading updates.
    
    Parameters
    ----------
    version_check_url : str
        URL to check for Better11 version information
    """
    
    UPDATE_CHECK_URL = "https://api.github.com/repos/yourusername/better11/releases/latest"
    
    def __init__(self, version_check_url: Optional[str] = None):
        self.version_check_url = version_check_url or self.UPDATE_CHECK_URL
    
    def get_current_version(self) -> Version:
        """Get currently installed Better11 version.
        
        Returns
        -------
        Version
            Current version
        """
        try:
            from better11 import __version__
            return Version.parse(__version__)
        except (ImportError, AttributeError):
            # Fallback if __version__ not available
            return Version(0, 3, 0)
    
    def check_for_updates(self) -> Optional[UpdateInfo]:
        """Check if newer Better11 version is available.
        
        Returns
        -------
        Optional[UpdateInfo]
            Update information if available, None otherwise
        """
        current = self.get_current_version()
        
        try:
            _LOGGER.info("Checking for Better11 updates from %s", self.version_check_url)
            response = requests.get(self.version_check_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse GitHub release format
            latest_version_str = data.get('tag_name', '').lstrip('v')
            if not latest_version_str:
                _LOGGER.warning("No version tag found in release data")
                return None
            
            latest_version = Version.parse(latest_version_str)
            
            if latest_version > current:
                # Find download URL (prefer .zip or .msi)
                download_url = None
                for asset in data.get('assets', []):
                    url = asset.get('browser_download_url', '')
                    if url.endswith('.zip') or url.endswith('.msi'):
                        download_url = url
                        break
                
                if not download_url:
                    download_url = data.get('zipball_url', '')
                
                return UpdateInfo(
                    app_id="better11",
                    current_version=current,
                    available_version=latest_version,
                    download_url=download_url,
                    release_notes=data.get('body', ''),
                    release_date=datetime.fromisoformat(data.get('published_at', '').replace('Z', '+00:00')) if data.get('published_at') else None,
                    is_security_update=False,  # Could be determined from release notes
                    is_mandatory=False,
                    size_mb=0.0
                )
            else:
                _LOGGER.info("Better11 is up to date (%s)", current)
                return None
                
        except requests.RequestException as e:
            _LOGGER.error("Failed to check for Better11 updates: %s", e)
            return None
        except Exception as e:
            _LOGGER.error("Unexpected error checking for updates: %s", e)
            return None
    
    def download_update(self, version: Version) -> Path:
        """Download Better11 update package.
        
        Parameters
        ----------
        version : Version
            Version to download
        
        Returns
        -------
        Path
            Path to downloaded update package
        
        Raises
        ------
        requests.RequestException
            If download fails
        """
        update_info = self.check_for_updates()
        if not update_info or update_info.available_version != version:
            raise ValueError(f"Update for version {version} not available")
        
        download_dir = Path.home() / ".better11" / "updates"
        download_dir.mkdir(parents=True, exist_ok=True)
        
        download_path = download_dir / f"better11-{version}.zip"
        
        _LOGGER.info("Downloading Better11 update to %s", download_path)
        
        response = requests.get(update_info.download_url, stream=True, timeout=60)
        response.raise_for_status()
        
        with open(download_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        _LOGGER.info("Downloaded Better11 update: %s", download_path)
        return download_path
    
    def install_update(self, package_path: Path) -> bool:
        """Install Better11 update.
        
        Note: On Windows, this requires replacing files on restart.
        
        Parameters
        ----------
        package_path : Path
            Path to update package
        
        Returns
        -------
        bool
            True if installation initiated successfully
        """
        _LOGGER.info("Installing Better11 update from %s", package_path)
        
        # On Windows, we need to schedule file replacement on restart
        # This is a simplified implementation
        # In production, you'd use MoveFileEx with MOVEFILE_DELAY_UNTIL_REBOOT
        
        import platform
        if platform.system() == "Windows":
            _LOGGER.warning(
                "Better11 self-update requires restart. "
                "Please extract %s and replace Better11 files manually, then restart.",
                package_path
            )
            # TODO: Implement proper Windows file replacement on restart
            return False
        else:
            # On Unix-like systems, can replace files directly
            _LOGGER.warning("Better11 self-update not fully implemented for this platform")
            return False
    
    def rollback_update(self) -> bool:
        """Rollback to previous Better11 version.
        
        Returns
        -------
        bool
            True if rollback successful
        """
        _LOGGER.warning("Better11 rollback not yet implemented")
        return False


__all__ = [
    "UpdateInfo",
    "ApplicationUpdater",
    "Better11Updater",
]
