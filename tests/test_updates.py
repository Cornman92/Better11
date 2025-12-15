"""Tests for Windows Update management."""
import platform
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from system_tools.updates import (
    UpdateType,
    UpdateStatus,
    WindowsUpdate,
    UpdateSettings,
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
        """Test creating a WindowsUpdate."""
        update = WindowsUpdate(
            id="test-id",
            title="Test Update",
            description="Test description",
            update_type=UpdateType.SECURITY,
            size_mb=100.5,
            status=UpdateStatus.AVAILABLE,
            kb_article="KB123456",
            is_mandatory=True,
            requires_restart=True
        )

        assert update.id == "test-id"
        assert update.title == "Test Update"
        assert update.update_type == UpdateType.SECURITY
        assert update.size_mb == 100.5
        assert update.status == UpdateStatus.AVAILABLE
        assert update.kb_article == "KB123456"
        assert update.is_mandatory is True
        assert update.requires_restart is True

    def test_size_display_mb(self):
        """Test size display in MB."""
        update = WindowsUpdate(
            id="test", title="Test", description="", update_type=UpdateType.OTHER,
            size_mb=500.0, status=UpdateStatus.AVAILABLE
        )
        assert "500.00 MB" in update.size_display

    def test_size_display_gb(self):
        """Test size display in GB."""
        update = WindowsUpdate(
            id="test", title="Test", description="", update_type=UpdateType.OTHER,
            size_mb=2048.0, status=UpdateStatus.AVAILABLE
        )
        assert "2.00 GB" in update.size_display


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
        assert manager.dry_run is True

    @patch('system_tools.updates.platform.system')
    def test_check_for_updates_non_windows(self, mock_system):
        """Test checking updates on non-Windows platform."""
        mock_system.return_value = "Linux"

        manager = WindowsUpdateManager()
        updates = manager.check_for_updates()

        assert updates == []

    def test_pause_updates_dry_run(self):
        """Test pausing updates in dry-run mode."""
        manager = WindowsUpdateManager(dry_run=True)
        result = manager.pause_updates(7)
        assert result is True

    def test_pause_updates_too_many_days(self):
        """Test pausing updates for too many days."""
        manager = WindowsUpdateManager()
        with pytest.raises(ValueError, match="Cannot pause updates for more than 35 days"):
            manager.pause_updates(40)

    def test_pause_updates_zero_days(self):
        """Test pausing updates for zero days."""
        manager = WindowsUpdateManager()
        with pytest.raises(ValueError, match="Days must be at least 1"):
            manager.pause_updates(0)

    def test_resume_updates_dry_run(self):
        """Test resuming updates in dry-run mode."""
        manager = WindowsUpdateManager(dry_run=True)
        result = manager.resume_updates()
        assert result is True

    def test_set_active_hours_dry_run(self):
        """Test setting active hours in dry-run mode."""
        manager = WindowsUpdateManager(dry_run=True)
        result = manager.set_active_hours(8, 17)
        assert result is True

    def test_set_active_hours_invalid_start(self):
        """Test setting invalid start hour."""
        manager = WindowsUpdateManager()
        with pytest.raises(ValueError, match="Hours must be between 0 and 23"):
            manager.set_active_hours(25, 17)

    def test_set_active_hours_invalid_end(self):
        """Test setting invalid end hour."""
        manager = WindowsUpdateManager()
        with pytest.raises(ValueError, match="Hours must be between 0 and 23"):
            manager.set_active_hours(8, -1)

    def test_set_active_hours_too_long_span(self):
        """Test setting active hours with too long span."""
        manager = WindowsUpdateManager()
        with pytest.raises(ValueError, match="Active hours span cannot exceed 18 hours"):
            manager.set_active_hours(6, 1)  # 19 hour span

    @patch('system_tools.updates.platform.system')
    def test_get_active_hours_non_windows(self, mock_system):
        """Test getting active hours on non-Windows."""
        mock_system.return_value = "Linux"

        manager = WindowsUpdateManager()
        start, end = manager.get_active_hours()

        assert start == 8
        assert end == 17

    @patch('system_tools.updates.platform.system')
    def test_get_update_history_non_windows(self, mock_system):
        """Test getting update history on non-Windows."""
        mock_system.return_value = "Linux"

        manager = WindowsUpdateManager()
        history = manager.get_update_history()

        assert history == []

    def test_uninstall_update_dry_run(self):
        """Test uninstalling update in dry-run mode."""
        manager = WindowsUpdateManager(dry_run=True)
        result = manager.uninstall_update("KB123456")
        assert result is True

    def test_uninstall_update_normalizes_kb(self):
        """Test that uninstall normalizes KB format."""
        manager = WindowsUpdateManager(dry_run=True)
        
        # Without KB prefix
        result = manager.uninstall_update("123456")
        assert result is True

    def test_hide_update_dry_run(self):
        """Test hiding update in dry-run mode."""
        manager = WindowsUpdateManager(dry_run=True)
        result = manager.hide_update("test-update-id")
        assert result is True

    @patch('system_tools.updates.platform.system')
    def test_install_updates_non_windows(self, mock_system):
        """Test installing updates on non-Windows."""
        mock_system.return_value = "Linux"

        manager = WindowsUpdateManager()
        result = manager.install_updates()

        assert result is False

    def test_install_updates_dry_run(self):
        """Test installing updates in dry-run mode."""
        manager = WindowsUpdateManager(dry_run=True)
        result = manager.install_updates()
        assert result is True

    @patch('system_tools.updates.platform.system')
    def test_get_update_settings_non_windows(self, mock_system):
        """Test getting settings on non-Windows."""
        mock_system.return_value = "Linux"

        manager = WindowsUpdateManager()
        settings = manager.get_update_settings()

        assert settings is None

    def test_validate_environment(self):
        """Test environment validation."""
        manager = WindowsUpdateManager()
        # Should not raise
        manager.validate_environment()

    def test_execute_returns_true(self):
        """Test execute method."""
        manager = WindowsUpdateManager()
        with patch.object(manager, 'check_for_updates', return_value=[]):
            result = manager.execute()
            assert result is True


class TestUpdateSettings:
    """Test UpdateSettings dataclass."""

    def test_update_settings_creation(self):
        """Test creating UpdateSettings."""
        pause_until = datetime.now() + timedelta(days=7)
        
        settings = UpdateSettings(
            auto_download=True,
            auto_install=True,
            active_hours_start=8,
            active_hours_end=17,
            pause_until=pause_until,
            last_check=datetime.now(),
            restart_required=False
        )

        assert settings.auto_download is True
        assert settings.auto_install is True
        assert settings.active_hours_start == 8
        assert settings.active_hours_end == 17
        assert settings.pause_until == pause_until
        assert settings.restart_required is False


# Windows-specific tests
@pytest.mark.skipif(platform.system() != "Windows", reason="Windows-specific test")
class TestWindowsUpdateManagerWindows:
    """Tests that require Windows platform."""

    def test_check_for_updates_on_windows(self):
        """Test checking for updates on Windows."""
        manager = WindowsUpdateManager()
        # This might take a while
        updates = manager.check_for_updates()

        # Should return a list (may be empty)
        assert isinstance(updates, list)

    def test_get_active_hours_on_windows(self):
        """Test getting active hours on Windows."""
        manager = WindowsUpdateManager()
        start, end = manager.get_active_hours()

        assert 0 <= start <= 23
        assert 0 <= end <= 23

    def test_get_update_settings_on_windows(self):
        """Test getting update settings on Windows."""
        manager = WindowsUpdateManager()
        settings = manager.get_update_settings()

        if settings:
            assert isinstance(settings, UpdateSettings)
            assert 0 <= settings.active_hours_start <= 23
