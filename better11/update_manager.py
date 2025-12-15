"""
Windows Update Manager Module

Provides comprehensive Windows Update management:
- Check for updates
- Download and install updates
- Manage update settings
- Control automatic updates
- View update history
- Uninstall updates
- WSUS integration
"""

import os
import subprocess
import json
import winreg
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import tempfile


class UpdateType(Enum):
    """Types of Windows updates"""
    CRITICAL = "Critical"
    SECURITY = "Security"
    DEFINITION = "Definition"
    FEATURE = "Feature"
    SERVICE_PACK = "Service Pack"
    UPDATE = "Update"
    DRIVER = "Driver"


class UpdateStatus(Enum):
    """Update installation status"""
    NOT_INSTALLED = "Not Installed"
    DOWNLOADING = "Downloading"
    DOWNLOADED = "Downloaded"
    INSTALLING = "Installing"
    INSTALLED = "Installed"
    FAILED = "Failed"
    PENDING_REBOOT = "Pending Reboot"


class AutoUpdateBehavior(Enum):
    """Automatic update behaviors"""
    NOTIFY_DOWNLOAD = 1  # Notify before download
    AUTO_DOWNLOAD_NOTIFY_INSTALL = 2  # Auto download, notify install
    AUTO_DOWNLOAD_SCHEDULE_INSTALL = 3  # Auto download and install
    AUTO_DOWNLOAD_AUTO_INSTALL = 4  # Fully automatic
    DISABLED = 5  # Updates disabled


@dataclass
class WindowsUpdate:
    """Represents a Windows update"""
    update_id: str
    title: str
    description: str
    kb_article: Optional[str]
    type: UpdateType
    status: UpdateStatus
    size: int
    is_mandatory: bool = False
    is_installed: bool = False
    requires_reboot: bool = False
    download_url: Optional[str] = None
    release_date: Optional[str] = None
    support_url: Optional[str] = None
    categories: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'update_id': self.update_id,
            'title': self.title,
            'description': self.description,
            'kb_article': self.kb_article,
            'type': self.type.value,
            'status': self.status.value,
            'size': self.size,
            'is_mandatory': self.is_mandatory,
            'is_installed': self.is_installed,
            'requires_reboot': self.requires_reboot,
            'download_url': self.download_url,
            'release_date': self.release_date,
            'support_url': self.support_url,
            'categories': self.categories
        }


@dataclass
class UpdateHistory:
    """Update installation history entry"""
    update_id: str
    title: str
    date: datetime
    operation: str  # Installation, Uninstallation
    result: str  # Succeeded, Failed, etc.
    kb_article: Optional[str] = None


