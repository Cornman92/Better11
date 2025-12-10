"""Tests for Windows Update management."""
import platform
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

import pytest

from system_tools.updates import (
    UpdateType,
    UpdateStatus,
    WindowsUpdate,
    WindowsUpdateManager,
)


class TestUpdateType:
    """Test UpdateType enum."""

    def test_update_type_values(self):
        """Test update type enum values."""
        assert UpdateType.CRITICAL.value == "critical"
        assert UpdateType.SECURITY.value == "security"
        assert UpdateType.DEFINITION.value == "definition"
        assert UpdateType.FEATURE.value == "feature"
        assert UpdateType.DRIVER.value == "driver"
        assert UpdateType.OTHER.value == "other"


class TestUpdateStatus:
    """Test UpdateStatus enum."""

    def test_update_status_values(self):
        """Test update status enum values."""
        assert UpdateStatus.AVAILABLE.value == "available"
        assert UpdateStatus.DOWNLOADING.value == "downloading"
        assert UpdateStatus.PENDING_INSTALL.value == "pending_install"
        assert UpdateStatus.INSTALLED.value == "installed"
        assert UpdateStatus.FAILED.value == "failed"


class TestWindowsUpdate:
    """Test WindowsUpdate dataclass."""

    def test_windows_update_creation(self):
        """Test creating a Windows update."""
        update = WindowsUpdate(
            id="KB5000001",
            title="Security Update for Windows 11",
            description="This update includes security improvements",
            update_type=UpdateType.SECURITY,
            size_mb=150.5,
            status=UpdateStatus.AVAILABLE,
            kb_article="KB5000001",
            support_url="https://support.microsoft.com/kb/5000001",
            is_mandatory=True,
            requires_restart=True
        )

        assert update.id == "KB5000001"
        assert update.title == "Security Update for Windows 11"
        assert update.update_type == UpdateType.SECURITY
        assert update.size_mb == 150.5
        assert update.status == UpdateStatus.AVAILABLE
        assert update.is_mandatory is True
        assert update.requires_restart is True

    def test_windows_update_defaults(self):
        """Test Windows update with default values."""
        update = WindowsUpdate(
            id="KB5000002",
            title="Test Update",
            description="Test",
            update_type=UpdateType.OTHER,
            size_mb=10.0,
            status=UpdateStatus.AVAILABLE
        )

        assert update.kb_article is None
        assert update.support_url is None
        assert update.is_mandatory is False
        assert update.requires_restart is False
        assert update.install_date is None


