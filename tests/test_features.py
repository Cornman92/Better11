"""Tests for Windows Features management."""
import sys
from unittest.mock import MagicMock, patch

import pytest

from system_tools.features import (
    FeatureState,
    WindowsFeature,
    FeaturePreset,
    WindowsFeaturesManager,
)


@pytest.mark.skipif(
    sys.platform != "win32",
    reason="Windows Features management only works on Windows"
)
class TestWindowsFeaturesManager:
    """Test WindowsFeaturesManager class."""
    
    @pytest.fixture
    def manager(self):
        """Create WindowsFeaturesManager instance."""
        return WindowsFeaturesManager(dry_run=True)
    
    def test_manager_creation(self, manager):
        """Test creating features manager."""
        assert manager.dry_run is True
        metadata = manager.get_metadata()
        assert metadata.name == "Windows Features Manager"
        assert metadata.requires_admin is True
        assert metadata.requires_restart is True
    
    def test_feature_state_enum(self):
        """Test feature state enum."""
        assert FeatureState.ENABLED.value == "enabled"
        assert FeatureState.DISABLED.value == "disabled"
        assert FeatureState.ENABLE_PENDING.value == "enable_pending"
    
    def test_feature_creation(self):
        """Test creating Windows feature."""
        feature = WindowsFeature(
            name="Microsoft-Windows-Subsystem-Linux",
            display_name="Windows Subsystem for Linux",
            description="Run Linux environments",
            state=FeatureState.ENABLED,
            restart_required=False
        )
        
        assert feature.name == "Microsoft-Windows-Subsystem-Linux"
        assert feature.state == FeatureState.ENABLED
    
    def test_feature_presets(self, manager):
        """Test feature presets."""
        assert manager.DEVELOPER_PRESET.name == "Developer"
        assert manager.MINIMAL_PRESET.name == "Minimal"
        assert len(manager.DEVELOPER_PRESET.features_to_enable) > 0
    
    @patch('system_tools.features.subprocess.run')
    def test_list_features(self, mock_run, manager):
        """Test listing Windows features."""
        # Mock DISM output
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = """
Feature Name                                    State
----------------------------------------------- --------
Microsoft-Windows-Subsystem-Linux              Enabled
VirtualMachinePlatform                         Disabled
"""
        mock_run.return_value = mock_result
        
        features = manager.list_features()
        assert len(features) == 2
        assert features[0].name == "Microsoft-Windows-Subsystem-Linux"
        assert features[0].state == FeatureState.ENABLED
        assert features[1].state == FeatureState.DISABLED
    
    @patch('system_tools.features.subprocess.run')
    def test_enable_feature(self, mock_run, manager):
        """Test enabling a feature."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Feature enabled successfully"
        mock_run.return_value = mock_result
        
        success = manager.enable_feature("Microsoft-Windows-Subsystem-Linux")
        assert success is True
    
    @patch('system_tools.features.subprocess.run')
    def test_disable_feature(self, mock_run, manager):
        """Test disabling a feature."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Feature disabled successfully"
        mock_run.return_value = mock_result
        
        success = manager.disable_feature("VirtualMachinePlatform")
        assert success is True
    
    @patch('system_tools.features.subprocess.run')
    def test_get_feature_dependencies(self, mock_run, manager):
        """Test getting feature dependencies."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = """
Feature Information:
Dependencies:
  Microsoft-Windows-Subsystem-Linux
"""
        mock_run.return_value = mock_result
        
        deps = manager.get_feature_dependencies("VirtualMachinePlatform")
        assert len(deps) > 0
    
    def test_get_feature_state(self, manager):
        """Test getting feature state."""
        # Mock list_features
        test_feature = WindowsFeature(
            name="Test-Feature",
            display_name="Test Feature",
            description="Test",
            state=FeatureState.ENABLED
        )
        manager.list_features = MagicMock(return_value=[test_feature])
        
        state = manager.get_feature_state("Test-Feature")
        assert state == FeatureState.ENABLED
    
    def test_apply_preset(self, manager):
        """Test applying feature preset."""
        preset = FeaturePreset(
            name="Test Preset",
            description="Test",
            features_to_enable=["Feature1"],
            features_to_disable=["Feature2"]
        )
        
        manager.enable_feature = MagicMock(return_value=True)
        manager.disable_feature = MagicMock(return_value=True)
        
        success = manager.apply_preset(preset)
        assert success is True
        manager.enable_feature.assert_called_once_with("Feature1")
        manager.disable_feature.assert_called_once_with("Feature2")
