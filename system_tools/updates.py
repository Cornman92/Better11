"""Windows Update management.

This module provides control over Windows Update behavior including
checking for updates, pausing updates, and configuring update settings.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional

from . import get_logger
from .base import SystemTool, ToolMetadata

_LOGGER = get_logger(__name__)


class UpdateType(Enum):
    """Type of Windows update."""
    
    CRITICAL = "critical"
    SECURITY = "security"
    DEFINITION = "definition"
    FEATURE = "feature"
    DRIVER = "driver"
    OTHER = "other"


class UpdateStatus(Enum):
    """Status of a Windows update."""
    
    AVAILABLE = "available"
    DOWNLOADING = "downloading"
    PENDING_INSTALL = "pending_install"
    INSTALLED = "installed"
    FAILED = "failed"


@dataclass
class WindowsUpdate:
    """Representation of a Windows update."""
    
    id: str
    title: str
    description: str
    update_type: UpdateType
    size_mb: float
    status: UpdateStatus
    kb_article: Optional[str] = None
    support_url: Optional[str] = None
    is_mandatory: bool = False
    requires_restart: bool = False
    install_date: Optional[datetime] = None


class WindowsUpdateManager(SystemTool):
    """Manage Windows Update settings and operations.
    
    This class provides methods to check for updates, install updates,
    pause updates, configure active hours, and manage update settings.
    
    Parameters
    ----------
    config : dict, optional
        Configuration dictionary
    dry_run : bool
        If True, simulate operations without making changes
    """
    
    def __init__(self, config: Optional[dict] = None, dry_run: bool = False):
        super().__init__(config, dry_run)
    
    def get_metadata(self) -> ToolMetadata:
        """Return tool metadata."""
        return ToolMetadata(
            name="Windows Update Manager",
            description="Manage Windows Update settings and operations",
            version="0.3.0",
            requires_admin=True,
            requires_restart=False,
            category="updates"
        )
    
    def validate_environment(self) -> None:
        """Validate Windows Update service is available."""
        # TODO: Check Windows Update service status
        pass
    
    def execute(self) -> bool:
        """Execute default update check operation."""
        updates = self.check_for_updates()
        _LOGGER.info("Found %d available updates", len(updates))
        return True
    
    def check_for_updates(self) -> List[WindowsUpdate]:
        """Check for available Windows updates.

        Returns
        -------
        List[WindowsUpdate]
            List of available updates
        """
        _LOGGER.info("Checking for Windows updates...")

        if self._dry_run:
            _LOGGER.info("[DRY RUN] Would check for Windows updates")
            return []

        try:
            import platform
            if platform.system() != "Windows":
                _LOGGER.warning("Windows Update checking only supported on Windows")
                return []

            import subprocess
            import json

            # Use Windows Update COM API via PowerShell
            script = '''
            $UpdateSession = New-Object -ComObject Microsoft.Update.Session
            $UpdateSearcher = $UpdateSession.CreateUpdateSearcher()
            $SearchResult = $UpdateSearcher.Search("IsInstalled=0 and Type='Software'")

            $updates = @()
            foreach ($Update in $SearchResult.Updates) {
                $updates += @{
                    Title = $Update.Title
                    Description = $Update.Description
                    SizeInMB = [math]::Round($Update.MaxDownloadSize / 1MB, 2)
                    IsDownloaded = $Update.IsDownloaded
                    IsMandatory = $Update.IsMandatory
                    RebootRequired = $Update.RebootRequired
                    KBArticleIDs = $Update.KBArticleIDs -join ","
                    SupportUrl = $Update.SupportUrl
                }
            }
            $updates | ConvertTo-Json -Depth 3
            '''

            result = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
                capture_output=True,
                text=True,
                timeout=120  # 2 minutes timeout
            )

            if result.returncode != 0:
                _LOGGER.error("PowerShell error checking for updates: %s", result.stderr)
                return []

            if not result.stdout.strip():
                _LOGGER.info("No updates available")
                return []

            updates_data = json.loads(result.stdout)
            if not isinstance(updates_data, list):
                updates_data = [updates_data]

            updates = []
            for update_data in updates_data:
                kb = update_data.get("KBArticleIDs", "")
                kb_article = f"KB{kb}" if kb else None

                update = WindowsUpdate(
                    id=kb_article or update_data.get("Title", "")[:50],
                    title=update_data.get("Title", "Unknown Update"),
                    description=update_data.get("Description", ""),
                    update_type=self._determine_update_type(update_data.get("Title", "")),
                    size_mb=update_data.get("SizeInMB", 0.0),
                    status=UpdateStatus.DOWNLOADING if update_data.get("IsDownloaded") else UpdateStatus.AVAILABLE,
                    kb_article=kb_article,
                    support_url=update_data.get("SupportUrl"),
                    is_mandatory=update_data.get("IsMandatory", False),
                    requires_restart=update_data.get("RebootRequired", False)
                )
                updates.append(update)

            _LOGGER.info("Found %d available updates", len(updates))
            return updates

        except subprocess.TimeoutExpired:
            _LOGGER.error("Timeout while checking for updates")
            return []
        except json.JSONDecodeError:
            _LOGGER.error("Failed to parse update data")
            return []
        except Exception as exc:
            _LOGGER.error("Failed to check for updates: %s", exc)
            return []

    def _determine_update_type(self, title: str) -> UpdateType:
        """Determine update type from title.

        Parameters
        ----------
        title : str
            Update title

        Returns
        -------
        UpdateType
            Determined update type
        """
        title_lower = title.lower()
        if "security" in title_lower:
            return UpdateType.SECURITY
        elif "critical" in title_lower:
            return UpdateType.CRITICAL
        elif "definition" in title_lower or "defender" in title_lower:
            return UpdateType.DEFINITION
        elif "feature" in title_lower or "version" in title_lower:
            return UpdateType.FEATURE
        elif "driver" in title_lower:
            return UpdateType.DRIVER
        else:
            return UpdateType.OTHER
    
    def install_updates(self, update_ids: Optional[List[str]] = None) -> bool:
        """Install specific updates or all available updates.
        
        Parameters
        ----------
        update_ids : List[str], optional
            List of update IDs to install. If None, install all.
        
        Returns
        -------
        bool
            True if installation successful
        """
        # TODO: Implement update installation
        raise NotImplementedError("Update installation - coming in v0.3.0")
    
    def pause_updates(self, days: int = 7) -> bool:
        """Pause Windows updates for specified number of days.

        Parameters
        ----------
        days : int
            Number of days to pause updates (max 35)

        Returns
        -------
        bool
            True if successful
        """
        if days > 35:
            raise ValueError("Cannot pause updates for more than 35 days")

        _LOGGER.info("Pausing updates for %d days", days)

        if self._dry_run:
            _LOGGER.info("[DRY RUN] Would pause updates for %d days", days)
            return True

        try:
            import platform
            if platform.system() != "Windows":
                _LOGGER.error("Windows Update control only supported on Windows")
                return False

            import winreg

            # Calculate pause expiry time
            expiry_time = datetime.now() + timedelta(days=days)
            # Convert to Windows file time format (100-nanosecond intervals since 1601-01-01)
            epoch = datetime(1601, 1, 1)
            delta = expiry_time - epoch
            file_time = int(delta.total_seconds() * 10000000)

            # Set pause expiry in registry
            key_path = r"SOFTWARE\Microsoft\WindowsUpdate\UX\Settings"

            try:
                key = winreg.CreateKeyEx(
                    winreg.HKEY_LOCAL_MACHINE,
                    key_path,
                    0,
                    winreg.KEY_WRITE
                )

                # Set pause expiry times for both feature and quality updates
                winreg.SetValueEx(key, "PauseFeatureUpdatesStartTime", 0, winreg.REG_SZ,
                                 datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"))
                winreg.SetValueEx(key, "PauseFeatureUpdatesEndTime", 0, winreg.REG_SZ,
                                 expiry_time.strftime("%Y-%m-%dT%H:%M:%SZ"))
                winreg.SetValueEx(key, "PauseQualityUpdatesStartTime", 0, winreg.REG_SZ,
                                 datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"))
                winreg.SetValueEx(key, "PauseQualityUpdatesEndTime", 0, winreg.REG_SZ,
                                 expiry_time.strftime("%Y-%m-%dT%H:%M:%SZ"))
                winreg.SetValueEx(key, "PauseUpdatesExpiryTime", 0, winreg.REG_SZ,
                                 expiry_time.strftime("%Y-%m-%dT%H:%M:%SZ"))

                winreg.CloseKey(key)

                _LOGGER.info("Successfully paused updates until %s", expiry_time.strftime("%Y-%m-%d"))
                return True

            except PermissionError:
                _LOGGER.error("Insufficient permissions to pause updates. Run as administrator.")
                return False

        except Exception as exc:
            _LOGGER.error("Failed to pause updates: %s", exc)
            return False
    
    def resume_updates(self) -> bool:
        """Resume Windows updates if paused.

        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Resuming Windows updates")

        if self._dry_run:
            _LOGGER.info("[DRY RUN] Would resume Windows updates")
            return True

        try:
            import platform
            if platform.system() != "Windows":
                _LOGGER.error("Windows Update control only supported on Windows")
                return False

            import winreg

            key_path = r"SOFTWARE\Microsoft\WindowsUpdate\UX\Settings"

            try:
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    key_path,
                    0,
                    winreg.KEY_WRITE
                )

                # Delete pause-related registry values
                pause_keys = [
                    "PauseFeatureUpdatesStartTime",
                    "PauseFeatureUpdatesEndTime",
                    "PauseQualityUpdatesStartTime",
                    "PauseQualityUpdatesEndTime",
                    "PauseUpdatesExpiryTime"
                ]

                for pause_key in pause_keys:
                    try:
                        winreg.DeleteValue(key, pause_key)
                    except FileNotFoundError:
                        # Key doesn't exist, that's fine
                        pass

                winreg.CloseKey(key)

                _LOGGER.info("Successfully resumed Windows updates")
                return True

            except PermissionError:
                _LOGGER.error("Insufficient permissions to resume updates. Run as administrator.")
                return False
            except FileNotFoundError:
                _LOGGER.warning("Update settings registry key not found")
                return False

        except Exception as exc:
            _LOGGER.error("Failed to resume updates: %s", exc)
            return False
    
    def set_active_hours(self, start_hour: int, end_hour: int) -> bool:
        """Set active hours to prevent restart interruptions.

        Parameters
        ----------
        start_hour : int
            Start hour (0-23)
        end_hour : int
            End hour (0-23)

        Returns
        -------
        bool
            True if successful
        """
        if not (0 <= start_hour <= 23 and 0 <= end_hour <= 23):
            raise ValueError("Hours must be between 0 and 23")

        _LOGGER.info("Setting active hours: %d:00 - %d:00", start_hour, end_hour)

        if self._dry_run:
            _LOGGER.info("[DRY RUN] Would set active hours to %d:00 - %d:00", start_hour, end_hour)
            return True

        try:
            import platform
            if platform.system() != "Windows":
                _LOGGER.error("Windows Update control only supported on Windows")
                return False

            import winreg

            key_path = r"SOFTWARE\Microsoft\WindowsUpdate\UX\Settings"

            try:
                key = winreg.CreateKeyEx(
                    winreg.HKEY_LOCAL_MACHINE,
                    key_path,
                    0,
                    winreg.KEY_WRITE
                )

                # Set active hours
                winreg.SetValueEx(key, "ActiveHoursStart", 0, winreg.REG_DWORD, start_hour)
                winreg.SetValueEx(key, "ActiveHoursEnd", 0, winreg.REG_DWORD, end_hour)

                winreg.CloseKey(key)

                _LOGGER.info("Successfully set active hours: %d:00 - %d:00", start_hour, end_hour)
                return True

            except PermissionError:
                _LOGGER.error("Insufficient permissions to set active hours. Run as administrator.")
                return False

        except Exception as exc:
            _LOGGER.error("Failed to set active hours: %s", exc)
            return False
    
    def get_update_history(self, days: int = 30) -> List[WindowsUpdate]:
        """Get Windows update installation history.

        Parameters
        ----------
        days : int
            Number of days of history to retrieve

        Returns
        -------
        List[WindowsUpdate]
            List of installed updates
        """
        _LOGGER.info("Retrieving update history for last %d days", days)

        try:
            import platform
            if platform.system() != "Windows":
                _LOGGER.warning("Windows Update history only supported on Windows")
                return []

            import subprocess
            import json

            # Calculate cutoff date
            cutoff_date = datetime.now() - timedelta(days=days)

            # Use Windows Update COM API to get history
            script = f'''
            $UpdateSession = New-Object -ComObject Microsoft.Update.Session
            $UpdateSearcher = $UpdateSession.CreateUpdateSearcher()
            $HistoryCount = $UpdateSearcher.GetTotalHistoryCount()
            $History = $UpdateSearcher.QueryHistory(0, $HistoryCount)

            $CutoffDate = (Get-Date).AddDays(-{days})

            $updates = @()
            foreach ($Entry in $History) {{
                if ($Entry.Date -ge $CutoffDate) {{
                    $updates += @{{
                        Title = $Entry.Title
                        Description = $Entry.Description
                        Date = $Entry.Date.ToString("o")
                        ResultCode = $Entry.ResultCode
                        KBArticleIDs = ($Entry.Update.KBArticleIDs -join ",")
                        SupportUrl = $Entry.Update.SupportUrl
                    }}
                }}
            }}
            $updates | ConvertTo-Json -Depth 3
            '''

            result = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                _LOGGER.error("PowerShell error retrieving update history: %s", result.stderr)
                return []

            if not result.stdout.strip():
                _LOGGER.info("No update history found")
                return []

            history_data = json.loads(result.stdout)
            if not isinstance(history_data, list):
                history_data = [history_data]

            updates = []
            for entry_data in history_data:
                kb = entry_data.get("KBArticleIDs", "")
                kb_article = f"KB{kb}" if kb else None

                # ResultCode: 2 = Succeeded, 3 = Succeeded with errors, others = failed
                result_code = entry_data.get("ResultCode", 0)
                status = UpdateStatus.INSTALLED if result_code in [2, 3] else UpdateStatus.FAILED

                update = WindowsUpdate(
                    id=kb_article or entry_data.get("Title", "")[:50],
                    title=entry_data.get("Title", "Unknown Update"),
                    description=entry_data.get("Description", ""),
                    update_type=self._determine_update_type(entry_data.get("Title", "")),
                    size_mb=0.0,  # Size not available in history
                    status=status,
                    kb_article=kb_article,
                    support_url=entry_data.get("SupportUrl"),
                    install_date=datetime.fromisoformat(entry_data.get("Date", "")) if entry_data.get("Date") else None
                )
                updates.append(update)

            _LOGGER.info("Retrieved %d updates from history", len(updates))
            return updates

        except subprocess.TimeoutExpired:
            _LOGGER.error("Timeout while retrieving update history")
            return []
        except json.JSONDecodeError:
            _LOGGER.error("Failed to parse update history data")
            return []
        except Exception as exc:
            _LOGGER.error("Failed to retrieve update history: %s", exc)
            return []
    
    def uninstall_update(self, kb_article: str) -> bool:
        """Uninstall a specific update by KB number.

        Parameters
        ----------
        kb_article : str
            KB article number (e.g., "KB5000001")

        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Uninstalling update %s", kb_article)

        if self._dry_run:
            _LOGGER.info("[DRY RUN] Would uninstall update %s", kb_article)
            return True

        try:
            import platform
            if platform.system() != "Windows":
                _LOGGER.error("Windows Update uninstall only supported on Windows")
                return False

            import subprocess

            # Normalize KB article format
            if not kb_article.upper().startswith("KB"):
                kb_article = f"KB{kb_article}"

            # Use WUSA.exe to uninstall the update
            # Note: Requires administrator privileges and may require restart
            command = ["wusa.exe", f"/uninstall /kb:{kb_article[2:]}", "/quiet", "/norestart"]

            _LOGGER.info("Executing: %s", " ".join(command))

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )

            if result.returncode == 0:
                _LOGGER.info("Successfully uninstalled update %s", kb_article)
                return True
            elif result.returncode == 2359302:  # Update not found
                _LOGGER.warning("Update %s not found or already uninstalled", kb_article)
                return False
            elif result.returncode == 3010:  # Restart required
                _LOGGER.warning("Update %s uninstalled, restart required", kb_article)
                return True
            else:
                _LOGGER.error("Failed to uninstall update %s: exit code %d", kb_article, result.returncode)
                if result.stderr:
                    _LOGGER.error("Error output: %s", result.stderr)
                return False

        except subprocess.TimeoutExpired:
            _LOGGER.error("Timeout while uninstalling update %s", kb_article)
            return False
        except PermissionError:
            _LOGGER.error("Insufficient permissions to uninstall update. Run as administrator.")
            return False
        except Exception as exc:
            _LOGGER.error("Failed to uninstall update %s: %s", kb_article, exc)
            return False


__all__ = [
    "UpdateType",
    "UpdateStatus",
    "WindowsUpdate",
    "WindowsUpdateManager",
]
