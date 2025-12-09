"""Tests for new system tools (v0.3.0)."""
import pytest

from system_tools.updates import (
    UpdateType,
    UpdateStatus,
    WindowsUpdate,
    WindowsUpdateManager,
)
from system_tools.privacy import (
    TelemetryLevel,
    PrivacySetting,
    PrivacyPreset,
    PrivacyManager,
)
from system_tools.startup import (
    StartupLocation,
    StartupImpact,
    StartupItem,
    StartupManager,
)
from system_tools.features import (
    FeatureState,
    WindowsFeature,
    FeaturePreset,
    WindowsFeaturesManager,
)


class TestWindowsUpdateManager:
    """Test Windows Update Manager."""
    
    def test_manager_creation(self):
        """Test creating update manager."""
        manager = WindowsUpdateManager()
        assert manager.dry_run is False
    
    def test_manager_metadata(self):
        """Test manager metadata."""
        manager = WindowsUpdateManager()
        metadata = manager.get_metadata()
        assert metadata.name == "Windows Update Manager"
        assert metadata.requires_admin is True


class TestPrivacyManager:
    """Test Privacy Manager."""
    
    def test_manager_creation(self):
        """Test creating privacy manager."""
        manager = PrivacyManager()
        assert manager.dry_run is False
    
    def test_manager_metadata(self):
        """Test manager metadata."""
        manager = PrivacyManager()
        metadata = manager.get_metadata()
        assert metadata.name == "Privacy Manager"
    
    def test_privacy_presets_exist(self):
        """Test that predefined presets exist."""
        assert PrivacyManager.MAXIMUM_PRIVACY is not None
        assert PrivacyManager.BALANCED is not None
        assert PrivacyManager.MAXIMUM_PRIVACY.telemetry_level == TelemetryLevel.BASIC


class TestStartupManager:
    """Test Startup Manager."""
    
    def test_manager_creation(self):
        """Test creating startup manager."""
        manager = StartupManager()
        assert manager.dry_run is False
    
    def test_manager_metadata(self):
        """Test manager metadata."""
        manager = StartupManager()
        metadata = manager.get_metadata()
        assert metadata.name == "Startup Manager"
        assert metadata.requires_admin is False  # Most ops don't need admin


class TestWindowsFeaturesManager:
    """Test Windows Features Manager."""
    
    def test_manager_creation(self):
        """Test creating features manager."""
        manager = WindowsFeaturesManager()
        assert manager.dry_run is False
    
    def test_manager_metadata(self):
        """Test manager metadata."""
        manager = WindowsFeaturesManager()
        metadata = manager.get_metadata()
        assert metadata.name == "Windows Features Manager"
        assert metadata.requires_restart is True  # Features often need restart
    
    def test_feature_presets_exist(self):
        """Test that predefined presets exist."""
        assert WindowsFeaturesManager.DEVELOPER_PRESET is not None
        assert WindowsFeaturesManager.MINIMAL_PRESET is not None


class TestDataClasses:
    """Test data classes for system tools."""
    
    def test_windows_update_creation(self):
        """Test creating WindowsUpdate."""
        update = WindowsUpdate(
            id="KB5000001",
            title="Test Update",
            description="A test update",
            update_type=UpdateType.SECURITY,
            size_mb=100.5,
            status=UpdateStatus.AVAILABLE
        )
        assert update.id == "KB5000001"
        assert update.update_type == UpdateType.SECURITY
    
    def test_startup_item_creation(self):
        """Test creating StartupItem."""
        item = StartupItem(
            name="Test App",
            command="test.exe",
            location=StartupLocation.REGISTRY_HKCU_RUN,
            enabled=True,
            impact=StartupImpact.LOW
        )
        assert item.name == "Test App"
        assert item.enabled is True
    
    def test_windows_feature_creation(self):
        """Test creating WindowsFeature."""
        feature = WindowsFeature(
            name="Test-Feature",
            display_name="Test Feature",
            description="A test feature",
            state=FeatureState.ENABLED
        )
        assert feature.name == "Test-Feature"
        assert feature.state == FeatureState.ENABLED


# TODO: Add integration tests when implementations are complete
# TODO: Add tests for actual Windows operations (with mocking)
# TODO: Add tests for error handling
# TODO: Add tests for dry-run mode