class TestWindowsUpdateManager:
    """Test WindowsUpdateManager class."""

    def test_manager_creation(self):
        """Test creating an update manager."""
        manager = WindowsUpdateManager()
        metadata = manager.get_metadata()

        assert metadata.name == "Windows Update Manager"
        assert metadata.version == "0.3.0"
        assert metadata.requires_admin is True
        assert metadata.category == "updates"

    def test_manager_dry_run(self):
        """Test manager with dry-run mode."""
        manager = WindowsUpdateManager(dry_run=True)
        assert manager._dry_run is True

    def test_pause_updates_invalid_days(self):
        """Test pausing updates with invalid days raises error."""
        manager = WindowsUpdateManager()

        with pytest.raises(ValueError, match="Cannot pause updates for more than 35 days"):
            manager.pause_updates(40)

    def test_pause_updates_dry_run(self):
        """Test pausing updates in dry-run mode."""
        manager = WindowsUpdateManager(dry_run=True)
        result = manager.pause_updates(7)
        assert result is True

    @patch('system_tools.updates.platform.system')
    def test_pause_updates_non_windows(self, mock_system):
        """Test pausing updates on non-Windows platform."""
        mock_system.return_value = "Linux"

        manager = WindowsUpdateManager()
        result = manager.pause_updates(7)
        assert result is False

    def test_resume_updates_dry_run(self):
        """Test resuming updates in dry-run mode."""
        manager = WindowsUpdateManager(dry_run=True)
        result = manager.resume_updates()
        assert result is True

    @patch('system_tools.updates.platform.system')
    def test_resume_updates_non_windows(self, mock_system):
        """Test resuming updates on non-Windows platform."""
        mock_system.return_value = "Linux"

        manager = WindowsUpdateManager()
        result = manager.resume_updates()
        assert result is False

    def test_set_active_hours_invalid_hours(self):
        """Test setting active hours with invalid hours raises error."""
        manager = WindowsUpdateManager()

        with pytest.raises(ValueError, match="Hours must be between 0 and 23"):
            manager.set_active_hours(-1, 12)

        with pytest.raises(ValueError, match="Hours must be between 0 and 23"):
            manager.set_active_hours(8, 25)

    def test_set_active_hours_dry_run(self):
        """Test setting active hours in dry-run mode."""
        manager = WindowsUpdateManager(dry_run=True)
        result = manager.set_active_hours(8, 18)
        assert result is True

    @patch('system_tools.updates.platform.system')
    def test_set_active_hours_non_windows(self, mock_system):
        """Test setting active hours on non-Windows platform."""
        mock_system.return_value = "Linux"

        manager = WindowsUpdateManager()
        result = manager.set_active_hours(8, 18)
        assert result is False

    def test_check_for_updates_dry_run(self):
        """Test checking for updates in dry-run mode."""
        manager = WindowsUpdateManager(dry_run=True)
        updates = manager.check_for_updates()
        assert updates == []

    @patch('system_tools.updates.platform.system')
    def test_check_for_updates_non_windows(self, mock_system):
        """Test checking for updates on non-Windows platform."""
        mock_system.return_value = "Linux"

        manager = WindowsUpdateManager()
        updates = manager.check_for_updates()
        assert updates == []

    def test_get_update_history_non_windows(self):
        """Test getting update history on non-Windows platform."""
        with patch('system_tools.updates.platform.system', return_value="Linux"):
            manager = WindowsUpdateManager()
            history = manager.get_update_history(30)
            assert history == []

    def test_uninstall_update_dry_run(self):
        """Test uninstalling update in dry-run mode."""
        manager = WindowsUpdateManager(dry_run=True)
        result = manager.uninstall_update("KB5000001")
        assert result is True

    @patch('system_tools.updates.platform.system')
    def test_uninstall_update_non_windows(self, mock_system):
        """Test uninstalling update on non-Windows platform."""
        mock_system.return_value = "Linux"

        manager = WindowsUpdateManager()
        result = manager.uninstall_update("KB5000001")
        assert result is False

    def test_uninstall_update_normalizes_kb_format(self):
        """Test that KB article format is normalized."""
        manager = WindowsUpdateManager(dry_run=True)

        # Should work with or without "KB" prefix
        result1 = manager.uninstall_update("KB5000001")
        result2 = manager.uninstall_update("5000001")

        assert result1 is True
        assert result2 is True

    def test_determine_update_type_security(self):
        """Test determining update type for security updates."""
        manager = WindowsUpdateManager()

        assert manager._determine_update_type("Security Update for Windows") == UpdateType.SECURITY
        assert manager._determine_update_type("2024-01 Security Update") == UpdateType.SECURITY

    def test_determine_update_type_critical(self):
        """Test determining update type for critical updates."""
        manager = WindowsUpdateManager()

        assert manager._determine_update_type("Critical Update for Windows") == UpdateType.CRITICAL

    def test_determine_update_type_definition(self):
        """Test determining update type for definition updates."""
        manager = WindowsUpdateManager()

        assert manager._determine_update_type("Definition Update for Windows Defender") == UpdateType.DEFINITION
        assert manager._determine_update_type("Windows Defender - KB123456") == UpdateType.DEFINITION

    def test_determine_update_type_feature(self):
        """Test determining update type for feature updates."""
        manager = WindowsUpdateManager()

        assert manager._determine_update_type("Feature Update to Windows 11, version 23H2") == UpdateType.FEATURE
        assert manager._determine_update_type("Windows 11 Version 23H2") == UpdateType.FEATURE

    def test_determine_update_type_driver(self):
        """Test determining update type for driver updates."""
        manager = WindowsUpdateManager()

        assert manager._determine_update_type("Intel Corporation - Display Driver") == UpdateType.DRIVER
        assert manager._determine_update_type("NVIDIA - Graphics driver") == UpdateType.DRIVER

    def test_determine_update_type_other(self):
        """Test determining update type for other updates."""
        manager = WindowsUpdateManager()

        assert manager._determine_update_type("Random Update") == UpdateType.OTHER
        assert manager._determine_update_type("") == UpdateType.OTHER

    def test_execute_returns_true(self):
        """Test that execute method runs successfully."""
        manager = WindowsUpdateManager(dry_run=True)
        result = manager.execute()
        assert result is True

    def test_validate_environment(self):
        """Test environment validation."""
        manager = WindowsUpdateManager()
        # Should not raise any exceptions
        manager.validate_environment()


