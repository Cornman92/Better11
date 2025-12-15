"""Windows Shell and Explorer customization.

This module provides customization options for the Windows 11 taskbar,
Start menu, context menus, and other shell elements.
"""
from __future__ import annotations

import platform
import subprocess
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

from . import get_logger
from .base import SystemTool, ToolMetadata

# Import winreg for Windows, use compatibility module for non-Windows
try:
    import winreg
except ImportError:
    from . import winreg_compat as winreg

_LOGGER = get_logger(__name__)


class TaskbarAlignment(Enum):
    """Taskbar alignment options."""
    
    LEFT = 0
    CENTER = 1


class TaskbarSize(Enum):
    """Taskbar size options."""
    
    SMALL = 0
    DEFAULT = 1
    LARGE = 2


class SearchBoxMode(Enum):
    """Search box display mode."""
    
    HIDDEN = 0
    ICON_ONLY = 1
    SEARCH_BOX = 2
    ICON_AND_LABEL = 3


class StartMenuStyle(Enum):
    """Start menu style."""
    
    DEFAULT = 0
    MORE_PINS = 1
    MORE_RECOMMENDATIONS = 2


@dataclass
class TaskbarSettings:
    """Current taskbar settings."""
    
    alignment: TaskbarAlignment
    show_search: SearchBoxMode
    show_task_view: bool
    show_widgets: bool
    show_chat: bool
    show_copilot: bool
    auto_hide: bool
    use_small_icons: bool
    combine_buttons: int  # 0=always, 1=when full, 2=never

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "alignment": self.alignment.name,
            "show_search": self.show_search.name,
            "show_task_view": self.show_task_view,
            "show_widgets": self.show_widgets,
            "show_chat": self.show_chat,
            "show_copilot": self.show_copilot,
            "auto_hide": self.auto_hide,
            "use_small_icons": self.use_small_icons,
            "combine_buttons": self.combine_buttons
        }


@dataclass
class StartMenuSettings:
    """Current Start menu settings."""
    
    style: StartMenuStyle
    show_recently_added: bool
    show_most_used: bool
    show_recently_opened: bool
    folders_shown: List[str]

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "style": self.style.name,
            "show_recently_added": self.show_recently_added,
            "show_most_used": self.show_most_used,
            "show_recently_opened": self.show_recently_opened,
            "folders_shown": self.folders_shown
        }


@dataclass
class ShellPreset:
    """Predefined shell customization preset."""
    
    name: str
    description: str
    taskbar_alignment: TaskbarAlignment
    search_mode: SearchBoxMode
    hide_widgets: bool
    hide_chat: bool
    hide_copilot: bool
    hide_task_view: bool
    enable_classic_context_menu: bool
    start_style: StartMenuStyle


