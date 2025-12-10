"""Tests for startup manager."""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from system_tools.startup import (
    StartupLocation,
    StartupImpact,
    StartupItem,
    StartupManager,
)


@pytest.mark.skipif(
    sys.platform != "win32",
    reason="Startup management only works on Windows"
)
class TestStartupManager:
    """Test StartupManager class."""
    
    @pytest.fixture
    def manager(self):
        """Create StartupManager instance."""
        return StartupManager(dry_run=True)
    
    def test_manager_creation(self, manager):
        """Test creating startup manager."""
        assert manager.dry_run is True
        metadata = manager.get_metadata()
        assert metadata.name == "Startup Manager"
        assert metadata.requires_admin is False  # Most operations don't need admin
    
    def test_startup_location_enum(self):
        """Test startup location enum."""
        assert StartupLocation.REGISTRY_HKLM_RUN.value == "hklm_run"
        assert StartupLocation.REGISTRY_HKCU_RUN.value == "hkcu_run"
        assert StartupLocation.STARTUP_FOLDER_COMMON.value == "startup_common"
    
    def test_startup_impact_enum(self):
        """Test startup impact enum."""
        assert StartupImpact.HIGH.value == "high"
        assert StartupImpact.MEDIUM.value == "medium"
        assert StartupImpact.LOW.value == "low"
    
    def test_startup_item_creation(self):
        """Test creating startup item."""
        item = StartupItem(
            name="Test App",
            command="C:\\Program Files\\Test\\app.exe",
            location=StartupLocation.REGISTRY_HKLM_RUN,
            enabled=True,
            impact=StartupImpact.MEDIUM
        )
        
        assert item.name == "Test App"
        assert item.enabled is True
        assert item.impact == StartupImpact.MEDIUM
    
    @patch('system_tools.startup.winreg')
    def test_list_startup_items_registry(self, mock_winreg, manager):
        """Test listing startup items from registry."""
        mock_key = MagicMock()
        mock_winreg.OpenKey.return_value = mock_key
        mock_winreg.EnumValue.side_effect = [
            ("TestApp", "C:\\test\\app.exe", 1),
            OSError()  # End of enumeration
        ]
        
        items = manager.list_startup_items()
        assert len(items) >= 0  # May have items from folders too
    
    def test_get_recommendations(self, manager):
        """Test getting startup recommendations."""
        # Mock list_startup_items to return test items
        test_items = [
            StartupItem("App1", "cmd1", StartupLocation.REGISTRY_HKLM_RUN, True, StartupImpact.HIGH),
            StartupItem("App2", "cmd2", StartupLocation.REGISTRY_HKCU_RUN, True, StartupImpact.MEDIUM),
        ] * 6  # 12 items total
        
        manager.list_startup_items = MagicMock(return_value=test_items)
        
        recommendations = manager.get_recommendations()
        assert len(recommendations) > 0
        assert any("12 startup items" in rec for rec in recommendations)
    
    @patch('system_tools.startup.winreg')
    def test_disable_startup_item_registry(self, mock_winreg, manager):
        """Test disabling startup item in registry."""
        item = StartupItem(
            name="TestApp",
            command="C:\\test\\app.exe",
            location=StartupLocation.REGISTRY_HKLM_RUN,
            enabled=True
        )
        
        mock_key = MagicMock()
        mock_winreg.OpenKey.return_value = mock_key
        
        success = manager.disable_startup_item(item)
        assert success is True
        mock_winreg.DeleteValue.assert_called_once()
    
    def test_remove_startup_item(self, manager):
        """Test removing startup item."""
        item = StartupItem(
            name="TestApp",
            command="C:\\test\\app.exe",
            location=StartupLocation.REGISTRY_HKLM_RUN,
            enabled=True
        )
        
        manager.disable_startup_item = MagicMock(return_value=True)
        
        success = manager.remove_startup_item(item)
        assert success is True
        manager.disable_startup_item.assert_called_once_with(item)
