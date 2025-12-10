"""Better11 Text User Interface (TUI).

A comprehensive terminal-based interface for all Better11 functionality.
"""
from __future__ import annotations

import sys
from pathlib import Path

from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Label,
    ListItem,
    ListView,
    Static,
    TabbedContent,
    TabPane,
)

# Import all managers
from better11.apps.manager import AppManager
from system_tools.startup import StartupManager
from system_tools.privacy import PrivacyManager
from system_tools.updates import WindowsUpdateManager
from system_tools.features import WindowsFeaturesManager
from system_tools.disk import DiskManager
from system_tools.network import NetworkManager
from system_tools.backup import BackupManager
from system_tools.power import PowerManager


class MainMenu(Screen):
    """Main menu screen."""
    
    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("1", "apps", "Applications"),
        Binding("2", "system", "System Tools"),
        Binding("3", "privacy", "Privacy"),
        Binding("4", "updates", "Updates"),
        Binding("5", "features", "Features"),
        Binding("6", "disk", "Disk & Storage"),
        Binding("7", "network", "Network"),
        Binding("8", "backup", "Backup"),
        Binding("9", "power", "Power"),
    ]
    
    CSS = """
    MainMenu {
        align: center middle;
    }
    
    .menu-container {
        width: 80;
        height: auto;
        border: heavy $primary;
        background: $surface;
        padding: 2;
    }
    
    .menu-title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }
    
    .menu-item {
        margin: 1 0;
    }
    """
    
    def compose(self) -> ComposeResult:
        """Create main menu layout."""
        yield Header()
        
        with Container(classes="menu-container"):
            yield Static("Better11 - Windows Enhancement Toolkit", classes="menu-title")
            yield Static()
            
            yield Button("1. Application Management", id="btn-apps", classes="menu-item")
            yield Button("2. System Optimization", id="btn-system", classes="menu-item")
            yield Button("3. Privacy & Security", id="btn-privacy", classes="menu-item")
            yield Button("4. Windows Updates", id="btn-updates", classes="menu-item")
            yield Button("5. Windows Features", id="btn-features", classes="menu-item")
            yield Button("6. Disk & Storage", id="btn-disk", classes="menu-item")
            yield Button("7. Network Tools", id="btn-network", classes="menu-item")
            yield Button("8. Backup & Restore", id="btn-backup", classes="menu-item")
            yield Button("9. Power Management", id="btn-power", classes="menu-item")
            yield Static()
            yield Button("Q. Quit", id="btn-quit", classes="menu-item")
        
        yield Footer()
    
    @on(Button.Pressed, "#btn-apps")
    def action_apps(self) -> None:
        """Show applications screen."""
        self.app.push_screen(ApplicationsScreen())
    
    @on(Button.Pressed, "#btn-system")
    def action_system(self) -> None:
        """Show system tools screen."""
        self.app.push_screen(SystemToolsScreen())
    
    @on(Button.Pressed, "#btn-privacy")
    def action_privacy(self) -> None:
        """Show privacy screen."""
        self.app.push_screen(PrivacyScreen())
    
    @on(Button.Pressed, "#btn-updates")
    def action_updates(self) -> None:
        """Show updates screen."""
        self.app.push_screen(UpdatesScreen())
    
    @on(Button.Pressed, "#btn-features")
    def action_features(self) -> None:
        """Show features screen."""
        self.app.push_screen(FeaturesScreen())
    
    @on(Button.Pressed, "#btn-disk")
    def action_disk(self) -> None:
        """Show disk screen."""
        self.app.push_screen(DiskScreen())
    
    @on(Button.Pressed, "#btn-network")
    def action_network(self) -> None:
        """Show network screen."""
        self.app.push_screen(NetworkScreen())
    
    @on(Button.Pressed, "#btn-backup")
    def action_backup(self) -> None:
        """Show backup screen."""
        self.app.push_screen(BackupScreen())
    
    @on(Button.Pressed, "#btn-power")
    def action_power(self) -> None:
        """Show power screen."""
        self.app.push_screen(PowerScreen())
    
    @on(Button.Pressed, "#btn-quit")
    def action_quit(self) -> None:
        """Quit application."""
        self.app.exit()