class ShellCustomizer(SystemTool):
    """Customize Windows 11 shell appearance and behavior.
    
    This class provides methods to customize the taskbar, Start menu,
    context menus, and other Windows 11 shell elements.
    
    Parameters
    ----------
    config : dict, optional
        Configuration dictionary
    dry_run : bool
        If True, simulate operations without making changes
    """
    
    # Registry paths
    EXPLORER_ADVANCED = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
    EXPLORER_SEARCH = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Search"
    START_MENU = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Start"
    PERSONALIZE = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize"
    
    # Predefined presets
    PRODUCTIVITY_PRESET = ShellPreset(
        name="Productivity",
        description="Clean taskbar focused on work",
        taskbar_alignment=TaskbarAlignment.LEFT,
        search_mode=SearchBoxMode.ICON_ONLY,
        hide_widgets=True,
        hide_chat=True,
        hide_copilot=False,
        hide_task_view=True,
        enable_classic_context_menu=True,
        start_style=StartMenuStyle.MORE_PINS
    )
    
    MINIMALIST_PRESET = ShellPreset(
        name="Minimalist",
        description="Absolute minimal taskbar",
        taskbar_alignment=TaskbarAlignment.CENTER,
        search_mode=SearchBoxMode.HIDDEN,
        hide_widgets=True,
        hide_chat=True,
        hide_copilot=True,
        hide_task_view=True,
        enable_classic_context_menu=True,
        start_style=StartMenuStyle.MORE_PINS
    )
    
    CLASSIC_PRESET = ShellPreset(
        name="Classic",
        description="Windows 10-like experience",
        taskbar_alignment=TaskbarAlignment.LEFT,
        search_mode=SearchBoxMode.SEARCH_BOX,
        hide_widgets=True,
        hide_chat=True,
        hide_copilot=True,
        hide_task_view=False,
        enable_classic_context_menu=True,
        start_style=StartMenuStyle.MORE_PINS
    )
    
    DEFAULT_PRESET = ShellPreset(
        name="Default",
        description="Windows 11 default settings",
        taskbar_alignment=TaskbarAlignment.CENTER,
        search_mode=SearchBoxMode.SEARCH_BOX,
        hide_widgets=False,
        hide_chat=False,
        hide_copilot=False,
        hide_task_view=False,
        enable_classic_context_menu=False,
        start_style=StartMenuStyle.DEFAULT
    )
    
    def __init__(self, config: Optional[dict] = None, dry_run: bool = False):
        super().__init__(config, dry_run)
    
    def get_metadata(self) -> ToolMetadata:
        """Return tool metadata."""
        return ToolMetadata(
            name="Shell Customizer",
            description="Customize Windows 11 taskbar, Start menu, and shell",
            version="0.3.0",
            requires_admin=False,
            requires_restart=False,  # Explorer restart usually sufficient
            category="customization"
        )
    
    def validate_environment(self) -> None:
        """Validate shell customization prerequisites."""
        pass
    
    def execute(self) -> bool:
        """Execute default settings display operation."""
        settings = self.get_taskbar_settings()
        if settings:
            _LOGGER.info("Current taskbar alignment: %s", settings.alignment.name)
        return True
    
    # Taskbar customization
    
    def get_taskbar_settings(self) -> Optional[TaskbarSettings]:
        """Get current taskbar settings.
        
        Returns
        -------
        TaskbarSettings, optional
            Current settings or None if unavailable
        """
        if platform.system() != "Windows":
            return None
        
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.EXPLORER_ADVANCED,
                0,
                winreg.KEY_READ
            )
            
            def get_value(name: str, default: int = 0) -> int:
                try:
                    value, _ = winreg.QueryValueEx(key, name)
                    return value
                except FileNotFoundError:
                    return default
            
            alignment = TaskbarAlignment(get_value("TaskbarAl", 1))
            search = SearchBoxMode(get_value("SearchboxTaskbarMode", 2))
            
            settings = TaskbarSettings(
                alignment=alignment,
                show_search=search,
                show_task_view=get_value("ShowTaskViewButton", 1) == 1,
                show_widgets=get_value("TaskbarDa", 1) == 1,
                show_chat=get_value("TaskbarMn", 1) == 1,
                show_copilot=get_value("ShowCopilotButton", 1) == 1,
                auto_hide=get_value("TaskbarAutoHide", 0) == 1,
                use_small_icons=get_value("TaskbarSmallIcons", 0) == 1,
                combine_buttons=get_value("TaskbarGlomLevel", 0)
            )
            
            winreg.CloseKey(key)
            return settings
        
        except Exception as exc:
            _LOGGER.error("Failed to get taskbar settings: %s", exc)
            return None
    
    def set_taskbar_alignment(self, alignment: TaskbarAlignment) -> bool:
        """Set taskbar alignment.
        
        Parameters
        ----------
        alignment : TaskbarAlignment
            Desired alignment (LEFT or CENTER)
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Setting taskbar alignment to %s", alignment.name)
        return self._set_registry_value(
            self.EXPLORER_ADVANCED, "TaskbarAl", alignment.value
        )
    
    def set_search_mode(self, mode: SearchBoxMode) -> bool:
        """Set search box display mode.
        
        Parameters
        ----------
        mode : SearchBoxMode
            Desired search display mode
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Setting search mode to %s", mode.name)
        return self._set_registry_value(
            self.EXPLORER_ADVANCED, "SearchboxTaskbarMode", mode.value
        )
    
    def set_task_view_visible(self, visible: bool) -> bool:
        """Show or hide Task View button.
        
        Parameters
        ----------
        visible : bool
            Whether to show the button
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Setting Task View visibility to %s", visible)
        return self._set_registry_value(
            self.EXPLORER_ADVANCED, "ShowTaskViewButton", 1 if visible else 0
        )
    
    def set_widgets_visible(self, visible: bool) -> bool:
        """Show or hide Widgets button.
        
        Parameters
        ----------
        visible : bool
            Whether to show the button
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Setting Widgets visibility to %s", visible)
        return self._set_registry_value(
            self.EXPLORER_ADVANCED, "TaskbarDa", 1 if visible else 0
        )
    
    def set_chat_visible(self, visible: bool) -> bool:
        """Show or hide Chat button.
        
        Parameters
        ----------
        visible : bool
            Whether to show the button
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Setting Chat visibility to %s", visible)
        return self._set_registry_value(
            self.EXPLORER_ADVANCED, "TaskbarMn", 1 if visible else 0
        )
    
    def set_copilot_visible(self, visible: bool) -> bool:
        """Show or hide Copilot button.
        
        Parameters
        ----------
        visible : bool
            Whether to show the button
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Setting Copilot visibility to %s", visible)
        return self._set_registry_value(
            self.EXPLORER_ADVANCED, "ShowCopilotButton", 1 if visible else 0
        )
    
    def set_auto_hide(self, enabled: bool) -> bool:
        """Enable or disable taskbar auto-hide.
        
        Parameters
        ----------
        enabled : bool
            Whether to auto-hide
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Setting taskbar auto-hide to %s", enabled)
        return self._set_registry_value(
            self.EXPLORER_ADVANCED, "TaskbarAutoHide", 1 if enabled else 0
        )
    
    # Context menu customization
    
    def enable_classic_context_menu(self) -> bool:
        """Enable Windows 10-style classic context menu.
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Enabling classic context menu")
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would enable classic context menu")
            return True
        
        if platform.system() != "Windows":
            _LOGGER.error("Context menu customization only available on Windows")
            return False
        
        try:
            # Create the key that enables classic menu
            key_path = r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32"
            
            key = winreg.CreateKeyEx(
                winreg.HKEY_CURRENT_USER,
                key_path,
                0,
                winreg.KEY_WRITE
            )
            
            # Set default value to empty string
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "")
            winreg.CloseKey(key)
            
            _LOGGER.info("Classic context menu enabled. Explorer restart required.")
            return True
        
        except Exception as exc:
            _LOGGER.error("Failed to enable classic context menu: %s", exc)
            return False
    
    def disable_classic_context_menu(self) -> bool:
        """Restore Windows 11-style context menu.
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Disabling classic context menu")
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would disable classic context menu")
            return True
        
        if platform.system() != "Windows":
            return False
        
        try:
            # Delete the key that enables classic menu
            key_path = r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}"
            
            try:
                winreg.DeleteKey(
                    winreg.HKEY_CURRENT_USER,
                    key_path + r"\InprocServer32"
                )
                winreg.DeleteKey(
                    winreg.HKEY_CURRENT_USER,
                    key_path
                )
            except FileNotFoundError:
                pass  # Already using Windows 11 menu
            
            _LOGGER.info("Windows 11 context menu restored. Explorer restart required.")
            return True
        
        except Exception as exc:
            _LOGGER.error("Failed to restore Windows 11 context menu: %s", exc)
            return False
    
    def is_classic_context_menu_enabled(self) -> bool:
        """Check if classic context menu is enabled.
        
        Returns
        -------
        bool
            True if classic menu is enabled
        """
        if platform.system() != "Windows":
            return False
        
        try:
            key_path = r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32"
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                key_path,
                0,
                winreg.KEY_READ
            )
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            return False
    
    # Start menu customization
    
    def get_start_menu_settings(self) -> Optional[StartMenuSettings]:
        """Get current Start menu settings.
        
        Returns
        -------
        StartMenuSettings, optional
            Current settings or None if unavailable
        """
        if platform.system() != "Windows":
            return None
        
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.EXPLORER_ADVANCED,
                0,
                winreg.KEY_READ
            )
            
            def get_value(name: str, default: int = 1) -> int:
                try:
                    value, _ = winreg.QueryValueEx(key, name)
                    return value
                except FileNotFoundError:
                    return default
            
            settings = StartMenuSettings(
                style=StartMenuStyle(get_value("Start_Layout", 0)),
                show_recently_added=get_value("Start_TrackProgs", 1) == 1,
                show_most_used=get_value("Start_TrackProgs", 1) == 1,
                show_recently_opened=get_value("Start_TrackDocs", 1) == 1,
                folders_shown=[]  # Would need additional parsing
            )
            
            winreg.CloseKey(key)
            return settings
        
        except Exception as exc:
            _LOGGER.error("Failed to get Start menu settings: %s", exc)
            return None
    
    def set_start_layout(self, style: StartMenuStyle) -> bool:
        """Set Start menu layout style.
        
        Parameters
        ----------
        style : StartMenuStyle
            Desired layout style
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Setting Start menu style to %s", style.name)
        return self._set_registry_value(
            self.EXPLORER_ADVANCED, "Start_Layout", style.value
        )
    
    def set_show_recent_apps(self, enabled: bool) -> bool:
        """Show or hide recently added apps in Start menu.
        
        Parameters
        ----------
        enabled : bool
            Whether to show recently added apps
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Setting show recent apps to %s", enabled)
        return self._set_registry_value(
            self.EXPLORER_ADVANCED, "Start_TrackProgs", 1 if enabled else 0
        )
    
    def set_show_recent_files(self, enabled: bool) -> bool:
        """Show or hide recently opened files in Start menu.
        
        Parameters
        ----------
        enabled : bool
            Whether to show recently opened files
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Setting show recent files to %s", enabled)
        return self._set_registry_value(
            self.EXPLORER_ADVANCED, "Start_TrackDocs", 1 if enabled else 0
        )
    
    # Desktop customization
    
    def set_show_desktop_icons(self, visible: bool) -> bool:
        """Show or hide desktop icons.
        
        Parameters
        ----------
        visible : bool
            Whether to show icons
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Setting desktop icons visibility to %s", visible)
        return self._set_registry_value(
            self.EXPLORER_ADVANCED, "HideIcons", 0 if visible else 1
        )
    
    def set_show_recycle_bin(self, visible: bool) -> bool:
        """Show or hide Recycle Bin on desktop.
        
        Parameters
        ----------
        visible : bool
            Whether to show Recycle Bin
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Setting Recycle Bin visibility to %s", visible)
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would set Recycle Bin visibility")
            return True
        
        if platform.system() != "Windows":
            return False
        
        try:
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\HideDesktopIcons\NewStartPanel"
            recycle_bin_guid = "{645FF040-5081-101B-9F08-00AA002F954E}"
            
            key = winreg.CreateKeyEx(
                winreg.HKEY_CURRENT_USER,
                key_path,
                0,
                winreg.KEY_WRITE
            )
            
            winreg.SetValueEx(key, recycle_bin_guid, 0, winreg.REG_DWORD, 0 if visible else 1)
            winreg.CloseKey(key)
            
            return True
        
        except Exception as exc:
            _LOGGER.error("Failed to set Recycle Bin visibility: %s", exc)
            return False
    
    # Presets
    
    def apply_preset(self, preset: ShellPreset) -> bool:
        """Apply a shell customization preset.
        
        Parameters
        ----------
        preset : ShellPreset
            Preset to apply
        
        Returns
        -------
        bool
            True if all settings applied successfully
        """
        _LOGGER.info("Applying shell preset: %s", preset.name)
        
        success = True
        
        # Apply taskbar settings
        success &= self.set_taskbar_alignment(preset.taskbar_alignment)
        success &= self.set_search_mode(preset.search_mode)
        success &= self.set_widgets_visible(not preset.hide_widgets)
        success &= self.set_chat_visible(not preset.hide_chat)
        success &= self.set_copilot_visible(not preset.hide_copilot)
        success &= self.set_task_view_visible(not preset.hide_task_view)
        
        # Apply context menu setting
        if preset.enable_classic_context_menu:
            success &= self.enable_classic_context_menu()
        else:
            success &= self.disable_classic_context_menu()
        
        # Apply Start menu setting
        success &= self.set_start_layout(preset.start_style)
        
        if success:
            _LOGGER.info("Preset applied successfully. Restart Explorer to see changes.")
        else:
            _LOGGER.warning("Some preset settings may not have been applied")
        
        return success
    
    def get_presets(self) -> List[ShellPreset]:
        """Get all available shell presets.
        
        Returns
        -------
        List[ShellPreset]
            Available presets
        """
        return [
            self.PRODUCTIVITY_PRESET,
            self.MINIMALIST_PRESET,
            self.CLASSIC_PRESET,
            self.DEFAULT_PRESET
        ]
    
    # Explorer management
    
    def restart_explorer(self) -> bool:
        """Restart Windows Explorer to apply changes.
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Restarting Explorer...")
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would restart Explorer")
            return True
        
        if platform.system() != "Windows":
            return False
        
        try:
            # Kill explorer
            subprocess.run(
                ["taskkill", "/f", "/im", "explorer.exe"],
                capture_output=True,
                timeout=10
            )
            
            # Start explorer
            subprocess.Popen(
                ["explorer.exe"],
                creationflags=subprocess.DETACHED_PROCESS
            )
            
            _LOGGER.info("Explorer restarted")
            return True
        
        except Exception as exc:
            _LOGGER.error("Failed to restart Explorer: %s", exc)
            return False
    
    # Helper methods
    
    def _set_registry_value(self, key_path: str, value_name: str, value: int) -> bool:
        """Set a registry DWORD value.
        
        Parameters
        ----------
        key_path : str
            Registry key path
        value_name : str
            Value name
        value : int
            Value to set
        
        Returns
        -------
        bool
            True if successful
        """
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would set %s\\%s to %d", key_path, value_name, value)
            return True
        
        if platform.system() != "Windows":
            _LOGGER.error("Registry operations only available on Windows")
            return False
        
        try:
            key = winreg.CreateKeyEx(
                winreg.HKEY_CURRENT_USER,
                key_path,
                0,
                winreg.KEY_WRITE
            )
            
            winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, value)
            winreg.CloseKey(key)
            
            return True
        
        except Exception as exc:
            _LOGGER.error("Failed to set registry value: %s", exc)
            return False


__all__ = [
    "TaskbarAlignment",
    "TaskbarSize",
    "SearchBoxMode",
    "StartMenuStyle",
    "TaskbarSettings",
    "StartMenuSettings",
    "ShellPreset",
    "ShellCustomizer",
]
