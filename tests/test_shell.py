"""Tests for Shell customization."""
import platform
from unittest.mock import MagicMock, patch

import pytest

from system_tools.shell import (
    TaskbarAlignment,
    TaskbarSize,
    SearchBoxMode,
    StartMenuStyle,
    TaskbarSettings,
    StartMenuSettings,
    ShellPreset,
    ShellCustomizer,
)


class TestEnums:
    """Test enum values."""

    def test_taskbar_alignment(self):
        """Test TaskbarAlignment values."""
        assert TaskbarAlignment.LEFT.value == 0
        assert TaskbarAlignment.CENTER.value == 1

    def test_search_box_mode(self):
        """Test SearchBoxMode values."""
        assert SearchBoxMode.HIDDEN.value == 0
        assert SearchBoxMode.ICON_ONLY.value == 1
        assert SearchBoxMode.SEARCH_BOX.value == 2

    def test_start_menu_style(self):
        """Test StartMenuStyle values."""
        assert StartMenuStyle.DEFAULT.value == 0
        assert StartMenuStyle.MORE_PINS.value == 1
        assert StartMenuStyle.MORE_RECOMMENDATIONS.value == 2


class TestTaskbarSettings:
    """Test TaskbarSettings dataclass."""

    def test_taskbar_settings_creation(self):
        """Test creating TaskbarSettings."""
        settings = TaskbarSettings(
            alignment=TaskbarAlignment.LEFT,
            show_search=SearchBoxMode.ICON_ONLY,
            show_task_view=False,
            show_widgets=False,
            show_chat=False,
            show_copilot=True,
            auto_hide=False,
            use_small_icons=False,
            combine_buttons=0
        )

        assert settings.alignment == TaskbarAlignment.LEFT
        assert settings.show_task_view is False
        assert settings.show_copilot is True

    def test_to_dict(self):
        """Test to_dict method."""
        settings = TaskbarSettings(
            alignment=TaskbarAlignment.CENTER,
            show_search=SearchBoxMode.SEARCH_BOX,
            show_task_view=True,
            show_widgets=True,
            show_chat=True,
            show_copilot=True,
            auto_hide=False,
            use_small_icons=False,
            combine_buttons=0
        )

        d = settings.to_dict()
        assert d["alignment"] == "CENTER"
        assert d["show_search"] == "SEARCH_BOX"


class TestShellPreset:
    """Test ShellPreset dataclass."""

    def test_shell_preset_creation(self):
        """Test creating a ShellPreset."""
        preset = ShellPreset(
            name="Test",
            description="Test preset",
            taskbar_alignment=TaskbarAlignment.LEFT,
            search_mode=SearchBoxMode.ICON_ONLY,
            hide_widgets=True,
            hide_chat=True,
            hide_copilot=True,
            hide_task_view=True,
            enable_classic_context_menu=True,
            start_style=StartMenuStyle.MORE_PINS
        )

        assert preset.name == "Test"
        assert preset.hide_widgets is True
        assert preset.enable_classic_context_menu is True


