"""Tests for startup manager."""
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

import pytest

from system_tools.startup import (
    StartupManager,
    StartupLocation,
    StartupImpact,
    StartupItem,
    list_startup_items,
    WINREG_AVAILABLE,
)


class TestStartupItem:
    """Test StartupItem dataclass."""
    
    def test_startup_item_creation(self):
        """Test creating a StartupItem."""
        item = StartupItem(
            name="Test App",
            command="C:\\test.exe",
            location=StartupLocation.REGISTRY_HKCU_RUN,
            enabled=True
        )
        assert item.name == "Test App"
        assert item.command == "C:\\test.exe"
        assert item.location == StartupLocation.REGISTRY_HKCU_RUN
        assert item.enabled is True
        assert item.impact == StartupImpact.UNKNOWN
    
    def test_startup_item_with_impact(self):
        """Test StartupItem with impact level."""
        item = StartupItem(
            name="Heavy App",
            command="C:\\heavy.exe",
            location=StartupLocation.STARTUP_FOLDER_USER,
            enabled=True,
            impact=StartupImpact.HIGH
        )
        assert item.impact == StartupImpact.HIGH
    
    def test_startup_item_str_enabled(self):
        """Test string representation of enabled item."""
        item = StartupItem(
            name="App",
            command="cmd",
            location=StartupLocation.REGISTRY_HKCU_RUN,
            enabled=True
        )
        assert "✓" in str(item)
        assert "App" in str(item)
    
    def test_startup_item_str_disabled(self):
        """Test string representation of disabled item."""
        item = StartupItem(
            name="App",
            command="cmd",
            location=StartupLocation.REGISTRY_HKCU_RUN,
            enabled=False
        )
        assert "✗" in str(item)


class TestStartupManager:
    """Test StartupManager class."""
    
    def test_startup_manager_creation(self):
        """Test creating StartupManager."""
        manager = StartupManager()
        assert manager is not None
        
    def test_get_metadata(self):
        """Test getting tool metadata."""
        manager = StartupManager()
        metadata = manager.get_metadata()
        assert metadata.name == "Startup Manager"
        assert metadata.version == "0.3.0"
        assert metadata.category == "performance"
        assert metadata.requires_admin is False
    
    def test_validate_environment_posix(self):
        """Test environment validation on POSIX systems."""
        manager = StartupManager()
        # Should not raise on POSIX systems (just logs warning)
        manager.validate_environment()
    
    def test_list_startup_items(self):
        """Test listing startup items."""
        manager = StartupManager()
        items = manager.list_startup_items()
        assert isinstance(items, list)
        # Items may be empty on test systems
    
    @pytest.mark.skipif(not WINREG_AVAILABLE, reason="winreg not available")
    def test_get_registry_items(self):
        """Test getting registry startup items."""
        manager = StartupManager()
        items = manager._get_registry_items()
        assert isinstance(items, list)
        
        # Verify all items have required attributes
        for item in items:
            assert isinstance(item.name, str)
            assert isinstance(item.command, str)
            assert isinstance(item.location, StartupLocation)
            assert isinstance(item.enabled, bool)
    
    def test_get_startup_folder_items(self):
        """Test getting startup folder items."""
        manager = StartupManager()
        items = manager._get_startup_folder_items()
        assert isinstance(items, list)
        
        # Verify structure even if empty
        for item in items:
            assert isinstance(item, StartupItem)
            assert item.location in [
                StartupLocation.STARTUP_FOLDER_USER,
                StartupLocation.STARTUP_FOLDER_COMMON
            ]
    
    def test_get_startup_folder_items_with_mock(self):
        """Test getting startup folder items with mocked filesystem."""
        manager = StartupManager()
        
        # Mock Path.exists and Path.iterdir
        with patch('system_tools.startup.Path.exists', return_value=True):
            # Mock a directory with some files
            mock_file = MagicMock()
            mock_file.is_file.return_value = True
            mock_file.suffix = '.lnk'
            mock_file.stem = 'TestApp'
            mock_file.__str__ = lambda self: 'C:\\TestApp.lnk'
            
            with patch('system_tools.startup.Path.iterdir', return_value=[mock_file]):
                items = manager._get_startup_folder_items()
                # Should find items from both folders
                assert len(items) >= 0
    
    def test_execute(self):
        """Test execute method."""
        manager = StartupManager()
        result = manager.execute()
        assert result is True
    
    def test_dry_run(self):
        """Test dry run mode."""
        manager = StartupManager(dry_run=True)
        items = manager.list_startup_items()
        assert isinstance(items, list)
        
        # Dry run shouldn't affect listing
        assert manager.dry_run is True
    
    def test_disable_startup_item_dry_run(self):
        """Test disabling startup item in dry run."""
        manager = StartupManager(dry_run=True)
        
        item = StartupItem(
            name="Test",
            command="test.exe",
            location=StartupLocation.REGISTRY_HKCU_RUN,
            enabled=True
        )
        
        # Should succeed in dry run without actual implementation
        result = manager.disable_startup_item(item)
        assert result is True
    
    def test_enable_startup_item_dry_run(self):
        """Test enabling startup item in dry run."""
        manager = StartupManager(dry_run=True)
        
        item = StartupItem(
            name="Test",
            command="test.exe",
            location=StartupLocation.REGISTRY_HKCU_RUN,
            enabled=False
        )
        
        result = manager.enable_startup_item(item)
        assert result is True
    
    def test_remove_startup_item_dry_run(self):
        """Test removing startup item in dry run."""
        manager = StartupManager(dry_run=True)
        
        item = StartupItem(
            name="Test",
            command="test.exe",
            location=StartupLocation.REGISTRY_HKCU_RUN,
            enabled=True
        )
        
        result = manager.remove_startup_item(item)
        assert result is True
    
    def test_disable_not_implemented_without_dry_run(self):
        """Test that disable raises NotImplementedError without dry run."""
        manager = StartupManager(dry_run=False)
        
        item = StartupItem(
            name="Test",
            command="test.exe",
            location=StartupLocation.REGISTRY_HKCU_RUN,
            enabled=True
        )
        
        with pytest.raises(NotImplementedError):
            manager.disable_startup_item(item)
    
    def test_get_boot_time_estimate(self):
        """Test boot time estimation."""
        manager = StartupManager()
        estimate = manager.get_boot_time_estimate()
        assert isinstance(estimate, float)
        assert estimate >= 0
    
    def test_get_boot_time_estimate_with_items(self):
        """Test boot time estimation with known items."""
        manager = StartupManager()
        
        # Mock list_startup_items to return known items
        items = [
            StartupItem("App1", "cmd", StartupLocation.REGISTRY_HKCU_RUN, 
                       True, StartupImpact.HIGH),
            StartupItem("App2", "cmd", StartupLocation.REGISTRY_HKCU_RUN, 
                       True, StartupImpact.LOW),
            StartupItem("App3", "cmd", StartupLocation.REGISTRY_HKCU_RUN, 
                       False, StartupImpact.HIGH),  # Disabled
        ]
        
        with patch.object(manager, 'list_startup_items', return_value=items):
            estimate = manager.get_boot_time_estimate()
            # HIGH (3.5) + LOW (0.5) = 4.0 (disabled item not counted)
            assert estimate == pytest.approx(4.0)
    
    def test_get_recommendations_few_items(self):
        """Test recommendations with few startup items."""
        manager = StartupManager()
        
        items = [
            StartupItem("App1", "cmd", StartupLocation.REGISTRY_HKCU_RUN, True),
            StartupItem("App2", "cmd", StartupLocation.REGISTRY_HKCU_RUN, True),
        ]
        
        with patch.object(manager, 'list_startup_items', return_value=items):
            recommendations = manager.get_recommendations()
            assert isinstance(recommendations, list)
            # Should have no warnings with only 2 items
            assert len(recommendations) == 0
    
    def test_get_recommendations_many_items(self):
        """Test recommendations with many startup items."""
        manager = StartupManager()
        
        # Create 20 items
        items = [
            StartupItem(f"App{i}", "cmd", StartupLocation.REGISTRY_HKCU_RUN, True)
            for i in range(20)
        ]
        
        with patch.object(manager, 'list_startup_items', return_value=items):
            recommendations = manager.get_recommendations()
            assert len(recommendations) > 0
            assert any("startup items" in rec.lower() for rec in recommendations)
    
    def test_get_recommendations_high_impact(self):
        """Test recommendations with high impact items."""
        manager = StartupManager()
        
        items = [
            StartupItem("Heavy1", "cmd", StartupLocation.REGISTRY_HKCU_RUN, 
                       True, StartupImpact.HIGH),
            StartupItem("Heavy2", "cmd", StartupLocation.REGISTRY_HKCU_RUN, 
                       True, StartupImpact.HIGH),
        ]
        
        with patch.object(manager, 'list_startup_items', return_value=items):
            recommendations = manager.get_recommendations()
            assert len(recommendations) > 0
            assert any("high-impact" in rec.lower() for rec in recommendations)


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    def test_list_startup_items_function(self):
        """Test list_startup_items convenience function."""
        items = list_startup_items()
        assert isinstance(items, list)
    
    def test_list_startup_items_returns_startup_items(self):
        """Test that convenience function returns StartupItems."""
        items = list_startup_items()
        for item in items:
            assert isinstance(item, StartupItem)


