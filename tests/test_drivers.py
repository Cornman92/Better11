"""Tests for Driver management."""
import platform
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from system_tools.drivers import (
    DriverStatus,
    DriverClass,
    DriverInfo,
    DriverBackup,
    DriverManager,
)


class TestDriverStatus:
    """Test DriverStatus enum."""

    def test_driver_status_values(self):
        """Test driver status enum values."""
        assert DriverStatus.OK.value == "ok"
        assert DriverStatus.PROBLEM.value == "problem"
        assert DriverStatus.DISABLED.value == "disabled"
        assert DriverStatus.UNKNOWN.value == "unknown"


class TestDriverClass:
    """Test DriverClass enum."""

    def test_driver_class_values(self):
        """Test driver class enum values."""
        assert DriverClass.DISPLAY.value == "Display"
        assert DriverClass.NET.value == "Net"
        assert DriverClass.USB.value == "USB"


class TestDriverInfo:
    """Test DriverInfo dataclass."""

    def test_driver_info_creation(self):
        """Test creating a DriverInfo."""
        driver = DriverInfo(
            device_name="Intel UHD Graphics",
            device_id="PCI\\VEN_8086",
            driver_name="igdumdim64",
            driver_version="30.0.100.9865",
            driver_date=datetime(2023, 6, 15),
            manufacturer="Intel Corporation",
            device_class="Display",
            status=DriverStatus.OK,
            inf_file="oem123.inf",
            is_signed=True,
            signer="Microsoft Windows Hardware Compatibility Publisher"
        )

        assert driver.device_name == "Intel UHD Graphics"
        assert driver.manufacturer == "Intel Corporation"
        assert driver.status == DriverStatus.OK
        assert driver.is_signed is True

    def test_is_outdated_recent(self):
        """Test is_outdated for recent driver."""
        driver = DriverInfo(
            device_name="Test",
            device_id="",
            driver_name="test",
            driver_version="1.0",
            driver_date=datetime.now(),
            manufacturer="",
            device_class="",
            status=DriverStatus.OK
        )

        assert driver.is_outdated is False

    def test_is_outdated_old(self):
        """Test is_outdated for old driver."""
        driver = DriverInfo(
            device_name="Test",
            device_id="",
            driver_name="test",
            driver_version="1.0",
            driver_date=datetime(2020, 1, 1),
            manufacturer="",
            device_class="",
            status=DriverStatus.OK
        )

        assert driver.is_outdated is True

    def test_to_dict(self):
        """Test to_dict method."""
        driver = DriverInfo(
            device_name="Test",
            device_id="ID123",
            driver_name="test",
            driver_version="1.0",
            driver_date=datetime(2023, 6, 15),
            manufacturer="Test Inc",
            device_class="Display",
            status=DriverStatus.OK
        )

        d = driver.to_dict()
        assert d["device_name"] == "Test"
        assert d["manufacturer"] == "Test Inc"
        assert d["status"] == "ok"


class TestDriverBackup:
    """Test DriverBackup dataclass."""

    def test_driver_backup_creation(self):
        """Test creating a DriverBackup."""
        backup = DriverBackup(
            backup_path=Path("/tmp/backup"),
            backup_date=datetime.now(),
            driver_count=15,
            size_bytes=1024 * 1024 * 50,  # 50 MB
            description="Test backup"
        )

        assert backup.driver_count == 15
        assert backup.size_mb == 50.0
        assert backup.description == "Test backup"