class ApplicationsScreen(Screen):
    """Applications management screen."""
    
    BINDINGS = [
        Binding("escape", "pop_screen", "Back"),
        Binding("l", "list_apps", "List Apps"),
        Binding("i", "install_app", "Install"),
        Binding("r", "refresh", "Refresh"),
    ]
    
    def compose(self) -> ComposeResult:
        """Create applications layout."""
        yield Header()
        
        with Vertical():
            yield Static("Application Management", id="screen-title")
            yield Static()
            
            with Horizontal():
                yield Button("List Applications", id="btn-list-apps")
                yield Button("Install Application", id="btn-install-app")
                yield Button("Application Status", id="btn-app-status")
                yield Button("Back", id="btn-back")
            
            yield Static()
            yield Static("Application List:", id="section-title")
            
            table = DataTable(id="apps-table")
            table.add_columns("App ID", "Name", "Version", "Type", "Status")
            yield table
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize screen."""
        self.load_applications()
    
    @work(exclusive=True)
    async def load_applications(self) -> None:
        """Load applications list."""
        table = self.query_one("#apps-table", DataTable)
        table.clear()
        
        try:
            catalog_path = Path(__file__).parent / "apps" / "catalog.json"
            manager = AppManager(catalog_path)
            apps = manager.list_available()
            
            for app in apps:
                status = "Installed" if hasattr(app, 'installed') and app.installed else "Available"
                table.add_row(
                    app.app_id,
                    app.name,
                    app.version,
                    app.installer_type.value,
                    status
                )
        except Exception as exc:
            table.add_row("Error", str(exc), "", "", "")
    
    @on(Button.Pressed, "#btn-back")
    def action_pop_screen(self) -> None:
        """Go back to main menu."""
        self.app.pop_screen()
    
    @on(Button.Pressed, "#btn-list-apps")
    def action_list_apps(self) -> None:
        """Reload applications list."""
        self.load_applications()
    
    def action_refresh(self) -> None:
        """Refresh applications list."""
        self.load_applications()


class SystemToolsScreen(Screen):
    """System optimization tools screen."""
    
    BINDINGS = [
        Binding("escape", "pop_screen", "Back"),
    ]
    
    def compose(self) -> ComposeResult:
        """Create system tools layout."""
        yield Header()
        
        with Vertical():
            yield Static("System Optimization Tools", id="screen-title")
            yield Static()
            
            with TabbedContent():
                with TabPane("Startup"):
                    yield StartupPane()
                
                with TabPane("Registry"):
                    yield Static("Registry Tweaks")
                    yield Static("Manage Windows registry settings with automatic backup.")
                
                with TabPane("Services"):
                    yield Static("Service Management")
                    yield Static("Control Windows services and background processes.")
                
                with TabPane("Bloatware"):
                    yield Static("Bloatware Removal")
                    yield Static("Remove unwanted pre-installed applications.")
        
        yield Footer()
    
    @on(Button.Pressed, "#btn-back")
    def action_pop_screen(self) -> None:
        """Go back to main menu."""
        self.app.pop_screen()


class StartupPane(Static):
    """Startup management pane."""
    
    def compose(self) -> ComposeResult:
        """Create startup pane layout."""
        yield Static("Startup Program Management")
        yield Static("Manage programs that run at Windows startup.")
        yield Static()
        
        with Horizontal():
            yield Button("List Startup Items", id="btn-list-startup")
            yield Button("Disable Item", id="btn-disable-startup")
            yield Button("Enable Item", id="btn-enable-startup")
        
        yield Static()
        
        table = DataTable(id="startup-table")
        table.add_columns("Name", "Command", "Location", "Status")
        yield table
    
    def on_mount(self) -> None:
        """Initialize pane."""
        self.load_startup_items()
    
    @work(exclusive=True)
    async def load_startup_items(self) -> None:
        """Load startup items."""
        table = self.query_one("#startup-table", DataTable)
        table.clear()
        
        try:
            manager = StartupManager(dry_run=True)
            items = manager.list_startup_items()
            
            for item in items:
                table.add_row(
                    item.name,
                    item.command[:50] + "..." if len(item.command) > 50 else item.command,
                    item.location.value,
                    "Enabled" if item.enabled else "Disabled"
                )
        except Exception as exc:
            table.add_row("Error", str(exc), "", "")
    
    @on(Button.Pressed, "#btn-list-startup")
    def action_list_startup(self) -> None:
        """Reload startup items."""
        self.load_startup_items()


class PrivacyScreen(Screen):
    """Privacy and security screen."""
    
    BINDINGS = [
        Binding("escape", "pop_screen", "Back"),
    ]
    
    def compose(self) -> ComposeResult:
        """Create privacy layout."""
        yield Header()
        
        with Vertical():
            yield Static("Privacy & Security", id="screen-title")
            yield Static()
            
            with Horizontal():
                yield Button("Telemetry Status", id="btn-telemetry-status")
                yield Button("Disable Telemetry", id="btn-disable-telemetry")
                yield Button("Disable Cortana", id="btn-disable-cortana")
                yield Button("Back", id="btn-back")
            
            yield Static()
            yield Static(id="privacy-status")
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize screen."""
        self.load_privacy_status()
    
    @work(exclusive=True)
    async def load_privacy_status(self) -> None:
        """Load privacy status."""
        status_widget = self.query_one("#privacy-status", Static)
        
        try:
            manager = PrivacyManager(dry_run=True)
            level = manager.get_telemetry_level()
            status_widget.update(f"Current Telemetry Level: {level.name}")
        except Exception as exc:
            status_widget.update(f"Error: {exc}")
    
    @on(Button.Pressed, "#btn-back")
    def action_pop_screen(self) -> None:
        """Go back to main menu."""
        self.app.pop_screen()
    
    @on(Button.Pressed, "#btn-telemetry-status")
    def action_telemetry_status(self) -> None:
        """Reload telemetry status."""
        self.load_privacy_status()