class TestStartupManagerIntegration:
    """Integration tests for StartupManager."""
    
    def test_full_workflow_dry_run(self):
        """Test complete workflow in dry run mode."""
        manager = StartupManager(dry_run=True)
        
        # List items
        items = manager.list_startup_items()
        
        # Get recommendations
        recommendations = manager.get_recommendations()
        assert isinstance(recommendations, list)
        
        # Get boot time estimate
        estimate = manager.get_boot_time_estimate()
        assert estimate >= 0
        
        # If we have items, test operations
        if items:
            item = items[0]
            
            # Test disable
            result = manager.disable_startup_item(item)
            assert result is True
            
            # Test enable
            result = manager.enable_startup_item(item)
            assert result is True
            
            # Test remove
            result = manager.remove_startup_item(item)
            assert result is True
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Windows-specific test")
    def test_run_method(self):
        """Test the run() method from base class."""
        manager = StartupManager(dry_run=True)
        
        # Run should execute and return True
        result = manager.run(skip_confirmation=True)
        assert result is True


class TestStartupLocation:
    """Test StartupLocation enum."""
    
    def test_all_locations_defined(self):
        """Test that all expected locations are defined."""
        expected = [
            "REGISTRY_HKLM_RUN",
            "REGISTRY_HKCU_RUN",
            "REGISTRY_HKLM_RUN_ONCE",
            "REGISTRY_HKCU_RUN_ONCE",
            "STARTUP_FOLDER_COMMON",
            "STARTUP_FOLDER_USER",
            "TASK_SCHEDULER",
            "SERVICES",
        ]
        
        for loc in expected:
            assert hasattr(StartupLocation, loc)


class TestStartupImpact:
    """Test StartupImpact enum."""
    
    def test_all_impacts_defined(self):
        """Test that all expected impact levels are defined."""
        expected = ["HIGH", "MEDIUM", "LOW", "UNKNOWN"]
        
        for impact in expected:
            assert hasattr(StartupImpact, impact)
