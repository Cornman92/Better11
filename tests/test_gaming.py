"""Tests for Gaming Optimization."""
import platform
from unittest.mock import MagicMock, patch

import pytest

from system_tools.gaming import (
    GameModeState,
    GPUScheduling,
    GamingSettings,
    GamingPreset,
    GamingOptimizer,
)


class TestEnums:
    """Test enum values."""

    def test_game_mode_state(self):
        """Test GameModeState values."""
        assert GameModeState.ENABLED.value == "enabled"
        assert GameModeState.DISABLED.value == "disabled"
        assert GameModeState.UNKNOWN.value == "unknown"

    def test_gpu_scheduling(self):
        """Test GPUScheduling values."""
        assert GPUScheduling.ENABLED.value == 2
        assert GPUScheduling.DISABLED.value == 1
        assert GPUScheduling.DEFAULT.value == 0


class TestGamingSettings:
    """Test GamingSettings dataclass."""

    def test_gaming_settings_creation(self):
        """Test creating GamingSettings."""
        settings = GamingSettings(
            game_mode_enabled=True,
            game_bar_enabled=True,
            gpu_scheduling_enabled=True,
            variable_refresh_rate=True,
            auto_hdr=True,
            fullscreen_optimizations=False,
            mouse_acceleration=False,
            pointer_precision=False,
            nagle_algorithm_disabled=True,
            power_plan="High Performance"
        )

        assert settings.game_mode_enabled is True
        assert settings.gpu_scheduling_enabled is True
        assert settings.mouse_acceleration is False
        assert settings.power_plan == "High Performance"

    def test_to_dict(self):
        """Test to_dict method."""
        settings = GamingSettings(
            game_mode_enabled=True,
            game_bar_enabled=False,
            gpu_scheduling_enabled=True,
            variable_refresh_rate=False,
            auto_hdr=False,
            fullscreen_optimizations=True,
            mouse_acceleration=False,
            pointer_precision=False,
            nagle_algorithm_disabled=True,
            power_plan="Balanced"
        )

        d = settings.to_dict()
        assert d["game_mode"] is True
        assert d["game_bar"] is False
        assert d["gpu_scheduling"] is True


class TestGamingPreset:
    """Test GamingPreset dataclass."""

    def test_gaming_preset_creation(self):
        """Test creating a GamingPreset."""
        preset = GamingPreset(
            name="Test Preset",
            description="Test description",
            enable_game_mode=True,
            disable_game_bar=True,
            enable_gpu_scheduling=True,
            disable_fullscreen_optimizations=True,
            disable_mouse_acceleration=True,
            disable_nagle=True,
            high_performance_power=True,
            disable_notifications=True,
            disable_background_apps=True
        )

        assert preset.name == "Test Preset"
        assert preset.enable_game_mode is True
        assert preset.disable_game_bar is True


