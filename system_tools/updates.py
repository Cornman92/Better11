"""Windows Update management.

This module provides control over Windows Update behavior including
checking for updates, pausing updates, and configuring update settings.
"""
from __future__ import annotations

import json
import platform
import subprocess
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional

from . import get_logger
from .base import SystemTool, ToolMetadata
from .safety import ensure_windows

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
        ensure_windows()
        
        # Check if Windows Update service exists
        try:
            result = subprocess.run(
                ["sc", "query", "wuauserv"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                _LOGGER.warning("Windows Update service (wuauserv) not found")
        except Exception as e:
            _LOGGER.warning("Could not check Windows Update service: %s", e)
    
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
        ensure_windows()
        _LOGGER.info("Checking for Windows updates...")
        
        try:
            # Try PowerShell Get-WindowsUpdate (Windows 10+)
            ps_command = """
            if (Get-Command Get-WindowsUpdate -ErrorAction SilentlyContinue) {
                $updates = Get-WindowsUpdate -ErrorAction SilentlyContinue
                $updates | ForEach-Object {
                    @{
                        Id = $_.Id.ToString()
                        Title = $_.Title
                        Description = $_.Description
                        UpdateType = $_.UpdateType.ToString()
                        Size = $_.Size / 1MB
                        IsMandatory = $_.IsMandatory
                        RequiresReboot = $_.RebootRequired
                        KBArticle = if ($_.KBArticleIDs) { $_.KBArticleIDs[0] } else { $null }
                    }
                } | ConvertTo-Json
            } else {
                # Fallback: Use Windows Update COM API
                $session = New-Object -ComObject Microsoft.Update.Session
                $searcher = $session.CreateUpdateSearcher()
                $result = $searcher.Search("IsInstalled=0")
                $updates = @()
                foreach ($update in $result.Updates) {
                    $updates += @{
                        Id = $update.Identity.UpdateID
                        Title = $update.Title
                        Description = $update.Description
                        UpdateType = "OTHER"
                        Size = $update.MaxDownloadSize / 1MB
                        IsMandatory = $update.IsMandatory
                        RequiresReboot = $update.InstallationBehavior.RebootBehavior -ne 0
                        KBArticle = ($update.KBArticleIDs | Select-Object -First 1)
                    }
                }
                $updates | ConvertTo-Json
            }
            """
            
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=120  # Update checks can take time
            )
            
            if result.returncode != 0:
                _LOGGER.error("Failed to check for updates: %s", result.stderr)
                return []
            
            if not result.stdout.strip():
                _LOGGER.info("No updates available")
                return []
            
            updates_data = json.loads(result.stdout)
            if not isinstance(updates_data, list):
                updates_data = [updates_data]
            
            updates: List[WindowsUpdate] = []
            for data in updates_data:
                update_type_map = {
                    "CRITICAL": UpdateType.CRITICAL,
                    "SECURITY": UpdateType.SECURITY,
                    "DEFINITION": UpdateType.DEFINITION,
                    "FEATURE": UpdateType.FEATURE,
                    "DRIVER": UpdateType.DRIVER,
                }
                
                update_type = update_type_map.get(
                    data.get("UpdateType", "OTHER").upper(),
                    UpdateType.OTHER
                )
                
                update = WindowsUpdate(
                    id=data.get("Id", ""),
                    title=data.get("Title", "Unknown Update"),
                    description=data.get("Description", ""),
                    update_type=update_type,
                    size_mb=float(data.get("Size", 0)),
                    status=UpdateStatus.AVAILABLE,
                    kb_article=data.get("KBArticle"),
                    is_mandatory=bool(data.get("IsMandatory", False)),
                    requires_restart=bool(data.get("RequiresReboot", False))
                )
                updates.append(update)
            
            _LOGGER.info("Found %d available update(s)", len(updates))
            return updates
            
        except subprocess.TimeoutExpired:
            _LOGGER.error("Update check timed out")
            return []
        except json.JSONDecodeError as e:
            _LOGGER.error("Failed to parse update information: %s", e)
            return []
        except Exception as e:
            _LOGGER.error("Error checking for updates: %s", e)
            return []
    
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
        ensure_windows()
        _LOGGER.info("Installing Windows updates%s", f" (IDs: {update_ids})" if update_ids else " (all)")
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would install updates")
            return True
        
        try:
            # Use PowerShell Install-WindowsUpdate if available
            ps_command = """
            if (Get-Command Install-WindowsUpdate -ErrorAction SilentlyContinue) {
                Install-WindowsUpdate -AcceptAll -AutoReboot:$false -ErrorAction Stop
            } else {
                # Fallback: Use Windows Update COM API
                $session = New-Object -ComObject Microsoft.Update.Session
                $searcher = $session.CreateUpdateSearcher()
                $result = $searcher.Search("IsInstalled=0")
                
                if ($result.Updates.Count -eq 0) {
                    Write-Host "No updates to install"
                    exit 0
                }
                
                $updatesToDownload = New-Object -ComObject Microsoft.Update.UpdateColl
                foreach ($update in $result.Updates) {
                    $updatesToDownload.Add($update) | Out-Null
                }
                
                $downloader = $session.CreateUpdateDownloader()
                $downloader.Updates = $updatesToDownload
                $downloadResult = $downloader.Download()
                
                if ($downloadResult.ResultCode -eq 2) {
                    $updatesToInstall = New-Object -ComObject Microsoft.Update.UpdateColl
                    foreach ($update in $result.Updates) {
                        if ($update.IsDownloaded) {
                            $updatesToInstall.Add($update) | Out-Null
                        }
                    }
                    
                    $installer = $session.CreateUpdateInstaller()
                    $installer.Updates = $updatesToInstall
                    $installResult = $installer.Install()
                    
                    if ($installResult.ResultCode -eq 2) {
                        Write-Host "Updates installed successfully"
                        exit 0
                    } else {
                        Write-Host "Installation failed with code: $($installResult.ResultCode)"
                        exit 1
                    }
                } else {
                    Write-Host "Download failed with code: $($downloadResult.ResultCode)"
                    exit 1
                }
            }
            """
            
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=3600  # Installation can take a long time
            )
            
            if result.returncode == 0:
                _LOGGER.info("Successfully installed Windows updates")
                return True
            else:
                _LOGGER.error("Update installation failed: %s", result.stderr)
                return False
                
        except subprocess.TimeoutExpired:
            _LOGGER.error("Update installation timed out")
            return False
        except Exception as e:
            _LOGGER.error("Error installing updates: %s", e)
            return False
    
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
        
        ensure_windows()
        _LOGGER.info("Pausing updates for %d days", days)
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would pause updates for %d days", days)
            return True
        
        try:
            # Calculate expiry date
            expiry_date = datetime.now() + timedelta(days=days)
            expiry_timestamp = int(expiry_date.timestamp())
            
            # Set registry key to pause updates
            # Windows 10/11: HKLM\SOFTWARE\Microsoft\WindowsUpdate\UX\Settings
            ps_command = f"""
            $regPath = "HKLM:\\SOFTWARE\\Microsoft\\WindowsUpdate\\UX\\Settings"
            if (-not (Test-Path $regPath)) {{
                New-Item -Path $regPath -Force | Out-Null
            }}
            Set-ItemProperty -Path $regPath -Name "PauseUpdatesExpiryTime" -Value {expiry_timestamp} -Type DWord -Force
            """
            
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_command],
                capture_output=True,
                text=True,
                check=True
            )
            
            _LOGGER.info("Successfully paused updates until %s", expiry_date)
            return True
            
        except subprocess.CalledProcessError as e:
            _LOGGER.error("Failed to pause updates: %s", e.stderr)
            return False
        except Exception as e:
            _LOGGER.error("Error pausing updates: %s", e)
            return False
    
    def resume_updates(self) -> bool:
        """Resume Windows updates if paused.
        
        Returns
        -------
        bool
            True if successful
        """
        ensure_windows()
        _LOGGER.info("Resuming Windows updates")
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would resume updates")
            return True
        
        try:
            # Remove pause registry key
            ps_command = """
            $regPath = "HKLM:\\SOFTWARE\\Microsoft\\WindowsUpdate\\UX\\Settings"
            if (Test-Path $regPath) {
                Remove-ItemProperty -Path $regPath -Name "PauseUpdatesExpiryTime" -ErrorAction SilentlyContinue
            }
            """
            
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_command],
                capture_output=True,
                text=True,
                check=True
            )
            
            _LOGGER.info("Successfully resumed Windows updates")
            return True
            
        except subprocess.CalledProcessError as e:
            _LOGGER.error("Failed to resume updates: %s", e.stderr)
            return False
        except Exception as e:
            _LOGGER.error("Error resuming updates: %s", e)
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
        
        ensure_windows()
        _LOGGER.info("Setting active hours: %d:00 - %d:00", start_hour, end_hour)
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would set active hours: %d:00 - %d:00", start_hour, end_hour)
            return True
        
        try:
            # Set active hours via registry
            # Windows 10/11: HKLM\SOFTWARE\Microsoft\WindowsUpdate\UX\Settings
            ps_command = f"""
            $regPath = "HKLM:\\SOFTWARE\\Microsoft\\WindowsUpdate\\UX\\Settings"
            if (-not (Test-Path $regPath)) {{
                New-Item -Path $regPath -Force | Out-Null
            }}
            Set-ItemProperty -Path $regPath -Name "ActiveHoursStart" -Value {start_hour} -Type DWord -Force
            Set-ItemProperty -Path $regPath -Name "ActiveHoursEnd" -Value {end_hour} -Type DWord -Force
            Set-ItemProperty -Path $regPath -Name "IsActiveHoursEnabled" -Value 1 -Type DWord -Force
            """
            
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_command],
                capture_output=True,
                text=True,
                check=True
            )
            
            _LOGGER.info("Successfully set active hours: %d:00 - %d:00", start_hour, end_hour)
            return True
            
        except subprocess.CalledProcessError as e:
            _LOGGER.error("Failed to set active hours: %s", e.stderr)
            return False
        except Exception as e:
            _LOGGER.error("Error setting active hours: %s", e)
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
        ensure_windows()
        _LOGGER.info("Retrieving update history for last %d days", days)
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            ps_command = f"""
            $session = New-Object -ComObject Microsoft.Update.Session
            $searcher = $session.CreateUpdateSearcher()
            $cutoffDate = [DateTime]::Now.AddDays(-{days})
            $historyCount = $searcher.GetTotalHistoryCount()
            
            if ($historyCount -eq 0) {{
                Write-Host "[]"
                exit 0
            }}
            
            $history = $searcher.QueryHistory(0, $historyCount)
            $updates = @()
            
            foreach ($entry in $history) {{
                if ($entry.Date -ge $cutoffDate) {{
                    $updates += @{{
                        Id = $entry.UpdateIdentity.UpdateID
                        Title = $entry.Title
                        Description = $entry.Description
                        InstallDate = $entry.Date.ToString("o")
                        ResultCode = $entry.ResultCode
                        KBArticle = if ($entry.UpdateIdentity.UpdateID -match 'KB\\d+') { $matches[0] } else { $null }
                    }}
                }}
            }}
            
            $updates | ConvertTo-Json
            """
            
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0 or not result.stdout.strip():
                _LOGGER.warning("No update history found")
                return []
            
            updates_data = json.loads(result.stdout)
            if not isinstance(updates_data, list):
                updates_data = [updates_data]
            
            updates: List[WindowsUpdate] = []
            for data in updates_data:
                # ResultCode 2 = Installed successfully
                status = UpdateStatus.INSTALLED if data.get("ResultCode") == 2 else UpdateStatus.FAILED
                
                update = WindowsUpdate(
                    id=data.get("Id", ""),
                    title=data.get("Title", "Unknown Update"),
                    description=data.get("Description", ""),
                    update_type=UpdateType.OTHER,
                    size_mb=0.0,
                    status=status,
                    kb_article=data.get("KBArticle"),
                    install_date=datetime.fromisoformat(data.get("InstallDate", "").replace('Z', '+00:00')) if data.get("InstallDate") else None
                )
                updates.append(update)
            
            _LOGGER.info("Retrieved %d update(s) from history", len(updates))
            return updates
            
        except Exception as e:
            _LOGGER.error("Error retrieving update history: %s", e)
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
        ensure_windows()
        _LOGGER.info("Uninstalling update %s", kb_article)
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would uninstall update %s", kb_article)
            return True
        
        try:
            # Use wusa.exe to uninstall update
            # Format: wusa.exe /uninstall /kb:KB5000001 /quiet /norestart
            kb_number = kb_article.replace("KB", "").replace("kb", "")
            
            result = subprocess.run(
                ["wusa.exe", "/uninstall", f"/kb:{kb_number}", "/quiet", "/norestart"],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0 or result.returncode == 3010:  # 3010 = success but restart required
                _LOGGER.info("Successfully uninstalled update %s", kb_article)
                return True
            else:
                _LOGGER.error("Failed to uninstall update %s: %s", kb_article, result.stderr)
                return False
                
        except subprocess.TimeoutExpired:
            _LOGGER.error("Uninstall operation timed out")
            return False
        except FileNotFoundError:
            _LOGGER.error("wusa.exe not found. This may not be available on this Windows version.")
            return False
        except Exception as e:
            _LOGGER.error("Error uninstalling update: %s", e)
            return False


__all__ = [
    "UpdateType",
    "UpdateStatus",
    "WindowsUpdate",
    "WindowsUpdateManager",
]