class TestShellCustomizer:
    """Test ShellCustomizer class."""

    def test_manager_creation(self):
        """Test creating a shell customizer."""
        customizer = ShellCustomizer()
        metadata = customizer.get_metadata()

        assert metadata.name == "Shell Customizer"
        assert metadata.version == "0.3.0"
        assert metadata.requires_admin is False
        assert metadata.category == "customization"

    def test_manager_dry_run(self):
        """Test customizer with dry-run mode."""
        customizer = ShellCustomizer(dry_run=True)
        assert customizer.dry_run is True

    def test_productivity_preset(self):
        """Test PRODUCTIVITY_PRESET."""
        preset = ShellCustomizer.PRODUCTIVITY_PRESET

        assert preset.name == "Productivity"
        assert preset.taskbar_alignment == TaskbarAlignment.LEFT
        assert preset.hide_widgets is True
        assert preset.enable_classic_context_menu is True

    def test_minimalist_preset(self):
        """Test MINIMALIST_PRESET."""
        preset = ShellCustomizer.MINIMALIST_PRESET

        assert preset.name == "Minimalist"
        assert preset.search_mode == SearchBoxMode.HIDDEN
        assert preset.hide_copilot is True

    def test_classic_preset(self):
        """Test CLASSIC_PRESET."""
        preset = ShellCustomizer.CLASSIC_PRESET

        assert preset.name == "Classic"
        assert preset.taskbar_alignment == TaskbarAlignment.LEFT

    def test_default_preset(self):
        """Test DEFAULT_PRESET."""
        preset = ShellCustomizer.DEFAULT_PRESET

        assert preset.name == "Default"
        assert preset.taskbar_alignment == TaskbarAlignment.CENTER
        assert preset.hide_widgets is False

    @patch('system_tools.shell.platform.system')
    def test_get_taskbar_settings_non_windows(self, mock_system):
        """Test getting taskbar settings on non-Windows."""
        mock_system.return_value = "Linux"

        customizer = ShellCustomizer()
        settings = customizer.get_taskbar_settings()

        assert settings is None

    @patch('system_tools.shell.platform.system')
    def test_get_start_menu_settings_non_windows(self, mock_system):
        """Test getting start menu settings on non-Windows."""
        mock_system.return_value = "Linux"

        customizer = ShellCustomizer()
        settings = customizer.get_start_menu_settings()

        assert settings is None

    def test_set_taskbar_alignment_dry_run(self):
        """Test setting taskbar alignment in dry-run mode."""
        customizer = ShellCustomizer(dry_run=True)
        result = customizer.set_taskbar_alignment(TaskbarAlignment.LEFT)
        assert result is True

    def test_set_search_mode_dry_run(self):
        """Test setting search mode in dry-run mode."""
        customizer = ShellCustomizer(dry_run=True)
        result = customizer.set_search_mode(SearchBoxMode.HIDDEN)
        assert result is True

    def test_set_task_view_visible_dry_run(self):
        """Test setting task view visibility in dry-run mode."""
        customizer = ShellCustomizer(dry_run=True)
        result = customizer.set_task_view_visible(False)
        assert result is True

    def test_set_widgets_visible_dry_run(self):
        """Test setting widgets visibility in dry-run mode."""
        customizer = ShellCustomizer(dry_run=True)
        result = customizer.set_widgets_visible(False)
        assert result is True

    def test_set_chat_visible_dry_run(self):
        """Test setting chat visibility in dry-run mode."""
        customizer = ShellCustomizer(dry_run=True)
        result = customizer.set_chat_visible(False)
        assert result is True

    def test_set_copilot_visible_dry_run(self):
        """Test setting copilot visibility in dry-run mode."""
        customizer = ShellCustomizer(dry_run=True)
        result = customizer.set_copilot_visible(False)
        assert result is True

    def test_set_auto_hide_dry_run(self):
        """Test setting auto-hide in dry-run mode."""
        customizer = ShellCustomizer(dry_run=True)
        result = customizer.set_auto_hide(True)
        assert result is True

    def test_enable_classic_context_menu_dry_run(self):
        """Test enabling classic context menu in dry-run mode."""
        customizer = ShellCustomizer(dry_run=True)
        result = customizer.enable_classic_context_menu()
        assert result is True

    def test_disable_classic_context_menu_dry_run(self):
        """Test disabling classic context menu in dry-run mode."""
        customizer = ShellCustomizer(dry_run=True)
        result = customizer.disable_classic_context_menu()
        assert result is True

    @patch('system_tools.shell.platform.system')
    def test_is_classic_context_menu_enabled_non_windows(self, mock_system):
        """Test checking classic menu on non-Windows."""
        mock_system.return_value = "Linux"

        customizer = ShellCustomizer()
        result = customizer.is_classic_context_menu_enabled()

        assert result is False

    def test_set_start_layout_dry_run(self):
        """Test setting start layout in dry-run mode."""
        customizer = ShellCustomizer(dry_run=True)
        result = customizer.set_start_layout(StartMenuStyle.MORE_PINS)
        assert result is True

    def test_set_show_recent_apps_dry_run(self):
        """Test setting show recent apps in dry-run mode."""
        customizer = ShellCustomizer(dry_run=True)
        result = customizer.set_show_recent_apps(False)
        assert result is True

    def test_set_show_recent_files_dry_run(self):
        """Test setting show recent files in dry-run mode."""
        customizer = ShellCustomizer(dry_run=True)
        result = customizer.set_show_recent_files(False)
        assert result is True

    def test_set_show_desktop_icons_dry_run(self):
        """Test setting desktop icons visibility in dry-run mode."""
        customizer = ShellCustomizer(dry_run=True)
        result = customizer.set_show_desktop_icons(False)
        assert result is True

    def test_set_show_recycle_bin_dry_run(self):
        """Test setting recycle bin visibility in dry-run mode."""
        customizer = ShellCustomizer(dry_run=True)
        result = customizer.set_show_recycle_bin(False)
        assert result is True

    def test_restart_explorer_dry_run(self):
        """Test restarting explorer in dry-run mode."""
        customizer = ShellCustomizer(dry_run=True)
        result = customizer.restart_explorer()
        assert result is True

    @patch('system_tools.shell.platform.system')
    def test_restart_explorer_non_windows(self, mock_system):
        """Test restarting explorer on non-Windows."""
        mock_system.return_value = "Linux"

        customizer = ShellCustomizer()
        result = customizer.restart_explorer()

        assert result is False

    def test_get_presets(self):
        """Test getting presets."""
        customizer = ShellCustomizer()
        presets = customizer.get_presets()

        assert len(presets) == 4
        assert any(p.name == "Productivity" for p in presets)
        assert any(p.name == "Minimalist" for p in presets)

    def test_apply_preset_dry_run(self):
        """Test applying preset in dry-run mode."""
        customizer = ShellCustomizer(dry_run=True)
        result = customizer.apply_preset(ShellCustomizer.PRODUCTIVITY_PRESET)
        assert result is True

    def test_validate_environment(self):
        """Test environment validation."""
        customizer = ShellCustomizer()
        # Should not raise
        customizer.validate_environment()


# Windows-specific tests
@pytest.mark.skipif(platform.system() != "Windows", reason="Windows-specific test")
class TestShellCustomizerWindows:
    """Tests that require Windows platform."""

    def test_get_taskbar_settings_on_windows(self):
        """Test getting taskbar settings on Windows."""
        customizer = ShellCustomizer()
        settings = customizer.get_taskbar_settings()

        if settings:
            assert isinstance(settings, TaskbarSettings)

    def test_is_classic_context_menu_enabled_on_windows(self):
        """Test checking classic menu on Windows."""
        customizer = ShellCustomizer()
        result = customizer.is_classic_context_menu_enabled()

        assert isinstance(result, bool)