class TestGamingOptimizer:
    """Test GamingOptimizer class."""

    def test_manager_creation(self):
        """Test creating a gaming optimizer."""
        optimizer = GamingOptimizer()
        metadata = optimizer.get_metadata()

        assert metadata.name == "Gaming Optimizer"
        assert metadata.version == "0.3.0"
        assert metadata.requires_admin is True
        assert metadata.category == "gaming"

    def test_manager_dry_run(self):
        """Test optimizer with dry-run mode."""
        optimizer = GamingOptimizer(dry_run=True)
        assert optimizer.dry_run is True

    def test_maximum_performance_preset(self):
        """Test MAXIMUM_PERFORMANCE preset."""
        preset = GamingOptimizer.MAXIMUM_PERFORMANCE

        assert preset.name == "Maximum Performance"
        assert preset.enable_game_mode is True
        assert preset.disable_game_bar is True
        assert preset.enable_gpu_scheduling is True
        assert preset.disable_mouse_acceleration is True
        assert preset.disable_nagle is True

    def test_balanced_gaming_preset(self):
        """Test BALANCED_GAMING preset."""
        preset = GamingOptimizer.BALANCED_GAMING

        assert preset.name == "Balanced Gaming"
        assert preset.enable_game_mode is True
        assert preset.disable_game_bar is False  # Keep game bar

    def test_streaming_optimized_preset(self):
        """Test STREAMING_OPTIMIZED preset."""
        preset = GamingOptimizer.STREAMING_OPTIMIZED

        assert preset.name == "Streaming Optimized"
        assert preset.disable_game_bar is False  # Keep for recording

    def test_default_settings_preset(self):
        """Test DEFAULT_SETTINGS preset."""
        preset = GamingOptimizer.DEFAULT_SETTINGS

        assert preset.name == "Windows Default"
        assert preset.enable_gpu_scheduling is False

    @patch('system_tools.gaming.platform.system')
    def test_get_current_settings_non_windows(self, mock_system):
        """Test getting settings on non-Windows."""
        mock_system.return_value = "Linux"

        optimizer = GamingOptimizer()
        settings = optimizer.get_current_settings()

        assert settings is None

    def test_set_game_mode_dry_run(self):
        """Test setting game mode in dry-run mode."""
        optimizer = GamingOptimizer(dry_run=True)
        result = optimizer.set_game_mode(True)
        assert result is True

    def test_set_game_bar_dry_run(self):
        """Test setting game bar in dry-run mode."""
        optimizer = GamingOptimizer(dry_run=True)
        result = optimizer.set_game_bar(False)
        assert result is True

    def test_set_gpu_scheduling_dry_run(self):
        """Test setting GPU scheduling in dry-run mode."""
        optimizer = GamingOptimizer(dry_run=True)
        result = optimizer.set_gpu_scheduling(True)
        assert result is True

    def test_set_mouse_acceleration_dry_run(self):
        """Test setting mouse acceleration in dry-run mode."""
        optimizer = GamingOptimizer(dry_run=True)
        result = optimizer.set_mouse_acceleration(False)
        assert result is True

    @patch('system_tools.gaming.platform.system')
    def test_set_mouse_acceleration_non_windows(self, mock_system):
        """Test setting mouse acceleration on non-Windows."""
        mock_system.return_value = "Linux"

        optimizer = GamingOptimizer()
        result = optimizer.set_mouse_acceleration(False)

        assert result is False

    def test_disable_nagle_algorithm_dry_run(self):
        """Test disabling Nagle's algorithm in dry-run mode."""
        optimizer = GamingOptimizer(dry_run=True)
        result = optimizer.disable_nagle_algorithm()
        assert result is True

    def test_enable_nagle_algorithm_dry_run(self):
        """Test enabling Nagle's algorithm in dry-run mode."""
        optimizer = GamingOptimizer(dry_run=True)
        result = optimizer.enable_nagle_algorithm()
        assert result is True

    def test_disable_fullscreen_optimizations_dry_run(self):
        """Test disabling fullscreen optimizations in dry-run mode."""
        optimizer = GamingOptimizer(dry_run=True)
        result = optimizer.disable_fullscreen_optimizations_globally()
        assert result is True

    def test_enable_fullscreen_optimizations_dry_run(self):
        """Test enabling fullscreen optimizations in dry-run mode."""
        optimizer = GamingOptimizer(dry_run=True)
        result = optimizer.enable_fullscreen_optimizations_globally()
        assert result is True

    def test_set_high_performance_power_dry_run(self):
        """Test setting high performance power plan in dry-run mode."""
        optimizer = GamingOptimizer(dry_run=True)
        result = optimizer.set_high_performance_power()
        assert result is True

    @patch('system_tools.gaming.platform.system')
    def test_set_high_performance_power_non_windows(self, mock_system):
        """Test setting power plan on non-Windows."""
        mock_system.return_value = "Linux"

        optimizer = GamingOptimizer()
        result = optimizer.set_high_performance_power()

        assert result is False

    def test_create_ultimate_performance_plan_dry_run(self):
        """Test creating ultimate performance plan in dry-run mode."""
        optimizer = GamingOptimizer(dry_run=True)
        result = optimizer.create_ultimate_performance_plan()
        assert result is True

    @patch('system_tools.gaming.platform.system')
    def test_create_ultimate_performance_non_windows(self, mock_system):
        """Test creating power plan on non-Windows."""
        mock_system.return_value = "Linux"

        optimizer = GamingOptimizer()
        result = optimizer.create_ultimate_performance_plan()

        assert result is False

    def test_get_presets(self):
        """Test getting presets."""
        optimizer = GamingOptimizer()
        presets = optimizer.get_presets()

        assert len(presets) == 4
        assert any(p.name == "Maximum Performance" for p in presets)
        assert any(p.name == "Balanced Gaming" for p in presets)

    def test_apply_preset_dry_run(self):
        """Test applying preset in dry-run mode."""
        optimizer = GamingOptimizer(dry_run=True)
        results = optimizer.apply_preset(GamingOptimizer.MAXIMUM_PERFORMANCE)

        assert isinstance(results, dict)
        assert all(v is True for v in results.values())

    def test_validate_environment(self):
        """Test environment validation."""
        optimizer = GamingOptimizer()
        # Should not raise
        optimizer.validate_environment()