class UpdatesScreen(Screen):
    """Windows Updates screen."""
    
    BINDINGS = [
        Binding("escape", "pop_screen", "Back"),
    ]
    
    def compose(self) -> ComposeResult:
        """Create updates layout."""
        yield Header()
        
        with Vertical():
            yield Static("Windows Update Management", id="screen-title")
            yield Static()
            
            with Horizontal():
                yield Button("Check Updates", id="btn-check-updates")
                yield Button("Pause Updates", id="btn-pause-updates")
                yield Button("Resume Updates", id="btn-resume-updates")
                yield Button("Back", id="btn-back")
            
            yield Static()
            yield Static("Windows Update features coming in v0.3.0", id="updates-status")
        
        yield Footer()
    
    @on(Button.Pressed, "#btn-back")
    def action_pop_screen(self) -> None:
        """Go back to main menu."""
        self.app.pop_screen()


class FeaturesScreen(Screen):
    """Windows Features screen."""
    
    BINDINGS = [
        Binding("escape", "pop_screen", "Back"),
    ]
    
    def compose(self) -> ComposeResult:
        """Create features layout."""
        yield Header()
        
        with Vertical():
            yield Static("Windows Optional Features", id="screen-title")
            yield Static()
            
            with Horizontal():
                yield Button("List Features", id="btn-list-features")
                yield Button("Enable Feature", id="btn-enable-feature")
                yield Button("Disable Feature", id="btn-disable-feature")
                yield Button("Back", id="btn-back")
            
            yield Static()
            yield Static("Windows Features management coming in v0.3.0", id="features-status")
        
        yield Footer()
    
    @on(Button.Pressed, "#btn-back")
    def action_pop_screen(self) -> None:
        """Go back to main menu."""
        self.app.pop_screen()


