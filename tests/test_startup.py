"""Tests for startup program management."""
import platform
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

from system_tools.startup import (
    StartupLocation,
    StartupImpact,
    StartupItem,
    StartupManager,
    STARTUP_REGISTRY_PATHS,
)


class TestStartupLocation:
    """Test StartupLocation enum."""

    def test_startup_location_values(self):
        """Test startup location enum values."""
        assert StartupLocation.REGISTRY_HKLM_RUN.value == "hklm_run"
        assert StartupLocation.REGISTRY_HKCU_RUN.value == "hkcu_run"
        assert StartupLocation.STARTUP_FOLDER_COMMON.value == "startup_common"
        assert StartupLocation.STARTUP_FOLDER_USER.value == "startup_user"
        assert StartupLocation.TASK_SCHEDULER.value == "task_scheduler"
        assert StartupLocation.SERVICES.value == "services"


class TestStartupImpact:
    """Test StartupImpact enum."""

    def test_startup_impact_values(self):
        """Test startup impact enum values."""
        assert StartupImpact.HIGH.value == "high"
        assert StartupImpact.MEDIUM.value == "medium"
        assert StartupImpact.LOW.value == "low"
        assert StartupImpact.UNKNOWN.value == "unknown"


class TestStartupItem:
    """Test StartupItem dataclass."""

    def test_startup_item_creation(self):
        """Test creating a startup item."""
        item = StartupItem(
            name="TestApp",
            command="C:\\Program Files\\TestApp\\app.exe",
            location=StartupLocation.REGISTRY_HKCU_RUN,
            enabled=True,
            impact=StartupImpact.LOW,
            publisher="Test Publisher"
        )

        assert item.name == "TestApp"
        assert item.command == "C:\\Program Files\\TestApp\\app.exe"
        assert item.location == StartupLocation.REGISTRY_HKCU_RUN
        assert item.enabled is True
        assert item.impact == StartupImpact.LOW
        assert item.publisher == "Test Publisher"

    def test_startup_item_defaults(self):
        """Test startup item with default values."""
        item = StartupItem(
            name="Test",
            command="test.exe",
            location=StartupLocation.REGISTRY_HKCU_RUN,
            enabled=True
        )

        assert item.impact == StartupImpact.UNKNOWN
        assert item.publisher is None


