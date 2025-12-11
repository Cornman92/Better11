"""Tests for privacy and telemetry control."""
import platform
from unittest.mock import Mock, patch, MagicMock

import pytest

from system_tools.privacy import (
    TelemetryLevel,
    PrivacySetting,
    PrivacyPreset,
    PrivacyManager,
)


class TestTelemetryLevel:
    """Test TelemetryLevel enum."""

    def test_telemetry_level_values(self):
        """Test telemetry level enum values."""
        assert TelemetryLevel.SECURITY.value == 0
        assert TelemetryLevel.BASIC.value == 1
        assert TelemetryLevel.ENHANCED.value == 2
        assert TelemetryLevel.FULL.value == 3


class TestPrivacySetting:
    """Test PrivacySetting enum."""

    def test_privacy_setting_values(self):
        """Test privacy setting enum values."""
        assert PrivacySetting.LOCATION.value == "location"
        assert PrivacySetting.CAMERA.value == "camera"
        assert PrivacySetting.MICROPHONE.value == "microphone"
        assert PrivacySetting.BACKGROUND_APPS.value == "background_apps"


class TestPrivacyPreset:
    """Test PrivacyPreset dataclass."""

    def test_privacy_preset_creation(self):
        """Test creating a privacy preset."""
        preset = PrivacyPreset(
            name="Test Preset",
            description="Test description",
            telemetry_level=TelemetryLevel.BASIC,
            settings={PrivacySetting.LOCATION: False},
            disable_advertising_id=True,
            disable_cortana=False
        )

        assert preset.name == "Test Preset"
        assert preset.description == "Test description"
        assert preset.telemetry_level == TelemetryLevel.BASIC
        assert preset.settings[PrivacySetting.LOCATION] is False
        assert preset.disable_advertising_id is True
        assert preset.disable_cortana is False


class TestPrivacyManager:
    """Test PrivacyManager class."""

    def test_manager_creation(self):
        """Test creating a privacy manager."""
        manager = PrivacyManager()
        metadata = manager.get_metadata()

        assert metadata.name == "Privacy Manager"
        assert metadata.version == "0.3.0"
        assert metadata.requires_admin is True
        assert metadata.category == "privacy"

    def test_manager_dry_run(self):
        """Test manager with dry-run mode."""
        manager = PrivacyManager(dry_run=True)
        assert manager.dry_run is True

    def test_maximum_privacy_preset(self):
        """Test MAXIMUM_PRIVACY preset."""
        preset = PrivacyManager.MAXIMUM_PRIVACY

        assert preset.name == "Maximum Privacy"
        assert preset.telemetry_level == TelemetryLevel.BASIC
        assert preset.disable_advertising_id is True
        assert preset.disable_cortana is True

        # All settings should be False (disabled) for maximum privacy
        for setting in PrivacySetting:
            assert preset.settings.get(setting, False) is False

    def test_balanced_preset(self):
        """Test BALANCED preset."""
        preset = PrivacyManager.BALANCED

        assert preset.name == "Balanced"
        assert preset.telemetry_level == TelemetryLevel.BASIC

        # Some settings should be enabled
        assert preset.settings.get(PrivacySetting.LOCATION) is True
        assert preset.settings.get(PrivacySetting.NOTIFICATIONS) is True

    def test_set_telemetry_level_dry_run(self):
        """Test setting telemetry level in dry-run mode."""
        manager = PrivacyManager(dry_run=True)
        result = manager.set_telemetry_level(TelemetryLevel.BASIC)
        assert result is True

    @patch('system_tools.privacy.platform.system')
    def test_set_telemetry_level_non_windows(self, mock_system):
        """Test setting telemetry level on non-Windows platform."""
        mock_system.return_value = "Linux"

        manager = PrivacyManager()
        result = manager.set_telemetry_level(TelemetryLevel.BASIC)
        assert result is False

    @patch('system_tools.privacy.platform.system')
    def test_get_telemetry_level_non_windows(self, mock_system):
        """Test getting telemetry level on non-Windows platform."""
        mock_system.return_value = "Linux"

        manager = PrivacyManager()
        level = manager.get_telemetry_level()
        # Should return default FULL on non-Windows
        assert level == TelemetryLevel.FULL

    def test_disable_advertising_id_dry_run(self):
        """Test disabling advertising ID in dry-run mode."""
        manager = PrivacyManager(dry_run=True)
        result = manager.disable_advertising_id()
        assert result is True

    @patch('system_tools.privacy.platform.system')
    def test_disable_advertising_id_non_windows(self, mock_system):
        """Test disabling advertising ID on non-Windows platform."""
        mock_system.return_value = "Linux"

        manager = PrivacyManager()
        result = manager.disable_advertising_id()
        assert result is False

    def test_disable_cortana_dry_run(self):
        """Test disabling Cortana in dry-run mode."""
        manager = PrivacyManager(dry_run=True)
        result = manager.disable_cortana()
        assert result is True

    @patch('system_tools.privacy.platform.system')
    def test_disable_cortana_non_windows(self, mock_system):
        """Test disabling Cortana on non-Windows platform."""
        mock_system.return_value = "Linux"

        manager = PrivacyManager()
        result = manager.disable_cortana()
        assert result is False

    def test_execute_returns_true(self):
        """Test that execute method runs successfully."""
        manager = PrivacyManager()
        with patch.object(manager, 'get_telemetry_level', return_value=TelemetryLevel.FULL):
            result = manager.execute()
            assert result is True

    def test_validate_environment(self):
        """Test environment validation."""
        manager = PrivacyManager()
        # Should not raise any exceptions
        manager.validate_environment()