# Mocked Windows tests
class TestWindowsUpdateManagerMocked:
    """Tests using mocked Windows API to simulate behavior."""

    @patch('system_tools.updates.platform.system')
    @patch('system_tools.updates.winreg')
    def test_pause_updates_mocked(self, mock_winreg, mock_system):
        """Test pausing updates with mocked registry."""
        mock_system.return_value = "Windows"

        # Mock registry operations
        mock_key = MagicMock()
        mock_winreg.CreateKeyEx.return_value = mock_key
        mock_winreg.HKEY_LOCAL_MACHINE = 0x80000002
        mock_winreg.KEY_WRITE = 0x20006
        mock_winreg.REG_SZ = 1

        manager = WindowsUpdateManager()
        result = manager.pause_updates(7)

        assert result is True
        # Verify registry operations were called
        assert mock_winreg.SetValueEx.call_count >= 3
        mock_winreg.CloseKey.assert_called_once_with(mock_key)

    @patch('system_tools.updates.platform.system')
    @patch('system_tools.updates.winreg')
    def test_resume_updates_mocked(self, mock_winreg, mock_system):
        """Test resuming updates with mocked registry."""
        mock_system.return_value = "Windows"

        # Mock registry operations
        mock_key = MagicMock()
        mock_winreg.OpenKey.return_value = mock_key
        mock_winreg.HKEY_LOCAL_MACHINE = 0x80000002
        mock_winreg.KEY_WRITE = 0x20006

        manager = WindowsUpdateManager()
        result = manager.resume_updates()

        assert result is True
        # Verify DeleteValue was called for pause keys
        assert mock_winreg.DeleteValue.called or mock_key.called
        mock_winreg.CloseKey.assert_called_once_with(mock_key)

    @patch('system_tools.updates.platform.system')
    @patch('system_tools.updates.winreg')
    def test_set_active_hours_mocked(self, mock_winreg, mock_system):
        """Test setting active hours with mocked registry."""
        mock_system.return_value = "Windows"

        # Mock registry operations
        mock_key = MagicMock()
        mock_winreg.CreateKeyEx.return_value = mock_key
        mock_winreg.HKEY_LOCAL_MACHINE = 0x80000002
        mock_winreg.KEY_WRITE = 0x20006
        mock_winreg.REG_DWORD = 4

        manager = WindowsUpdateManager()
        result = manager.set_active_hours(8, 18)

        assert result is True
        # Verify active hours were set
        assert mock_winreg.SetValueEx.call_count == 2
        mock_winreg.CloseKey.assert_called_once_with(mock_key)

    @patch('system_tools.updates.platform.system')
    @patch('system_tools.updates.subprocess.run')
    def test_check_for_updates_mocked(self, mock_run, mock_system):
        """Test checking for updates with mocked PowerShell."""
        mock_system.return_value = "Windows"

        # Mock PowerShell response
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '''[
            {
                "Title": "2024-01 Security Update for Windows 11",
                "Description": "This update includes security improvements",
                "SizeInMB": 150.5,
                "IsDownloaded": false,
                "IsMandatory": true,
                "RebootRequired": true,
                "KBArticleIDs": "5000001",
                "SupportUrl": "https://support.microsoft.com"
            }
        ]'''
        mock_run.return_value = mock_result

        manager = WindowsUpdateManager()
        updates = manager.check_for_updates()

        assert len(updates) == 1
        assert updates[0].title == "2024-01 Security Update for Windows 11"
        assert updates[0].kb_article == "KB5000001"
        assert updates[0].update_type == UpdateType.SECURITY
        assert updates[0].is_mandatory is True

    @patch('system_tools.updates.platform.system')
    @patch('system_tools.updates.subprocess.run')
    def test_get_update_history_mocked(self, mock_run, mock_system):
        """Test getting update history with mocked PowerShell."""
        mock_system.return_value = "Windows"

        # Mock PowerShell response
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = '''[
            {
                "Title": "Security Update KB5000001",
                "Description": "Security improvements",
                "Date": "2024-01-15T10:30:00Z",
                "ResultCode": 2,
                "KBArticleIDs": "5000001",
                "SupportUrl": "https://support.microsoft.com"
            }
        ]'''
        mock_run.return_value = mock_result

        manager = WindowsUpdateManager()
        history = manager.get_update_history(30)

        assert len(history) == 1
        assert history[0].kb_article == "KB5000001"
        assert history[0].status == UpdateStatus.INSTALLED

    @patch('system_tools.updates.platform.system')
    @patch('system_tools.updates.subprocess.run')
    def test_uninstall_update_mocked_success(self, mock_run, mock_system):
        """Test uninstalling update with mocked WUSA."""
        mock_system.return_value = "Windows"

        # Mock successful uninstall
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        manager = WindowsUpdateManager()
        result = manager.uninstall_update("KB5000001")

        assert result is True
        # Verify WUSA was called correctly
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "wusa.exe" in args
        assert "/kb:5000001" in " ".join(args)

    @patch('system_tools.updates.platform.system')
    @patch('system_tools.updates.subprocess.run')
    def test_uninstall_update_not_found(self, mock_run, mock_system):
        """Test uninstalling update that's not found."""
        mock_system.return_value = "Windows"

        # Mock update not found
        mock_result = MagicMock()
        mock_result.returncode = 2359302  # Update not found
        mock_run.return_value = mock_result

        manager = WindowsUpdateManager()
        result = manager.uninstall_update("KB5000001")

        assert result is False

    @patch('system_tools.updates.platform.system')
    @patch('system_tools.updates.subprocess.run')
    def test_check_for_updates_timeout(self, mock_run, mock_system):
        """Test handling timeout when checking for updates."""
        mock_system.return_value = "Windows"

        # Mock timeout
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired("powershell", 120)

        manager = WindowsUpdateManager()
        updates = manager.check_for_updates()

        assert updates == []

    @patch('system_tools.updates.platform.system')
    @patch('system_tools.updates.winreg')
    def test_pause_updates_permission_error(self, mock_winreg, mock_system):
        """Test handling permission error when pausing updates."""
        mock_system.return_value = "Windows"

        # Mock permission error
        mock_winreg.CreateKeyEx.side_effect = PermissionError()

        manager = WindowsUpdateManager()
        result = manager.pause_updates(7)

        assert result is False


# Windows-specific integration tests
@pytest.mark.skipif(platform.system() != "Windows", reason="Windows-specific test")
class TestWindowsUpdateManagerWindows:
    """Integration tests that require Windows platform."""

    def test_set_active_hours_integration(self):
        """Integration test for setting active hours."""
        manager = WindowsUpdateManager()

        # This requires admin rights
        try:
            result = manager.set_active_hours(8, 18)
            # If successful, result should be True
            # If no admin rights, result should be False
            assert isinstance(result, bool)
        except PermissionError:
            pytest.skip("Requires administrator privileges")

    def test_pause_and_resume_integration(self):
        """Integration test for pausing and resuming updates."""
        manager = WindowsUpdateManager()

        try:
            # Try to pause updates
            pause_result = manager.pause_updates(1)

            if pause_result:
                # If pause succeeded, try to resume
                resume_result = manager.resume_updates()
                assert isinstance(resume_result, bool)
        except PermissionError:
            pytest.skip("Requires administrator privileges")
