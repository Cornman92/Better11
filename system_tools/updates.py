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
    HIDDEN = "hidden"


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

    @property
    def size_display(self) -> str:
        """Get human-readable size."""
        if self.size_mb >= 1024:
            return f"{self.size_mb / 1024:.2f} GB"
        return f"{self.size_mb:.2f} MB"


@dataclass
class UpdateSettings:
    """Windows Update settings."""
    
    auto_download: bool
    auto_install: bool
    active_hours_start: int
    active_hours_end: int
    pause_until: Optional[datetime]
    last_check: Optional[datetime]
    restart_required: bool


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
    
    # Registry paths for Windows Update
    UPDATE_POLICY_PATH = r"SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate"
    UPDATE_AU_PATH = r"SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU"
    UPDATE_SETTINGS_PATH = r"SOFTWARE\Microsoft\WindowsUpdate\UX\Settings"
    
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
        if platform.system() != "Windows":
            return
        
        try:
            # Check if Windows Update service exists
            result = subprocess.run(
                ["sc", "query", "wuauserv"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                _LOGGER.warning("Windows Update service may not be available")
        except Exception as exc:
            _LOGGER.warning("Could not verify Windows Update service: %s", exc)
    
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
        
        if platform.system() != "Windows":
            _LOGGER.warning("Windows Update checking only available on Windows")
            return []
        
        try:
            # Use PowerShell to check for updates via Windows Update API
            ps_script = '''
            $Session = New-Object -ComObject Microsoft.Update.Session
            $Searcher = $Session.CreateUpdateSearcher()
            
            try {
                $SearchResult = $Searcher.Search("IsInstalled=0 and IsHidden=0")
                $Updates = @()
                
                foreach ($Update in $SearchResult.Updates) {
                    $KBArticle = ""
                    if ($Update.KBArticleIDs.Count -gt 0) {
                        $KBArticle = "KB" + $Update.KBArticleIDs.Item(0)
                    }
                    
                    $SupportUrl = ""
                    if ($Update.MoreInfoUrls.Count -gt 0) {
                        $SupportUrl = $Update.MoreInfoUrls.Item(0)
                    }
                    
                    $UpdateType = "Other"
                    if ($Update.Categories.Count -gt 0) {
                        $Category = $Update.Categories.Item(0).Name
                        if ($Category -like "*Security*") { $UpdateType = "Security" }
                        elseif ($Category -like "*Critical*") { $UpdateType = "Critical" }
                        elseif ($Category -like "*Definition*") { $UpdateType = "Definition" }
                        elseif ($Category -like "*Driver*") { $UpdateType = "Driver" }
                        elseif ($Category -like "*Feature*") { $UpdateType = "Feature" }
                    }
                    
                    $Updates += @{
                        Id = $Update.Identity.UpdateID
                        Title = $Update.Title
                        Description = $Update.Description
                        UpdateType = $UpdateType
                        SizeMB = [math]::Round($Update.MaxDownloadSize / 1MB, 2)
                        KBArticle = $KBArticle
                        SupportUrl = $SupportUrl
                        IsMandatory = $Update.IsMandatory
                        RequiresRestart = $Update.RebootRequired
                        IsDownloaded = $Update.IsDownloaded
                    }
                }
                
                $Updates | ConvertTo-Json -Depth 10
            }
            catch {
                @() | ConvertTo-Json
            }
            '''
            
            result = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=120  # Updates check can take a while
            )
            
            if result.returncode != 0:
                _LOGGER.error("Failed to check for updates: %s", result.stderr)
                return []
            
            output = result.stdout.strip()
            if not output or output == "null":
                return []
            
            data = json.loads(output)
            if not isinstance(data, list):
                data = [data] if data else []
            
            updates = []
            for item in data:
                update_type = UpdateType.OTHER
                try:
                    update_type = UpdateType(item.get("UpdateType", "Other").lower())
                except ValueError:
                    pass
                
                status = UpdateStatus.AVAILABLE
                if item.get("IsDownloaded"):
                    status = UpdateStatus.PENDING_INSTALL
                
                updates.append(WindowsUpdate(
                    id=item.get("Id", ""),
                    title=item.get("Title", "Unknown"),
                    description=item.get("Description", ""),
                    update_type=update_type,
                    size_mb=float(item.get("SizeMB", 0)),
                    status=status,
                    kb_article=item.get("KBArticle"),
                    support_url=item.get("SupportUrl"),
                    is_mandatory=item.get("IsMandatory", False),
                    requires_restart=item.get("RequiresRestart", False)
                ))
            
            _LOGGER.info("Found %d available updates", len(updates))
            return updates
            
        except subprocess.TimeoutExpired:
            _LOGGER.error("Update check timed out")
            return []
        except json.JSONDecodeError as exc:
            _LOGGER.error("Failed to parse update data: %s", exc)
            return []
        except Exception as exc:
            _LOGGER.error("Failed to check for updates: %s", exc)
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
        _LOGGER.info("Installing Windows updates...")
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would install Windows updates")
            return True
        
        if platform.system() != "Windows":
            _LOGGER.error("Update installation only available on Windows")
            return False
        
        try:
            # Build PowerShell script for installing updates
            filter_clause = ""
            if update_ids:
                ids_json = json.dumps(update_ids)
                filter_clause = f'''
                $FilterIds = {ids_json} | ConvertFrom-Json
                $UpdatesToInstall = New-Object -ComObject Microsoft.Update.UpdateColl
                foreach ($Update in $SearchResult.Updates) {{
                    if ($FilterIds -contains $Update.Identity.UpdateID) {{
                        $UpdatesToInstall.Add($Update) | Out-Null
                    }}
                }}
                '''
            else:
                filter_clause = '''
                $UpdatesToInstall = New-Object -ComObject Microsoft.Update.UpdateColl
                foreach ($Update in $SearchResult.Updates) {
                    if (-not $Update.IsHidden) {
                        $UpdatesToInstall.Add($Update) | Out-Null
                    }
                }
                '''
            
            ps_script = f'''
            $Session = New-Object -ComObject Microsoft.Update.Session
            $Searcher = $Session.CreateUpdateSearcher()
            $SearchResult = $Searcher.Search("IsInstalled=0")
            
            {filter_clause}
            
            if ($UpdatesToInstall.Count -eq 0) {{
                Write-Output '{{"success": true, "message": "No updates to install"}}'
                exit 0
            }}
            
            # Download updates first
            $Downloader = $Session.CreateUpdateDownloader()
            $Downloader.Updates = $UpdatesToInstall
            $DownloadResult = $Downloader.Download()
            
            if ($DownloadResult.ResultCode -ne 2) {{
                Write-Output '{{"success": false, "message": "Download failed"}}'
                exit 1
            }}
            
            # Install updates
            $Installer = $Session.CreateUpdateInstaller()
            $Installer.Updates = $UpdatesToInstall
            $InstallResult = $Installer.Install()
            
            $Result = @{{
                success = ($InstallResult.ResultCode -eq 2)
                rebootRequired = $InstallResult.RebootRequired
                updatesInstalled = $UpdatesToInstall.Count
                message = if ($InstallResult.ResultCode -eq 2) {{ "Installation successful" }} else {{ "Installation completed with warnings" }}
            }}
            
            $Result | ConvertTo-Json
            '''
            
            result = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=3600  # Updates can take a long time
            )
            
            if result.returncode != 0:
                _LOGGER.error("Update installation failed: %s", result.stderr)
                return False
            
            try:
                data = json.loads(result.stdout)
                if data.get("success"):
                    _LOGGER.info("Updates installed successfully. Reboot required: %s", 
                                data.get("rebootRequired", False))
                    return True
                else:
                    _LOGGER.error("Update installation failed: %s", data.get("message"))
                    return False
            except json.JSONDecodeError:
                _LOGGER.info("Update installation completed")
                return True
        
        except subprocess.TimeoutExpired:
            _LOGGER.error("Update installation timed out")
            return False
        except Exception as exc:
            _LOGGER.error("Failed to install updates: %s", exc)
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
        
        if days < 1:
            raise ValueError("Days must be at least 1")
        
        _LOGGER.info("Pausing updates for %d days", days)
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would pause updates for %d days", days)
            return True
        
        if platform.system() != "Windows":
            _LOGGER.error("Update pause only available on Windows")
            return False
        
        try:
            # Calculate pause until date
            pause_until = datetime.now() + timedelta(days=days)
            pause_until_str = pause_until.strftime("%Y-%m-%dT%H:%M:%SZ")
            
            # Set pause via registry
            ps_script = f'''
            $RegPath = "HKLM:\\SOFTWARE\\Microsoft\\WindowsUpdate\\UX\\Settings"
            
            # Ensure the key exists
            if (-not (Test-Path $RegPath)) {{
                New-Item -Path $RegPath -Force | Out-Null
            }}
            
            # Set pause feature updates
            Set-ItemProperty -Path $RegPath -Name "PauseFeatureUpdatesStartTime" -Value (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
            Set-ItemProperty -Path $RegPath -Name "PauseFeatureUpdatesEndTime" -Value "{pause_until_str}"
            
            # Set pause quality updates
            Set-ItemProperty -Path $RegPath -Name "PauseQualityUpdatesStartTime" -Value (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
            Set-ItemProperty -Path $RegPath -Name "PauseQualityUpdatesEndTime" -Value "{pause_until_str}"
            
            # Set pause state
            Set-ItemProperty -Path $RegPath -Name "PauseUpdatesExpiryTime" -Value "{pause_until_str}"
            Set-ItemProperty -Path $RegPath -Name "PauseUpdatesStartTime" -Value (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
            
            Write-Output "Paused"
            '''
            
            result = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                _LOGGER.info("Updates paused until %s", pause_until.strftime("%Y-%m-%d"))
                return True
            else:
                _LOGGER.error("Failed to pause updates: %s", result.stderr)
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
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would resume updates")
            return True
        
        if platform.system() != "Windows":
            _LOGGER.error("Update resume only available on Windows")
            return False
        
        try:
            ps_script = '''
            $RegPath = "HKLM:\\SOFTWARE\\Microsoft\\WindowsUpdate\\UX\\Settings"
            
            # Remove pause settings
            $PropertiesToRemove = @(
                "PauseFeatureUpdatesStartTime",
                "PauseFeatureUpdatesEndTime",
                "PauseQualityUpdatesStartTime",
                "PauseQualityUpdatesEndTime",
                "PauseUpdatesExpiryTime",
                "PauseUpdatesStartTime"
            )
            
            foreach ($Property in $PropertiesToRemove) {
                try {
                    Remove-ItemProperty -Path $RegPath -Name $Property -ErrorAction SilentlyContinue
                } catch {}
            }
            
            Write-Output "Resumed"
            '''
            
            result = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                _LOGGER.info("Updates resumed successfully")
                return True
            else:
                _LOGGER.error("Failed to resume updates: %s", result.stderr)
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
        
        # Calculate span (max 18 hours)
        if end_hour > start_hour:
            span = end_hour - start_hour
        else:
            span = (24 - start_hour) + end_hour
        
        if span > 18:
            raise ValueError("Active hours span cannot exceed 18 hours")
        
        _LOGGER.info("Setting active hours: %d:00 - %d:00", start_hour, end_hour)
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would set active hours")
            return True
        
        if platform.system() != "Windows":
            _LOGGER.error("Active hours only available on Windows")
            return False
        
        try:
            ps_script = f'''
            $RegPath = "HKLM:\\SOFTWARE\\Microsoft\\WindowsUpdate\\UX\\Settings"
            
            # Ensure the key exists
            if (-not (Test-Path $RegPath)) {{
                New-Item -Path $RegPath -Force | Out-Null
            }}
            
            # Set active hours
            Set-ItemProperty -Path $RegPath -Name "ActiveHoursStart" -Value {start_hour} -Type DWord
            Set-ItemProperty -Path $RegPath -Name "ActiveHoursEnd" -Value {end_hour} -Type DWord
            Set-ItemProperty -Path $RegPath -Name "IsActiveHoursEnabled" -Value 1 -Type DWord
            
            Write-Output "Active hours set"
            '''
            
            result = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                _LOGGER.info("Active hours set successfully")
                return True
            else:
                _LOGGER.error("Failed to set active hours: %s", result.stderr)
                return False
        
        except Exception as exc:
            _LOGGER.error("Failed to set active hours: %s", exc)
            return False
    
    def get_active_hours(self) -> tuple[int, int]:
        """Get current active hours settings.
        
        Returns
        -------
        tuple[int, int]
            Start hour and end hour
        """
        if platform.system() != "Windows":
            return (8, 17)  # Default
        
        try:
            ps_script = '''
            $RegPath = "HKLM:\\SOFTWARE\\Microsoft\\WindowsUpdate\\UX\\Settings"
            
            $Start = 8
            $End = 17
            
            try {
                $Start = (Get-ItemProperty -Path $RegPath -Name "ActiveHoursStart" -ErrorAction SilentlyContinue).ActiveHoursStart
                $End = (Get-ItemProperty -Path $RegPath -Name "ActiveHoursEnd" -ErrorAction SilentlyContinue).ActiveHoursEnd
            } catch {}
            
            @{Start = $Start; End = $End} | ConvertTo-Json
            '''
            
            result = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return (int(data.get("Start", 8)), int(data.get("End", 17)))
        
        except Exception:
            pass
        
        return (8, 17)
    
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
        _LOGGER.info("Getting update history for last %d days", days)
        
        if platform.system() != "Windows":
            _LOGGER.warning("Update history only available on Windows")
            return []
        
        try:
            # Use raw string to avoid escape sequence warnings
            ps_script = r'''
            $Session = New-Object -ComObject Microsoft.Update.Session
            $Searcher = $Session.CreateUpdateSearcher()
            $HistoryCount = $Searcher.GetTotalHistoryCount()
            
            if ($HistoryCount -eq 0) {
                @() | ConvertTo-Json
                exit 0
            }
            
            $History = $Searcher.QueryHistory(0, $HistoryCount)
            $CutoffDate = (Get-Date).AddDays(-''' + str(days) + r''')
            
            $Updates = @()
            foreach ($Entry in $History) {
                if ($Entry.Date -lt $CutoffDate) { continue }
                
                $KBMatch = [regex]::Match($Entry.Title, "KB(\d+)")
                $KBArticle = if ($KBMatch.Success) { "KB" + $KBMatch.Groups[1].Value } else { "" }
                
                $Updates += @{
                    Id = $Entry.UpdateIdentity.UpdateID
                    Title = $Entry.Title
                    Description = $Entry.Description
                    InstallDate = $Entry.Date.ToString("o")
                    Status = switch ($Entry.ResultCode) {
                        0 { "NotStarted" }
                        1 { "InProgress" }
                        2 { "Installed" }
                        3 { "InstalledWithErrors" }
                        4 { "Failed" }
                        5 { "Aborted" }
                        default { "Unknown" }
                    }
                    KBArticle = $KBArticle
                    SupportUrl = $Entry.SupportUrl
                }
            }
            
            $Updates | ConvertTo-Json -Depth 10
            '''
            
            result = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                _LOGGER.error("Failed to get update history: %s", result.stderr)
                return []
            
            output = result.stdout.strip()
            if not output or output == "null":
                return []
            
            data = json.loads(output)
            if not isinstance(data, list):
                data = [data] if data else []
            
            updates = []
            for item in data:
                status = UpdateStatus.INSTALLED
                status_str = item.get("Status", "Unknown").lower()
                if status_str == "failed":
                    status = UpdateStatus.FAILED
                elif status_str == "inprogress":
                    status = UpdateStatus.DOWNLOADING
                
                install_date = None
                if item.get("InstallDate"):
                    try:
                        install_date = datetime.fromisoformat(item["InstallDate"].replace("Z", "+00:00"))
                    except ValueError:
                        pass
                
                updates.append(WindowsUpdate(
                    id=item.get("Id", ""),
                    title=item.get("Title", "Unknown"),
                    description=item.get("Description", ""),
                    update_type=UpdateType.OTHER,
                    size_mb=0,
                    status=status,
                    kb_article=item.get("KBArticle"),
                    support_url=item.get("SupportUrl"),
                    install_date=install_date
                ))
            
            _LOGGER.info("Found %d updates in history", len(updates))
            return updates
        
        except Exception as exc:
            _LOGGER.error("Failed to get update history: %s", exc)
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
        # Normalize KB article format
        if not kb_article.upper().startswith("KB"):
            kb_article = "KB" + kb_article
        
        _LOGGER.info("Uninstalling update %s", kb_article)
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would uninstall update %s", kb_article)
            return True
        
        if platform.system() != "Windows":
            _LOGGER.error("Update uninstall only available on Windows")
            return False
        
        try:
            # Use WUSA to uninstall
            result = subprocess.run(
                ["wusa", "/uninstall", f"/kb:{kb_article[2:]}", "/quiet", "/norestart"],
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode == 0:
                _LOGGER.info("Update %s uninstalled successfully", kb_article)
                return True
            elif result.returncode == 3010:
                _LOGGER.info("Update %s uninstalled. Restart required.", kb_article)
                return True
            elif result.returncode == 2359303:
                _LOGGER.warning("Update %s is not installed", kb_article)
                return False
            else:
                _LOGGER.error("Failed to uninstall update. Return code: %d", result.returncode)
                return False
        
        except subprocess.TimeoutExpired:
            _LOGGER.error("Update uninstall timed out")
            return False
        except Exception as exc:
            _LOGGER.error("Failed to uninstall update: %s", exc)
            return False
    
    def hide_update(self, update_id: str) -> bool:
        """Hide an update to prevent it from being installed.
        
        Parameters
        ----------
        update_id : str
            Update ID to hide
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Hiding update %s", update_id)
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would hide update %s", update_id)
            return True
        
        if platform.system() != "Windows":
            _LOGGER.error("Update hiding only available on Windows")
            return False
        
        try:
            ps_script = f'''
            $Session = New-Object -ComObject Microsoft.Update.Session
            $Searcher = $Session.CreateUpdateSearcher()
            $SearchResult = $Searcher.Search("IsInstalled=0")
            
            $Found = $false
            foreach ($Update in $SearchResult.Updates) {{
                if ($Update.Identity.UpdateID -eq "{update_id}") {{
                    $Update.IsHidden = $true
                    $Found = $true
                    break
                }}
            }}
            
            if ($Found) {{
                Write-Output "Hidden"
            }} else {{
                Write-Output "NotFound"
            }}
            '''
            
            result = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0 and "Hidden" in result.stdout:
                _LOGGER.info("Update hidden successfully")
                return True
            else:
                _LOGGER.error("Failed to hide update")
                return False
        
        except Exception as exc:
            _LOGGER.error("Failed to hide update: %s", exc)
            return False
    
    def get_update_settings(self) -> Optional[UpdateSettings]:
        """Get current Windows Update settings.
        
        Returns
        -------
        UpdateSettings, optional
            Current settings or None if unavailable
        """
        if platform.system() != "Windows":
            return None
        
        try:
            ps_script = '''
            $RegPath = "HKLM:\\SOFTWARE\\Microsoft\\WindowsUpdate\\UX\\Settings"
            
            $Settings = @{
                ActiveHoursStart = 8
                ActiveHoursEnd = 17
                PauseUntil = $null
                RestartRequired = $false
            }
            
            try {
                $Props = Get-ItemProperty -Path $RegPath -ErrorAction SilentlyContinue
                if ($Props.ActiveHoursStart) { $Settings.ActiveHoursStart = $Props.ActiveHoursStart }
                if ($Props.ActiveHoursEnd) { $Settings.ActiveHoursEnd = $Props.ActiveHoursEnd }
                if ($Props.PauseUpdatesExpiryTime) { $Settings.PauseUntil = $Props.PauseUpdatesExpiryTime }
            } catch {}
            
            # Check for pending reboot
            $RebootPending = Test-Path "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\WindowsUpdate\\Auto Update\\RebootRequired"
            $Settings.RestartRequired = $RebootPending
            
            $Settings | ConvertTo-Json
            '''
            
            result = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                
                pause_until = None
                if data.get("PauseUntil"):
                    try:
                        pause_until = datetime.fromisoformat(data["PauseUntil"].replace("Z", "+00:00"))
                    except ValueError:
                        pass
                
                return UpdateSettings(
                    auto_download=True,  # Default Windows 11 behavior
                    auto_install=True,
                    active_hours_start=data.get("ActiveHoursStart", 8),
                    active_hours_end=data.get("ActiveHoursEnd", 17),
                    pause_until=pause_until,
                    last_check=None,  # Not easily available
                    restart_required=data.get("RestartRequired", False)
                )
        
        except Exception as exc:
            _LOGGER.error("Failed to get update settings: %s", exc)
        
        return None


__all__ = [
    "UpdateType",
    "UpdateStatus",
    "WindowsUpdate",
    "UpdateSettings",
    "WindowsUpdateManager",
]