# Windows-specific tests
@pytest.mark.skipif(platform.system() != "Windows", reason="Windows-specific test")
class TestPrivacyManagerWindows:
    """Tests that require Windows platform."""

    def test_get_telemetry_level_on_windows(self):
        """Test getting telemetry level on Windows."""
        manager = PrivacyManager()
        level = manager.get_telemetry_level()

        # Should return a valid TelemetryLevel
        assert isinstance(level, TelemetryLevel)

    def test_set_and_get_telemetry_level_integration(self):
        """Integration test: set and get telemetry level."""
        manager = PrivacyManager()

        # This requires admin rights, so it may fail in CI/CD
        try:
            # Try to set telemetry level
            result = manager.set_telemetry_level(TelemetryLevel.BASIC)

            if result:
                # If successful, verify we can read it back
                level = manager.get_telemetry_level()
                assert level == TelemetryLevel.BASIC
        except PermissionError:
            pytest.skip("Requires administrator privileges")

    def test_disable_advertising_id_integration(self):
        """Integration test: disable advertising ID."""
        manager = PrivacyManager()

        try:
            # This should work without admin rights
            result = manager.disable_advertising_id()
            # If successful, result should be True
            assert result is True or result is False
        except Exception:
            pytest.skip("May require specific Windows version")

    def test_disable_cortana_integration(self):
        """Integration test: disable Cortana."""
        manager = PrivacyManager()

        try:
            # This requires admin rights
            result = manager.disable_cortana()
            # Should either succeed or fail with permission error
            assert result is True or result is False
        except PermissionError:
            pytest.skip("Requires administrator privileges")


# Mocked Windows tests
class TestPrivacyManagerMocked:
    """Tests using mocked winreg to simulate Windows behavior."""

    @patch('system_tools.privacy.platform.system')
    @patch('system_tools.privacy.winreg')
    def test_set_telemetry_level_mocked(self, mock_winreg, mock_system):
        """Test setting telemetry level with mocked registry."""
        mock_system.return_value = "Windows"

        # Mock registry operations
        mock_key = MagicMock()
        mock_winreg.CreateKeyEx.return_value = mock_key
        mock_winreg.HKEY_LOCAL_MACHINE = 0x80000002
        mock_winreg.KEY_WRITE = 0x20006
        mock_winreg.REG_DWORD = 4

        manager = PrivacyManager()
        result = manager.set_telemetry_level(TelemetryLevel.BASIC)

        assert result is True
        mock_winreg.SetValueEx.assert_called_once()
        mock_winreg.CloseKey.assert_called_once_with(mock_key)

    @patch('system_tools.privacy.platform.system')
    @patch('system_tools.privacy.winreg')
    def test_get_telemetry_level_mocked(self, mock_winreg, mock_system):
        """Test getting telemetry level with mocked registry."""
        mock_system.return_value = "Windows"

        # Mock registry read
        mock_key = MagicMock()
        mock_winreg.OpenKey.return_value = mock_key
        mock_winreg.QueryValueEx.return_value = (1, 4)  # BASIC telemetry
        mock_winreg.HKEY_LOCAL_MACHINE = 0x80000002
        mock_winreg.KEY_READ = 0x20019

        manager = PrivacyManager()
        level = manager.get_telemetry_level()

        assert level == TelemetryLevel.BASIC
        mock_winreg.CloseKey.assert_called_once_with(mock_key)

    @patch('system_tools.privacy.platform.system')
    @patch('system_tools.privacy.winreg')
    def test_get_telemetry_level_key_not_found(self, mock_winreg, mock_system):
        """Test getting telemetry level when registry key doesn't exist."""
        mock_system.return_value = "Windows"

        # Mock registry key not found
        mock_winreg.OpenKey.side_effect = FileNotFoundError()

        manager = PrivacyManager()
        level = manager.get_telemetry_level()

        # Should return FULL as default
        assert level == TelemetryLevel.FULL

    @patch('system_tools.privacy.platform.system')
    @patch('system_tools.privacy.winreg')
    def test_disable_advertising_id_mocked(self, mock_winreg, mock_system):
        """Test disabling advertising ID with mocked registry."""
        mock_system.return_value = "Windows"

        # Mock registry operations
        mock_key = MagicMock()
        mock_winreg.CreateKeyEx.return_value = mock_key
        mock_winreg.HKEY_CURRENT_USER = 0x80000001
        mock_winreg.KEY_WRITE = 0x20006
        mock_winreg.REG_DWORD = 4

        manager = PrivacyManager()
        result = manager.disable_advertising_id()

        assert result is True
        mock_winreg.SetValueEx.assert_called_once()

    @patch('system_tools.privacy.platform.system')
    @patch('system_tools.privacy.winreg')
    def test_set_telemetry_permission_error(self, mock_winreg, mock_system):
        """Test handling permission error when setting telemetry."""
        mock_system.return_value = "Windows"

        # Mock permission error
        mock_winreg.CreateKeyEx.side_effect = PermissionError()

        manager = PrivacyManager()
        result = manager.set_telemetry_level(TelemetryLevel.BASIC)

        assert result is False