# Mocked Windows tests
class TestGamingOptimizerMocked:
    """Tests with mocked Windows registry."""

    @patch('system_tools.gaming.platform.system')
    @patch('system_tools.gaming.winreg')
    def test_get_game_mode_status_enabled(self, mock_winreg, mock_system):
        """Test getting game mode status when enabled."""
        mock_system.return_value = "Windows"
        
        mock_key = MagicMock()
        mock_winreg.OpenKey.return_value = mock_key
        mock_winreg.QueryValueEx.return_value = (1, 4)  # Enabled
        mock_winreg.HKEY_CURRENT_USER = 0x80000001
        mock_winreg.KEY_READ = 0x20019

        optimizer = GamingOptimizer()
        result = optimizer._get_game_mode_status()

        assert result is True

    @patch('system_tools.gaming.platform.system')
    @patch('system_tools.gaming.winreg')
    def test_get_game_mode_status_disabled(self, mock_winreg, mock_system):
        """Test getting game mode status when disabled."""
        mock_system.return_value = "Windows"
        
        mock_key = MagicMock()
        mock_winreg.OpenKey.return_value = mock_key
        mock_winreg.QueryValueEx.return_value = (0, 4)  # Disabled
        mock_winreg.HKEY_CURRENT_USER = 0x80000001
        mock_winreg.KEY_READ = 0x20019

        optimizer = GamingOptimizer()
        result = optimizer._get_game_mode_status()

        assert result is False

    @patch('system_tools.gaming.platform.system')
    @patch('system_tools.gaming.winreg')
    def test_get_gpu_scheduling_status_enabled(self, mock_winreg, mock_system):
        """Test getting GPU scheduling status when enabled."""
        mock_system.return_value = "Windows"
        
        mock_key = MagicMock()
        mock_winreg.OpenKey.return_value = mock_key
        mock_winreg.QueryValueEx.return_value = (2, 4)  # Enabled
        mock_winreg.HKEY_LOCAL_MACHINE = 0x80000002
        mock_winreg.KEY_READ = 0x20019

        optimizer = GamingOptimizer()
        result = optimizer._get_gpu_scheduling_status()

        assert result is True


# Windows-specific tests
@pytest.mark.skipif(platform.system() != "Windows", reason="Windows-specific test")
class TestGamingOptimizerWindows:
    """Tests that require Windows platform."""

    def test_get_current_settings_on_windows(self):
        """Test getting current settings on Windows."""
        optimizer = GamingOptimizer()
        settings = optimizer.get_current_settings()

        if settings:
            assert isinstance(settings, GamingSettings)

    def test_get_game_mode_status_on_windows(self):
        """Test getting game mode status on Windows."""
        optimizer = GamingOptimizer()
        result = optimizer._get_game_mode_status()

        assert isinstance(result, bool)

    def test_get_game_bar_status_on_windows(self):
        """Test getting game bar status on Windows."""
        optimizer = GamingOptimizer()
        result = optimizer._get_game_bar_status()

        assert isinstance(result, bool)