class TestDriverManager:
    """Test DriverManager class."""

    def test_manager_creation(self):
        """Test creating a driver manager."""
        manager = DriverManager()
        metadata = manager.get_metadata()

        assert metadata.name == "Driver Manager"
        assert metadata.version == "0.3.0"
        assert metadata.requires_admin is True
        assert metadata.category == "drivers"

    def test_manager_dry_run(self):
        """Test manager with dry-run mode."""
        manager = DriverManager(dry_run=True)
        assert manager.dry_run is True

    @patch('system_tools.drivers.platform.system')
    def test_list_drivers_non_windows(self, mock_system):
        """Test listing drivers on non-Windows."""
        mock_system.return_value = "Linux"

        manager = DriverManager()
        drivers = manager.list_drivers()

        assert drivers == []

    @patch('system_tools.drivers.platform.system')
    def test_get_problematic_drivers_non_windows(self, mock_system):
        """Test getting problematic drivers on non-Windows."""
        mock_system.return_value = "Linux"

        manager = DriverManager()
        problems = manager.get_problematic_drivers()

        assert problems == []

    def test_backup_drivers_dry_run(self):
        """Test backing up drivers in dry-run mode."""
        manager = DriverManager(dry_run=True)
        backup = manager.backup_drivers("test_backup")

        assert backup is not None
        assert backup.driver_count == 0

    @patch('system_tools.drivers.platform.system')
    def test_backup_drivers_non_windows(self, mock_system):
        """Test backing up drivers on non-Windows."""
        mock_system.return_value = "Linux"

        manager = DriverManager()
        backup = manager.backup_drivers()

        assert backup is None

    def test_restore_driver_dry_run(self):
        """Test restoring driver in dry-run mode."""
        manager = DriverManager(dry_run=True)
        result = manager.restore_driver(Path("/tmp/test.inf"))
        assert result is True

    @patch('system_tools.drivers.platform.system')
    def test_restore_driver_non_windows(self, mock_system):
        """Test restoring driver on non-Windows."""
        mock_system.return_value = "Linux"

        manager = DriverManager()
        result = manager.restore_driver(Path("/tmp/test.inf"))

        assert result is False

    def test_delete_backup_dry_run(self):
        """Test deleting backup in dry-run mode."""
        manager = DriverManager(dry_run=True)
        backup = DriverBackup(
            backup_path=Path("/tmp/test"),
            backup_date=datetime.now(),
            driver_count=0,
            size_bytes=0,
            description=""
        )
        result = manager.delete_backup(backup)
        assert result is True

    def test_update_driver_dry_run(self):
        """Test updating driver in dry-run mode."""
        manager = DriverManager(dry_run=True)
        result = manager.update_driver("test-device-id")
        assert result is True

    @patch('system_tools.drivers.platform.system')
    def test_update_driver_non_windows(self, mock_system):
        """Test updating driver on non-Windows."""
        mock_system.return_value = "Linux"

        manager = DriverManager()
        result = manager.update_driver("test-device-id")

        assert result is False

    def test_get_driver_summary(self):
        """Test getting driver summary."""
        manager = DriverManager()
        
        with patch.object(manager, 'list_drivers', return_value=[]):
            with patch.object(manager, 'get_problematic_drivers', return_value=[]):
                with patch.object(manager, 'list_backups', return_value=[]):
                    summary = manager.get_driver_summary()

        assert "total_drivers" in summary
        assert "problematic" in summary
        assert "unsigned" in summary
        assert "by_class" in summary

    def test_validate_environment(self):
        """Test environment validation."""
        manager = DriverManager()
        # Should not raise
        manager.validate_environment()

    def test_execute_returns_true(self):
        """Test execute method."""
        manager = DriverManager()
        with patch.object(manager, 'list_drivers', return_value=[]):
            result = manager.execute()
            assert result is True

    def test_get_outdated_drivers(self):
        """Test getting outdated drivers."""
        old_driver = DriverInfo(
            device_name="Old Driver",
            device_id="",
            driver_name="old",
            driver_version="1.0",
            driver_date=datetime(2020, 1, 1),
            manufacturer="",
            device_class="",
            status=DriverStatus.OK
        )
        new_driver = DriverInfo(
            device_name="New Driver",
            device_id="",
            driver_name="new",
            driver_version="2.0",
            driver_date=datetime.now(),
            manufacturer="",
            device_class="",
            status=DriverStatus.OK
        )

        manager = DriverManager()
        with patch.object(manager, 'list_drivers', return_value=[old_driver, new_driver]):
            outdated = manager.get_outdated_drivers()

        assert len(outdated) == 1
        assert outdated[0].device_name == "Old Driver"


# Windows-specific tests
@pytest.mark.skipif(platform.system() != "Windows", reason="Windows-specific test")
class TestDriverManagerWindows:
    """Tests that require Windows platform."""

    def test_list_drivers_on_windows(self):
        """Test listing drivers on Windows."""
        manager = DriverManager()
        drivers = manager.list_drivers()

        # Should return a list
        assert isinstance(drivers, list)

    def test_get_driver_summary_on_windows(self):
        """Test getting driver summary on Windows."""
        manager = DriverManager()
        summary = manager.get_driver_summary()

        assert isinstance(summary, dict)
        assert summary["total_drivers"] >= 0
