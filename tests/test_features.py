"""Tests for Windows Features management."""
import platform
from unittest.mock import patch

import pytest

from system_tools.features import (
    FeatureState,
    WindowsFeature,
    FeaturePreset,
    WindowsFeaturesManager,
)


class TestFeatureState:
    """Test FeatureState enum."""

    def test_feature_state_values(self):
        """Test feature state enum values."""
        assert FeatureState.ENABLED.value == "enabled"
        assert FeatureState.DISABLED.value == "disabled"
        assert FeatureState.ENABLE_PENDING.value == "enable_pending"
        assert FeatureState.DISABLE_PENDING.value == "disable_pending"


class TestWindowsFeature:
    """Test WindowsFeature dataclass."""

    def test_windows_feature_creation(self):
        """Test creating a WindowsFeature."""
        feature = WindowsFeature(
            name="Microsoft-Windows-Subsystem-Linux",
            display_name="Windows Subsystem for Linux",
            description="WSL support",
            state=FeatureState.ENABLED,
            restart_required=True,
            dependencies=["VirtualMachinePlatform"]
        )

        assert feature.name == "Microsoft-Windows-Subsystem-Linux"
        assert feature.display_name == "Windows Subsystem for Linux"
        assert feature.state == FeatureState.ENABLED
        assert feature.restart_required is True
        assert "VirtualMachinePlatform" in feature.dependencies

    def test_is_enabled_property(self):
        """Test is_enabled property."""
        enabled_feature = WindowsFeature(
            name="Test", display_name="Test", description="",
            state=FeatureState.ENABLED
        )
        disabled_feature = WindowsFeature(
            name="Test", display_name="Test", description="",
            state=FeatureState.DISABLED
        )
        pending_feature = WindowsFeature(
            name="Test", display_name="Test", description="",
            state=FeatureState.ENABLE_PENDING
        )

        assert enabled_feature.is_enabled is True
        assert disabled_feature.is_enabled is False
        assert pending_feature.is_enabled is True  # Pending enable = enabled


class TestFeaturePreset:
    """Test FeaturePreset dataclass."""

    def test_feature_preset_creation(self):
        """Test creating a FeaturePreset."""
        preset = FeaturePreset(
            name="Test Preset",
            description="Test description",
            features_to_enable=["Feature1", "Feature2"],
            features_to_disable=["Feature3"]
        )

        assert preset.name == "Test Preset"
        assert preset.description == "Test description"
        assert len(preset.features_to_enable) == 2
        assert len(preset.features_to_disable) == 1