class WindowsUpdateManager:
    """Manage Windows Updates using PowerShell and WMI"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self._check_prerequisites()

    def _check_prerequisites(self):
        """Check if required PowerShell modules are available"""
        # Check for PSWindowsUpdate module
        ps_script = "Get-Module -ListAvailable PSWindowsUpdate"
        result = subprocess.run(
            ["powershell", "-Command", ps_script],
            capture_output=True,
            text=True
        )

        if not result.stdout.strip():
            print("Warning: PSWindowsUpdate module not installed.")
            print("Install with: Install-Module PSWindowsUpdate -Force")

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

    def check_for_updates(self) -> List[WindowsUpdate]:
        """Check for available Windows updates"""
        ps_script = """
        try {
            Import-Module PSWindowsUpdate -ErrorAction Stop
            $updates = Get-WindowsUpdate -MicrosoftUpdate

            $updates | ForEach-Object {
                [PSCustomObject]@{
                    UpdateId = $_.UpdateID
                    Title = $_.Title
                    Description = $_.Description
                    KBArticle = $_.KBArticleID
                    Type = $_.Categories[0].Name
                    Size = $_.Size
                    IsMandatory = $_.IsMandatory
                    IsInstalled = $_.IsInstalled
                    RebootRequired = $_.RebootRequired
                }
            } | ConvertTo-Json
        } catch {
            # Fallback to WU COM interface
            $session = New-Object -ComObject Microsoft.Update.Session
            $searcher = $session.CreateUpdateSearcher()
            $results = $searcher.Search("IsInstalled=0")

            $results.Updates | ForEach-Object {
                [PSCustomObject]@{
                    UpdateId = $_.Identity.UpdateID
                    Title = $_.Title
                    Description = $_.Description
                    KBArticle = if ($_.KBArticleIDs.Count -gt 0) { $_.KBArticleIDs[0] } else { $null }
                    Type = if ($_.Categories.Count -gt 0) { $_.Categories[0].Name } else { "Update" }
                    Size = $_.MaxDownloadSize
                    IsMandatory = $_.IsMandatory
                    IsInstalled = $_.IsInstalled
                    RebootRequired = $_.RebootRequired
                }
            } | ConvertTo-Json
        }
        """

        result = self._run_powershell(ps_script, check=False)

        if not result.stdout.strip():
            return []

        try:
            data = json.loads(result.stdout)
            if isinstance(data, dict):
                data = [data]

            updates = []
            for item in data:
                update = WindowsUpdate(
                    update_id=item.get('UpdateId', ''),
                    title=item.get('Title', ''),
                    description=item.get('Description', ''),
                    kb_article=item.get('KBArticle'),
                    type=self._parse_update_type(item.get('Type', 'Update')),
                    status=UpdateStatus.NOT_INSTALLED,
                    size=item.get('Size', 0),
                    is_mandatory=item.get('IsMandatory', False),
                    is_installed=item.get('IsInstalled', False),
                    requires_reboot=item.get('RebootRequired', False)
                )
                updates.append(update)

            return updates
        except json.JSONDecodeError:
            return []

    def _parse_update_type(self, type_str: str) -> UpdateType:
        """Parse update type from string"""
        type_map = {
            'Critical Updates': UpdateType.CRITICAL,
            'Security Updates': UpdateType.SECURITY,
            'Definition Updates': UpdateType.DEFINITION,
            'Feature Packs': UpdateType.FEATURE,
            'Service Packs': UpdateType.SERVICE_PACK,
            'Drivers': UpdateType.DRIVER
        }
        return type_map.get(type_str, UpdateType.UPDATE)

    def download_updates(self, update_ids: Optional[List[str]] = None) -> bool:
        """Download specified updates or all available updates"""
        if update_ids:
            updates_filter = " -UpdateID " + ",".join(update_ids)
        else:
            updates_filter = ""

        ps_script = f"""
        try {{
            Import-Module PSWindowsUpdate -ErrorAction Stop
            Get-WindowsUpdate{updates_filter} -Download -AcceptAll
            $true
        }} catch {{
            # Fallback to COM
            $session = New-Object -ComObject Microsoft.Update.Session
            $searcher = $session.CreateUpdateSearcher()
            $results = $searcher.Search("IsInstalled=0")

            $downloader = $session.CreateUpdateDownloader()
            $downloader.Updates = $results.Updates
            $result = $downloader.Download()

            $result.ResultCode -eq 2  # 2 = Success
        }}
        """

        result = self._run_powershell(ps_script, check=False)
        return result.returncode == 0

    def install_updates(
        self,
        update_ids: Optional[List[str]] = None,
        auto_reboot: bool = False,
        ignore_reboot: bool = False
    ) -> Tuple[bool, bool]:
        """
        Install updates

        Returns:
            (success, reboot_required)
        """
        if update_ids:
            updates_filter = " -UpdateID " + ",".join(update_ids)
        else:
            updates_filter = ""

        reboot_param = ""
        if auto_reboot:
            reboot_param = " -AutoReboot"
        elif ignore_reboot:
            reboot_param = " -IgnoreReboot"

        ps_script = f"""
        try {{
            Import-Module PSWindowsUpdate -ErrorAction Stop
            $result = Get-WindowsUpdate{updates_filter} -Install -AcceptAll{reboot_param}

            [PSCustomObject]@{{
                Success = $?
                RebootRequired = (Get-WURebootStatus -Silent)
            }} | ConvertTo-Json
        }} catch {{
            # Fallback to COM
            $session = New-Object -ComObject Microsoft.Update.Session
            $searcher = $session.CreateUpdateSearcher()
            $results = $searcher.Search("IsInstalled=0 and IsDownloaded=1")

            $installer = $session.CreateUpdateInstaller()
            $installer.Updates = $results.Updates
            $installResult = $installer.Install()

            [PSCustomObject]@{{
                Success = ($installResult.ResultCode -eq 2)
                RebootRequired = $installResult.RebootRequired
            }} | ConvertTo-Json
        }}
        """

        result = self._run_powershell(ps_script, check=False)

        if result.stdout.strip():
            try:
                data = json.loads(result.stdout)
                return (data.get('Success', False), data.get('RebootRequired', False))
            except:
                pass

        return (result.returncode == 0, False)

    def get_update_history(self, max_results: int = 50) -> List[UpdateHistory]:
        """Get Windows Update history"""
        ps_script = f"""
        $session = New-Object -ComObject Microsoft.Update.Session
        $searcher = $session.CreateUpdateSearcher()
        $historyCount = $searcher.GetTotalHistoryCount()
        $history = $searcher.QueryHistory(0, [Math]::Min($historyCount, {max_results}))

        $history | ForEach-Object {{
            [PSCustomObject]@{{
                UpdateId = $_.UpdateIdentity.UpdateID
                Title = $_.Title
                Date = $_.Date.ToString("yyyy-MM-dd HH:mm:ss")
                Operation = switch ($_.Operation) {{
                    1 {{ "Installation" }}
                    2 {{ "Uninstallation" }}
                    default {{ "Unknown" }}
                }}
                Result = switch ($_.ResultCode) {{
                    0 {{ "Not Started" }}
                    1 {{ "In Progress" }}
                    2 {{ "Succeeded" }}
                    3 {{ "Succeeded with Errors" }}
                    4 {{ "Failed" }}
                    5 {{ "Aborted" }}
                    default {{ "Unknown" }}
                }}
                KBArticle = if ($_.Title -match 'KB\\d+') {{ $matches[0] }} else {{ $null }}
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

            history = []
            for item in data:
                entry = UpdateHistory(
                    update_id=item['UpdateId'],
                    title=item['Title'],
                    date=datetime.strptime(item['Date'], "%Y-%m-%d %H:%M:%S"),
                    operation=item['Operation'],
                    result=item['Result'],
                    kb_article=item.get('KBArticle')
                )
                history.append(entry)

            return history
        except:
            return []

    def uninstall_update(self, kb_article: str) -> bool:
        """Uninstall a Windows update by KB number"""
        ps_script = f"""
        wusa /uninstall /kb:{kb_article.replace('KB', '')} /quiet /norestart
        $?
        """

        result = self._run_powershell(ps_script, check=False)
        return result.returncode == 0

    def get_installed_updates(self) -> List[WindowsUpdate]:
        """Get list of installed updates"""
        ps_script = """
        Get-HotFix | ForEach-Object {
            [PSCustomObject]@{
                UpdateId = $_.HotFixID
                Title = $_.Description
                Description = $_.Description
                KBArticle = $_.HotFixID
                InstalledOn = $_.InstalledOn.ToString("yyyy-MM-dd")
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

            updates = []
            for item in data:
                update = WindowsUpdate(
                    update_id=item['UpdateId'],
                    title=item['Title'],
                    description=item['Description'],
                    kb_article=item['KBArticle'],
                    type=UpdateType.UPDATE,
                    status=UpdateStatus.INSTALLED,
                    size=0,
                    is_installed=True,
                    release_date=item.get('InstalledOn')
                )
                updates.append(update)

            return updates
        except:
            return []

    def pause_updates(self, days: int = 7) -> bool:
        """Pause Windows updates for specified days (max 35)"""
        if days > 35:
            days = 35

        ps_script = f"""
        $regPath = "HKLM:\\SOFTWARE\\Microsoft\\WindowsUpdate\\UX\\Settings"
        $pauseDate = (Get-Date).AddDays({days}).ToString("yyyy-MM-ddTHH:mm:ssZ")

        Set-ItemProperty -Path $regPath -Name "PauseUpdatesExpiryTime" -Value $pauseDate -Force
        $?
        """

        result = self._run_powershell(ps_script, check=False)
        return result.returncode == 0

    def resume_updates(self) -> bool:
        """Resume Windows updates"""
        ps_script = """
        $regPath = "HKLM:\\SOFTWARE\\Microsoft\\WindowsUpdate\\UX\\Settings"
        Remove-ItemProperty -Path $regPath -Name "PauseUpdatesExpiryTime" -Force -ErrorAction SilentlyContinue
        $?
        """

        result = self._run_powershell(ps_script, check=False)
        return result.returncode == 0

    def set_auto_update_behavior(self, behavior: AutoUpdateBehavior) -> bool:
        """Set automatic update behavior"""
        try:
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, "AUOptions", 0, winreg.REG_DWORD, behavior.value)
            return True
        except Exception as e:
            if self.verbose:
                print(f"Error setting auto update behavior: {e}")
            return False

    def get_auto_update_behavior(self) -> Optional[AutoUpdateBehavior]:
        """Get current automatic update behavior"""
        try:
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, "AUOptions")
                return AutoUpdateBehavior(value)
        except:
            return None

    def check_pending_reboot(self) -> bool:
        """Check if system has pending reboot for updates"""
        ps_script = """
        $rebootPending = $false

        # Check Component Based Servicing
        if (Test-Path "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Component Based Servicing\\RebootPending") {
            $rebootPending = $true
        }

        # Check Windows Update
        if (Test-Path "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\WindowsUpdate\\Auto Update\\RebootRequired") {
            $rebootPending = $true
        }

        # Check pending file rename operations
        $regKey = "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Session Manager"
        $pendingFileRename = Get-ItemProperty -Path $regKey -Name "PendingFileRenameOperations" -ErrorAction SilentlyContinue
        if ($pendingFileRename) {
            $rebootPending = $true
        }

        $rebootPending
        """

        result = self._run_powershell(ps_script, check=False)
        return result.stdout.strip().lower() == "true"

    def get_wsus_server(self) -> Optional[str]:
        """Get configured WSUS server"""
        try:
            key_path = r"SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_READ) as key:
                wsus_server, _ = winreg.QueryValueEx(key, "WUServer")
                return wsus_server
        except:
            return None

    def set_wsus_server(self, server_url: str, status_server_url: Optional[str] = None) -> bool:
        """Configure WSUS server"""
        try:
            key_path = r"SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate"
            with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                winreg.SetValueEx(key, "WUServer", 0, winreg.REG_SZ, server_url)
                status_url = status_server_url or server_url
                winreg.SetValueEx(key, "WUStatusServer", 0, winreg.REG_SZ, status_url)

            # Enable use of WSUS
            au_key_path = r"SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU"
            with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, au_key_path) as au_key:
                winreg.SetValueEx(au_key, "UseWUServer", 0, winreg.REG_DWORD, 1)

            return True
        except Exception as e:
            if self.verbose:
                print(f"Error setting WSUS server: {e}")
            return False


# Convenience functions
def check_updates() -> List[WindowsUpdate]:
    """Quick check for updates"""
    manager = WindowsUpdateManager()
    return manager.check_for_updates()


def install_all_updates(auto_reboot: bool = False) -> Tuple[bool, bool]:
    """Quick install all updates"""
    manager = WindowsUpdateManager()
    return manager.install_updates(auto_reboot=auto_reboot)


def pause_updates(days: int = 7) -> bool:
    """Quick pause updates"""
    manager = WindowsUpdateManager()
    return manager.pause_updates(days)


def check_reboot_required() -> bool:
    """Quick check if reboot required"""
    manager = WindowsUpdateManager()
    return manager.check_pending_reboot()