class DiskScreen(Screen):
    """Disk and storage screen."""
    
    BINDINGS = [
        Binding("escape", "pop_screen", "Back"),
    ]
    
    def compose(self) -> ComposeResult:
        """Create disk layout."""
        yield Header()
        
        with Vertical():
            yield Static("Disk & Storage Management", id="screen-title")
            yield Static()
            
            with Horizontal():
                yield Button("Analyze Disk Space", id="btn-analyze-disk")
                yield Button("Cleanup Temp Files", id="btn-cleanup-temp")
                yield Button("Back", id="btn-back")
            
            yield Static()
            
            table = DataTable(id="disk-table")
            table.add_columns("Drive", "Label", "Total (GB)", "Used (GB)", "Free (GB)", "Usage %")
            yield table
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize screen."""
        self.load_disk_info()
    
    @work(exclusive=True)
    async def load_disk_info(self) -> None:
        """Load disk information."""
        table = self.query_one("#disk-table", DataTable)
        table.clear()
        
        try:
            manager = DiskManager(dry_run=True)
            disks = manager.analyze_disk_space()
            
            for drive_letter, disk_info in disks.items():
                table.add_row(
                    drive_letter,
                    disk_info.label,
                    f"{disk_info.total_gb:.2f}",
                    f"{disk_info.used_gb:.2f}",
                    f"{disk_info.free_gb:.2f}",
                    f"{disk_info.usage_percent:.1f}%"
                )
        except Exception as exc:
            table.add_row("Error", str(exc), "", "", "", "")
    
    @on(Button.Pressed, "#btn-back")
    def action_pop_screen(self) -> None:
        """Go back to main menu."""
        self.app.pop_screen()
    
    @on(Button.Pressed, "#btn-analyze-disk")
    def action_analyze_disk(self) -> None:
        """Reload disk information."""
        self.load_disk_info()


class NetworkScreen(Screen):
    """Network tools screen."""
    
    BINDINGS = [
        Binding("escape", "pop_screen", "Back"),
    ]
    
    def compose(self) -> ComposeResult:
        """Create network layout."""
        yield Header()
        
        with Vertical():
            yield Static("Network Tools", id="screen-title")
            yield Static()
            
            with Horizontal():
                yield Button("List Adapters", id="btn-list-adapters")
                yield Button("Flush DNS", id="btn-flush-dns")
                yield Button("Reset TCP/IP", id="btn-reset-tcp")
                yield Button("Back", id="btn-back")
            
            yield Static()
            yield Static(id="network-status")
        
        yield Footer()
    
    @on(Button.Pressed, "#btn-back")
    def action_pop_screen(self) -> None:
        """Go back to main menu."""
        self.app.pop_screen()
    
    @on(Button.Pressed, "#btn-flush-dns")
    def action_flush_dns(self) -> None:
        """Flush DNS cache."""
        status = self.query_one("#network-status", Static)
        try:
            manager = NetworkManager(dry_run=False)
            success = manager.flush_dns_cache()
            if success:
                status.update("DNS cache flushed successfully!")
            else:
                status.update("Failed to flush DNS cache")
        except Exception as exc:
            status.update(f"Error: {exc}")


class BackupScreen(Screen):
    """Backup and restore screen."""
    
    BINDINGS = [
        Binding("escape", "pop_screen", "Back"),
    ]
    
    def compose(self) -> ComposeResult:
        """Create backup layout."""
        yield Header()
        
        with Vertical():
            yield Static("Backup & Restore", id="screen-title")
            yield Static()
            
            with Horizontal():
                yield Button("List Restore Points", id="btn-list-restore")
                yield Button("Create Restore Point", id="btn-create-restore")
                yield Button("Export Settings", id="btn-export-settings")
                yield Button("Back", id="btn-back")
            
            yield Static()
            
            table = DataTable(id="restore-table")
            table.add_columns("Sequence", "Description", "Date", "Type")
            yield table
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize screen."""
        self.load_restore_points()
    
    @work(exclusive=True)
    async def load_restore_points(self) -> None:
        """Load restore points."""
        table = self.query_one("#restore-table", DataTable)
        table.clear()
        
        try:
            manager = BackupManager(dry_run=True)
            points = manager.list_restore_points()
            
            for point in points:
                table.add_row(
                    str(point.sequence_number),
                    point.description,
                    point.creation_time.strftime("%Y-%m-%d %H:%M"),
                    point.restore_point_type
                )
        except Exception as exc:
            table.add_row("Error", str(exc), "", "")
    
    @on(Button.Pressed, "#btn-back")
    def action_pop_screen(self) -> None:
        """Go back to main menu."""
        self.app.pop_screen()
    
    @on(Button.Pressed, "#btn-list-restore")
    def action_list_restore(self) -> None:
        """Reload restore points."""
        self.load_restore_points()


class PowerScreen(Screen):
    """Power management screen."""
    
    BINDINGS = [
        Binding("escape", "pop_screen", "Back"),
    ]
    
    def compose(self) -> ComposeResult:
        """Create power layout."""
        yield Header()
        
        with Vertical():
            yield Static("Power Management", id="screen-title")
            yield Static()
            
            with Horizontal():
                yield Button("List Power Plans", id="btn-list-plans")
                yield Button("Enable Hibernation", id="btn-enable-hibernate")
                yield Button("Disable Hibernation", id="btn-disable-hibernate")
                yield Button("Back", id="btn-back")
            
            yield Static()
            
            table = DataTable(id="power-table")
            table.add_columns("Name", "Type", "Status")
            yield table
        
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize screen."""
        self.load_power_plans()
    
    @work(exclusive=True)
    async def load_power_plans(self) -> None:
        """Load power plans."""
        table = self.query_one("#power-table", DataTable)
        table.clear()
        
        try:
            manager = PowerManager(dry_run=True)
            plans = manager.list_power_plans()
            
            for plan in plans:
                status = "Active" if plan.is_active else "Inactive"
                table.add_row(
                    plan.name,
                    plan.plan_type.value,
                    status
                )
        except Exception as exc:
            table.add_row("Error", str(exc), "")
    
    @on(Button.Pressed, "#btn-back")
    def action_pop_screen(self) -> None:
        """Go back to main menu."""
        self.app.pop_screen()
    
    @on(Button.Pressed, "#btn-list-plans")
    def action_list_plans(self) -> None:
        """Reload power plans."""
        self.load_power_plans()


class Better11TUI(App):
    """Better11 Terminal User Interface application."""
    
    TITLE = "Better11 TUI"
    CSS_PATH = None
    
    BINDINGS = [
        Binding("q", "quit", "Quit", show=True, priority=True),
        Binding("d", "toggle_dark", "Toggle Dark Mode", show=True),
    ]
    
    def on_mount(self) -> None:
        """Initialize application."""
        self.push_screen(MainMenu())
    
    def action_toggle_dark(self) -> None:
        """Toggle dark mode."""
        self.dark = not self.dark


def main() -> int:
    """Run the TUI application."""
    app = Better11TUI()
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