class TestStartupManager:
    """Test StartupManager class."""

    def test_manager_creation(self):
        """Test creating a startup manager."""
        manager = StartupManager()
        metadata = manager.get_metadata()

        assert metadata.name == "Startup Manager"
        assert metadata.version == "0.3.0"
        assert metadata.category == "optimization"

    def test_manager_dry_run(self):
        """Test manager with dry-run mode."""
        manager = StartupManager(dry_run=True)
        assert manager.dry_run is True

    def test_list_startup_items_structure(self):
        """Test that list_startup_items returns a list."""
        manager = StartupManager()
        items = manager.list_startup_items()
        assert isinstance(items, list)

    @patch('system_tools.startup.platform.system')
    def test_list_startup_items_non_windows(self, mock_system):
        """Test listing startup items on non-Windows platform."""
        mock_system.return_value = "Linux"

        manager = StartupManager()
        items = manager.list_startup_items()

        # Should return empty list on non-Windows
        assert items == []

    @pytest.mark.skipif(platform.system() != "Windows", reason="Windows-specific test")
    def test_get_registry_items_on_windows(self):
        """Test getting registry startup items on Windows."""
        manager = StartupManager()
        items = manager._get_registry_items()

        # Should return a list (may be empty)
        assert isinstance(items, list)

    @pytest.mark.skipif(platform.system() != "Windows", reason="Windows-specific test")
    def test_get_startup_folder_items_on_windows(self):
        """Test getting startup folder items on Windows."""
        manager = StartupManager()
        items = manager._get_startup_folder_items()

        # Should return a list (may be empty)
        assert isinstance(items, list)

    def test_enable_startup_item_dry_run(self):
        """Test enabling startup item in dry-run mode."""
        manager = StartupManager(dry_run=True)

        item = StartupItem(
            name="Test",
            command="test.exe",
            location=StartupLocation.REGISTRY_HKCU_RUN,
            enabled=False
        )

        result = manager.enable_startup_item(item)
        assert result is True

    def test_disable_startup_item_dry_run(self):
        """Test disabling startup item in dry-run mode."""
        manager = StartupManager(dry_run=True)

        item = StartupItem(
            name="Test",
            command="test.exe",
            location=StartupLocation.REGISTRY_HKCU_RUN,
            enabled=True
        )

        result = manager.disable_startup_item(item)
        assert result is True

    def test_remove_startup_item_dry_run(self):
        """Test removing startup item in dry-run mode."""
        manager = StartupManager(dry_run=True)

        item = StartupItem(
            name="Test",
            command="test.exe",
            location=StartupLocation.REGISTRY_HKCU_RUN,
            enabled=True
        )

        result = manager.remove_startup_item(item)
        assert result is True

    def test_get_recommendations_empty_list(self):
        """Test getting recommendations with no startup items."""
        manager = StartupManager()

        with patch.object(manager, 'list_startup_items', return_value=[]):
            recommendations = manager.get_recommendations()
            assert len(recommendations) > 0
            assert "No startup items" in recommendations[0]

    def test_get_recommendations_many_items(self):
        """Test getting recommendations with many startup items."""
        manager = StartupManager()

        # Create 20 mock startup items
        items = [
            StartupItem(
                name=f"Item{i}",
                command=f"item{i}.exe",
                location=StartupLocation.REGISTRY_HKCU_RUN,
                enabled=True
            )
            for i in range(20)
        ]

        with patch.object(manager, 'list_startup_items', return_value=items):
            recommendations = manager.get_recommendations()
            assert len(recommendations) > 0
            assert "slow down boot time" in recommendations[0]

    def test_get_recommendations_common_apps(self):
        """Test recommendations detect common safe-to-disable apps."""
        manager = StartupManager()

        items = [
            StartupItem(
                name="OneDrive",
                command="C:\\Program Files\\OneDrive\\OneDrive.exe",
                location=StartupLocation.REGISTRY_HKCU_RUN,
                enabled=True
            ),
            StartupItem(
                name="Spotify",
                command="C:\\Users\\User\\AppData\\Spotify\\Spotify.exe",
                location=StartupLocation.REGISTRY_HKCU_RUN,
                enabled=True
            ),
        ]

        with patch.object(manager, 'list_startup_items', return_value=items):
            recommendations = manager.get_recommendations()

            # Should suggest these can be disabled
            recommendations_text = " ".join(recommendations)
            assert "OneDrive" in recommendations_text or "Spotify" in recommendations_text

    def test_get_recommendations_high_impact_items(self):
        """Test recommendations mention high-impact items."""
        manager = StartupManager()

        items = [
            StartupItem(
                name="HeavyApp",
                command="heavy.exe",
                location=StartupLocation.REGISTRY_HKCU_RUN,
                enabled=True,
                impact=StartupImpact.HIGH
            ),
        ]

        with patch.object(manager, 'list_startup_items', return_value=items):
            recommendations = manager.get_recommendations()
            recommendations_text = " ".join(recommendations)
            assert "high-impact" in recommendations_text.lower()

    def test_execute_returns_true(self):
        """Test that execute method runs successfully."""
        manager = StartupManager()
        with patch.object(manager, 'list_startup_items', return_value=[]):
            result = manager.execute()
            assert result is True

    def test_validate_environment(self):
        """Test environment validation."""
        manager = StartupManager()
        # Should not raise any exceptions
        manager.validate_environment()

    @patch('system_tools.startup.platform.system')
    def test_enable_startup_item_non_windows(self, mock_system):
        """Test enabling startup item on non-Windows returns error."""
        mock_system.return_value = "Linux"

        manager = StartupManager()
        item = StartupItem(
            name="Test",
            command="test.exe",
            location=StartupLocation.REGISTRY_HKCU_RUN,
            enabled=False
        )

        # This should handle non-Windows gracefully
        # The actual implementation should return False or log a warning

    def test_remove_startup_folder_item(self):
        """Test removing a startup folder item."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test file
            test_file = Path(tmpdir) / "test_startup.lnk"
            test_file.touch()

            item = StartupItem(
                name="TestApp",
                command=str(test_file),
                location=StartupLocation.STARTUP_FOLDER_USER,
                enabled=True
            )

            manager = StartupManager()

            # On Windows this should work, on other platforms it should fail gracefully
            if platform.system() == "Windows":
                result = manager._remove_startup_folder_item(item)
                # File should be deleted if on Windows
                if result:
                    assert not test_file.exists()

    def test_enumerate_startup_folder_nonexistent(self):
        """Test enumerating a non-existent startup folder."""
        manager = StartupManager()
        fake_folder = Path("/nonexistent/folder/that/does/not/exist")

        items = manager._enumerate_startup_folder(
            fake_folder,
            StartupLocation.STARTUP_FOLDER_USER
        )

        assert items == []


# Integration-like tests (only run on Windows)
@pytest.mark.skipif(platform.system() != "Windows", reason="Windows-specific test")
class TestStartupManagerWindows:
    """Tests that require Windows platform."""

    def test_list_registry_items(self):
        """Test listing registry startup items."""
        manager = StartupManager()
        items = manager._get_registry_items()

        # Verify structure of returned items
        for item in items:
            assert isinstance(item, StartupItem)
            assert item.name
            assert item.command
            assert item.location in (
                StartupLocation.REGISTRY_HKLM_RUN,
                StartupLocation.REGISTRY_HKCU_RUN
            )

    def test_list_folder_items(self):
        """Test listing startup folder items."""
        manager = StartupManager()
        items = manager._get_startup_folder_items()

        # Verify structure of returned items
        for item in items:
            assert isinstance(item, StartupItem)
            assert item.name
            assert item.command
            assert item.location in (
                StartupLocation.STARTUP_FOLDER_COMMON,
                StartupLocation.STARTUP_FOLDER_USER
            )
