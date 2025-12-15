"""Tests for privacy and telemetry control."""
import sys
from unittest.mock import MagicMock, patch

import pytest

from system_tools.privacy import (
    TelemetryLevel,
    PrivacySetting,
    PrivacyPreset,
    PrivacyManager,
)


@pytest.mark.skipif(
    sys.platform != "win32",
    reason="Privacy management only works on Windows"
)
class TestPrivacyManager:
    """Test PrivacyManager class."""
    
    @pytest.fixture
    def manager(self):
        """Create PrivacyManager instance."""
        return PrivacyManager(dry_run=True)
    
    def test_manager_creation(self, manager):
        """Test creating privacy manager."""
        assert manager.dry_run is True
        metadata = manager.get_metadata()
        assert metadata.name == "Privacy Manager"
        assert metadata.requires_admin is True
    
    def test_telemetry_levels(self):
        """Test telemetry level enum."""
        assert TelemetryLevel.SECURITY.value == 0
        assert TelemetryLevel.BASIC.value == 1
        assert TelemetryLevel.ENHANCED.value == 2
        assert TelemetryLevel.FULL.value == 3
    
    def test_privacy_settings(self):
        """Test privacy setting enum."""
        assert PrivacySetting.LOCATION.value == "location"
        assert PrivacySetting.CAMERA.value == "camera"
        assert PrivacySetting.MICROPHONE.value == "microphone"
    
    def test_privacy_presets(self, manager):
        """Test privacy presets."""
        assert manager.MAXIMUM_PRIVACY.name == "Maximum Privacy"
        assert manager.BALANCED.name == "Balanced"
        assert manager.MAXIMUM_PRIVACY.telemetry_level == TelemetryLevel.BASIC
        assert manager.MAXIMUM_PRIVACY.disable_advertising_id is True
    
    @patch('system_tools.privacy.winreg')
    def test_set_telemetry_level(self, mock_winreg, manager):
        """Test setting telemetry level."""
        mock_key = MagicMock()
        mock_winreg.OpenKey.side_effect = FileNotFoundError()
        mock_winreg.CreateKey.return_value = mock_key
        
        success = manager.set_telemetry_level(TelemetryLevel.BASIC)
        assert success is True
    
    @patch('system_tools.privacy.winreg')
    def test_get_telemetry_level(self, mock_winreg, manager):
        """Test getting telemetry level."""
        mock_key = MagicMock()
        mock_winreg.OpenKey.return_value = mock_key
        mock_winreg.QueryValueEx.return_value = (1, None)  # BASIC level
        
        level = manager.get_telemetry_level()
        assert level == TelemetryLevel.BASIC
    
    @patch('system_tools.privacy.winreg')
    def test_set_app_permission(self, mock_winreg, manager):
        """Test setting app permission."""
        mock_key = MagicMock()
        mock_winreg.OpenKey.side_effect = FileNotFoundError()
        mock_winreg.CreateKey.return_value = mock_key
        
        success = manager.set_app_permission(PrivacySetting.LOCATION, False)
        assert success is True
    
    @patch('system_tools.privacy.winreg')
    def test_get_app_permission(self, mock_winreg, manager):
        """Test getting app permission."""
        mock_key = MagicMock()
        mock_winreg.OpenKey.return_value = mock_key
        mock_winreg.QueryValueEx.return_value = ("Allow", None)
        
        enabled = manager.get_app_permission(PrivacySetting.LOCATION)
        assert enabled is True
    
    @patch('system_tools.privacy.winreg')
    def test_disable_advertising_id(self, mock_winreg, manager):
        """Test disabling advertising ID."""
        mock_key = MagicMock()
        mock_winreg.OpenKey.side_effect = FileNotFoundError()
        mock_winreg.CreateKey.return_value = mock_key
        
        success = manager.disable_advertising_id()
        assert success is True
    
    @patch('system_tools.privacy.winreg')
    def test_disable_cortana(self, mock_winreg, manager):
        """Test disabling Cortana."""
        mock_key = MagicMock()
        mock_winreg.OpenKey.side_effect = FileNotFoundError()
        mock_winreg.CreateKey.return_value = mock_key
        
        success = manager.disable_cortana()
        assert success is True
    
    def test_apply_preset(self, manager):
        """Test applying privacy preset."""
        preset = PrivacyPreset(
            name="Test Preset",
            description="Test",
            telemetry_level=TelemetryLevel.BASIC,
            settings={PrivacySetting.LOCATION: False},
            disable_advertising_id=True
        )
        
        # Mock all methods
        manager.set_telemetry_level = MagicMock(return_value=True)
        manager.set_app_permission = MagicMock(return_value=True)
        manager.disable_advertising_id = MagicMock(return_value=True)
        manager.disable_cortana = MagicMock(return_value=True)
        
        success = manager.apply_preset(preset)
        assert success is True
        manager.set_telemetry_level.assert_called_once()
        manager.disable_advertising_id.assert_called_once()