class TestWindowsFeaturesManager:
    """Test WindowsFeaturesManager class."""

    def test_manager_creation(self):
        """Test creating a features manager."""
        manager = WindowsFeaturesManager()
        metadata = manager.get_metadata()

        assert metadata.name == "Windows Features Manager"
        assert metadata.version == "0.3.0"
        assert metadata.requires_admin is True
        assert metadata.requires_restart is True
        assert metadata.category == "features"

    def test_manager_dry_run(self):
        """Test manager with dry-run mode."""
        manager = WindowsFeaturesManager(dry_run=True)
        assert manager.dry_run is True

    def test_developer_preset(self):
        """Test DEVELOPER_PRESET."""
        preset = WindowsFeaturesManager.DEVELOPER_PRESET

        assert preset.name == "Developer"
        assert "Microsoft-Windows-Subsystem-Linux" in preset.features_to_enable
        assert "VirtualMachinePlatform" in preset.features_to_enable

    def test_minimal_preset(self):
        """Test MINIMAL_PRESET."""
        preset = WindowsFeaturesManager.MINIMAL_PRESET

        assert preset.name == "Minimal"
        assert len(preset.features_to_disable) > 0

    def test_gaming_preset(self):
        """Test GAMING_PRESET."""
        preset = WindowsFeaturesManager.GAMING_PRESET

        assert preset.name == "Gaming"
        assert "DirectPlay" in preset.features_to_enable

    def test_server_preset(self):
        """Test SERVER_PRESET."""
        preset = WindowsFeaturesManager.SERVER_PRESET

        assert preset.name == "Server-like"
        assert "TelnetClient" in preset.features_to_enable

    @patch('system_tools.features.platform.system')
    def test_list_features_non_windows(self, mock_system):
        """Test listing features on non-Windows."""
        mock_system.return_value = "Linux"

        manager = WindowsFeaturesManager()
        features = manager.list_features()

        assert features == []

    def test_enable_feature_dry_run(self):
        """Test enabling feature in dry-run mode."""
        manager = WindowsFeaturesManager(dry_run=True)
        result = manager.enable_feature("TestFeature")
        assert result is True

    def test_disable_feature_dry_run(self):
        """Test disabling feature in dry-run mode."""
        manager = WindowsFeaturesManager(dry_run=True)
        result = manager.disable_feature("TestFeature")
        assert result is True

    @patch('system_tools.features.platform.system')
    def test_enable_feature_non_windows(self, mock_system):
        """Test enabling feature on non-Windows."""
        mock_system.return_value = "Linux"

        manager = WindowsFeaturesManager()
        result = manager.enable_feature("TestFeature")

        assert result is False

    @patch('system_tools.features.platform.system')
    def test_disable_feature_non_windows(self, mock_system):
        """Test disabling feature on non-Windows."""
        mock_system.return_value = "Linux"

        manager = WindowsFeaturesManager()
        result = manager.disable_feature("TestFeature")

        assert result is False

    def test_get_presets(self):
        """Test getting presets."""
        manager = WindowsFeaturesManager()
        presets = manager.get_presets()

        assert len(presets) == 4
        assert any(p.name == "Developer" for p in presets)
        assert any(p.name == "Minimal" for p in presets)

    @patch('system_tools.features.platform.system')
    def test_get_feature_non_windows(self, mock_system):
        """Test getting feature on non-Windows."""
        mock_system.return_value = "Linux"

        manager = WindowsFeaturesManager()
        feature = manager.get_feature("TestFeature")

        assert feature is None

    @patch('system_tools.features.platform.system')
    def test_check_wsl_status_non_windows(self, mock_system):
        """Test checking WSL status on non-Windows."""
        mock_system.return_value = "Linux"

        manager = WindowsFeaturesManager()
        status = manager.check_wsl_status()

        assert status["available"] is False
        assert "Not on Windows" in status["reason"]

    def test_enable_wsl_dry_run(self):
        """Test enabling WSL in dry-run mode."""
        manager = WindowsFeaturesManager(dry_run=True)
        result = manager.enable_wsl(wsl2=True)
        assert result is True

    def test_enable_hyper_v_dry_run(self):
        """Test enabling Hyper-V in dry-run mode."""
        manager = WindowsFeaturesManager(dry_run=True)
        result = manager.enable_hyper_v()
        assert result is True

    def test_validate_environment(self):
        """Test environment validation."""
        manager = WindowsFeaturesManager()
        # Should not raise
        manager.validate_environment()

    def test_execute_returns_true(self):
        """Test execute method."""
        manager = WindowsFeaturesManager()
        with patch.object(manager, 'list_features', return_value=[]):
            result = manager.execute()
            assert result is True

    def test_feature_descriptions(self):
        """Test feature descriptions dictionary."""
        descriptions = WindowsFeaturesManager.FEATURE_DESCRIPTIONS

        assert "Microsoft-Windows-Subsystem-Linux" in descriptions
        assert "VirtualMachinePlatform" in descriptions
        assert len(descriptions) > 10


# Windows-specific tests
@pytest.mark.skipif(platform.system() != "Windows", reason="Windows-specific test")
class TestWindowsFeaturesManagerWindows:
    """Tests that require Windows platform."""

    def test_list_features_on_windows(self):
        """Test listing features on Windows."""
        manager = WindowsFeaturesManager()
        features = manager.list_features()

        # Should return a list (may be empty)
        assert isinstance(features, list)

    def test_check_wsl_status_on_windows(self):
        """Test checking WSL status on Windows."""
        manager = WindowsFeaturesManager()
        status = manager.check_wsl_status()

        assert isinstance(status, dict)
        assert "wsl_enabled" in status
        assert "vm_platform_enabled" in status
