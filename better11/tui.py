"""
Terminal User Interface (TUI) for Better11

Comprehensive TUI using Rich/Textual for all features:
- Image management
- ISO download and USB creation
- Windows updates
- Driver management
- Package management
- System optimization
- File management
"""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.layout import Layout
from rich.live import Live
from rich import print as rprint
from typing import Optional, List, Dict
import sys


class Better11TUI:
    """Main TUI application"""

    def __init__(self):
        self.console = Console()
        self.running = True

    def clear_screen(self):
        """Clear console screen"""
        self.console.clear()

    def show_header(self):
        """Display application header"""
        header = Panel(
            "[bold cyan]Better11[/bold cyan] - Windows Management Toolkit\n"
            "[dim]Comprehensive Windows optimization and management[/dim]",
            style="bold blue"
        )
        self.console.print(header)
        self.console.print()

    def show_main_menu(self) -> str:
        """Display main menu and get selection"""
        menu_items = [
            ("1", "Image Management", "WIM/ESD/ISO editing and deployment"),
            ("2", "ISO & USB Creator", "Download Windows ISO and create bootable USB"),
            ("3", "Windows Updates", "Manage Windows updates"),
            ("4", "Driver Management", "Install, backup, and inject drivers"),
            ("5", "Package Manager", "Install apps (WinGet, Choco, NPM, Pip, etc.)"),
            ("6", "System Optimizer", "Optimize system performance"),
            ("7", "File Manager", "Advanced file operations and optimization"),
            ("8", "System Info", "View system information and health"),
            ("9", "Settings", "Configure Better11"),
            ("0", "Exit", "Exit the application")
        ]

        table = Table(show_header=True, header_style="bold magenta", box=None)
        table.add_column("Option", style="cyan", width=8)
        table.add_column("Feature", style="green")
        table.add_column("Description", style="dim")

        for option, feature, description in menu_items:
            table.add_row(option, feature, description)

        self.console.print(table)
        self.console.print()

        choice = Prompt.ask("Select option", choices=[str(i) for i in range(10)])
        return choice

    def image_management_menu(self):
        """Image management submenu"""
        from better11.image_manager import ImageManager

        self.clear_screen()
        self.show_header()

        rprint("[bold yellow]Image Management[/bold yellow]\n")

        options = [
            ("1", "Mount WIM/ESD"),
            ("2", "Unmount image"),
            ("3", "Inject drivers to image"),
            ("4", "Inject updates to image"),
            ("5", "Apply image to drive"),
            ("6", "Capture image"),
            ("7", "Optimize image"),
            ("0", "Back")
        ]

        table = Table(show_header=False, box=None)
        for opt, desc in options:
            table.add_row(f"[cyan]{opt}[/cyan]", desc)

        self.console.print(table)
        choice = Prompt.ask("\nSelect option", choices=[o[0] for o in options])

        manager = ImageManager()

        if choice == "1":
            image_path = Prompt.ask("Enter image path (WIM/ESD)")
            index = int(Prompt.ask("Enter index", default="1"))

            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                task = progress.add_task("Mounting image...", total=None)
                try:
                    mount_point = manager.mount_wim(image_path, index)
                    progress.update(task, completed=True)
                    rprint(f"\n[green]✓[/green] Image mounted at: {mount_point.path}")
                except Exception as e:
                    rprint(f"\n[red]✗[/red] Error: {e}")

            Prompt.ask("\nPress Enter to continue")

        elif choice == "3":
            image_path = Prompt.ask("Enter image path")
            driver_path = Prompt.ask("Enter driver folder path")

            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                task = progress.add_task("Injecting drivers...", total=None)
                try:
                    success = manager.inject_drivers_to_image(image_path, driver_path)
                    if success:
                        rprint("\n[green]✓[/green] Drivers injected successfully")
                    else:
                        rprint("\n[red]✗[/red] Failed to inject drivers")
                except Exception as e:
                    rprint(f"\n[red]✗[/red] Error: {e}")

            Prompt.ask("\nPress Enter to continue")

    def iso_usb_menu(self):
        """ISO and USB creation submenu"""
        from better11.iso_manager import USBBootCreator, list_usb_drives

        self.clear_screen()
        self.show_header()

        rprint("[bold yellow]ISO & USB Creator[/bold yellow]\n")

        options = [
            ("1", "List USB drives"),
            ("2", "Create bootable USB"),
            ("3", "Download Windows ISO (placeholder)"),
            ("0", "Back")
        ]

        table = Table(show_header=False, box=None)
        for opt, desc in options:
            table.add_row(f"[cyan]{opt}[/cyan]", desc)

        self.console.print(table)
        choice = Prompt.ask("\nSelect option", choices=[o[0] for o in options])

        if choice == "1":
            rprint("\n[bold]USB Drives:[/bold]\n")
            devices = list_usb_drives()

            if devices:
                table = Table(show_header=True, header_style="bold")
                table.add_column("Device ID")
                table.add_column("Name")
                table.add_column("Size")
                table.add_column("Drive Letter")

                for device in devices:
                    size_gb = device.size / (1024**3)
                    table.add_row(
                        device.device_id,
                        device.name,
                        f"{size_gb:.2f} GB",
                        device.drive_letter or "N/A"
                    )

                self.console.print(table)
            else:
                rprint("[yellow]No USB drives found[/yellow]")

            Prompt.ask("\nPress Enter to continue")

        elif choice == "2":
            iso_path = Prompt.ask("Enter ISO file path")
            drive_letter = Prompt.ask("Enter USB drive letter (e.g., E)")

            if Confirm.ask(f"\n[red]WARNING:[/red] This will erase all data on {drive_letter}:. Continue?"):
                creator = USBBootCreator()

                with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                    task = progress.add_task("Creating bootable USB...", total=None)
                    try:
                        success = creator.create_bootable_usb_simple(iso_path, drive_letter)
                        if success:
                            rprint("\n[green]✓[/green] Bootable USB created successfully")
                        else:
                            rprint("\n[red]✗[/red] Failed to create bootable USB")
                    except Exception as e:
                        rprint(f"\n[red]✗[/red] Error: {e}")

                Prompt.ask("\nPress Enter to continue")

    def updates_menu(self):
        """Windows updates submenu"""
        from better11.update_manager import WindowsUpdateManager

        self.clear_screen()
        self.show_header()

        rprint("[bold yellow]Windows Update Manager[/bold yellow]\n")

        options = [
            ("1", "Check for updates"),
            ("2", "Install all updates"),
            ("3", "View update history"),
            ("4", "Pause updates"),
            ("5", "Resume updates"),
            ("0", "Back")
        ]

        table = Table(show_header=False, box=None)
        for opt, desc in options:
            table.add_row(f"[cyan]{opt}[/cyan]", desc)

        self.console.print(table)
        choice = Prompt.ask("\nSelect option", choices=[o[0] for o in options])

        manager = WindowsUpdateManager()

        if choice == "1":
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                task = progress.add_task("Checking for updates...", total=None)
                try:
                    updates = manager.check_for_updates()
                    progress.stop()

                    if updates:
                        rprint(f"\n[green]Found {len(updates)} updates:[/green]\n")

                        table = Table(show_header=True, header_style="bold")
                        table.add_column("Title", style="cyan")
                        table.add_column("Type")
                        table.add_column("Size")

                        for update in updates[:10]:  # Show first 10
                            size_mb = update.size / (1024**2)
                            table.add_row(update.title, update.type.value, f"{size_mb:.1f} MB")

                        self.console.print(table)
                    else:
                        rprint("\n[green]✓[/green] System is up to date")
                except Exception as e:
                    rprint(f"\n[red]✗[/red] Error: {e}")

            Prompt.ask("\nPress Enter to continue")

        elif choice == "2":
            if Confirm.ask("\nInstall all available updates?"):
                with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                    task = progress.add_task("Installing updates...", total=None)
                    try:
                        success, reboot_required = manager.install_updates()
                        if success:
                            rprint("\n[green]✓[/green] Updates installed successfully")
                            if reboot_required:
                                rprint("[yellow]⚠[/yellow] Reboot required")
                        else:
                            rprint("\n[red]✗[/red] Failed to install updates")
                    except Exception as e:
                        rprint(f"\n[red]✗[/red] Error: {e}")

                Prompt.ask("\nPress Enter to continue")

    def driver_menu(self):
        """Driver management submenu"""
        from better11.driver_manager import DriverManager

        self.clear_screen()
        self.show_header()

        rprint("[bold yellow]Driver Manager[/bold yellow]\n")

        options = [
            ("1", "List installed drivers"),
            ("2", "Find missing drivers"),
            ("3", "Backup all drivers"),
            ("4", "Install driver package"),
            ("5", "Inject drivers to image"),
            ("0", "Back")
        ]

        table = Table(show_header=False, box=None)
        for opt, desc in options:
            table.add_row(f"[cyan]{opt}[/cyan]", desc)

        self.console.print(table)
        choice = Prompt.ask("\nSelect option", choices=[o[0] for o in options])

        manager = DriverManager()

        if choice == "1":
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                task = progress.add_task("Loading drivers...", total=None)
                drivers = manager.get_all_drivers()
                progress.stop()

            if drivers:
                rprint(f"\n[green]Found {len(drivers)} drivers:[/green]\n")

                table = Table(show_header=True, header_style="bold")
                table.add_column("Device", style="cyan")
                table.add_column("Version")
                table.add_column("Provider")

                for driver in drivers[:20]:  # Show first 20
                    table.add_row(driver.device_name, driver.driver_version, driver.driver_provider)

                self.console.print(table)

            Prompt.ask("\nPress Enter to continue")

        elif choice == "3":
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                task = progress.add_task("Backing up drivers...", total=None)
                try:
                    count, backup_path = manager.backup_all_drivers()
                    rprint(f"\n[green]✓[/green] Backed up {count} drivers to: {backup_path}")
                except Exception as e:
                    rprint(f"\n[red]✗[/red] Error: {e}")

            Prompt.ask("\nPress Enter to continue")

    def package_menu(self):
        """Package manager submenu"""
        from better11.package_manager import UnifiedPackageManager, PackageManager

        self.clear_screen()
        self.show_header()

        rprint("[bold yellow]Package Manager[/bold yellow]\n")

        options = [
            ("1", "Search packages"),
            ("2", "List installed packages"),
            ("3", "Install package"),
            ("4", "Update all packages"),
            ("5", "Show available package managers"),
            ("0", "Back")
        ]

        table = Table(show_header=False, box=None)
        for opt, desc in options:
            table.add_row(f"[cyan]{opt}[/cyan]", desc)

        self.console.print(table)
        choice = Prompt.ask("\nSelect option", choices=[o[0] for o in options])

        manager = UnifiedPackageManager()

        if choice == "1":
            query = Prompt.ask("Search for")

            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                task = progress.add_task("Searching...", total=None)
                results = manager.search(query)
                progress.stop()

            for mgr_type, packages in results.items():
                rprint(f"\n[bold]{mgr_type.value}:[/bold] {len(packages)} results")

                if packages:
                    table = Table(show_header=True, header_style="bold")
                    table.add_column("Name", style="cyan")
                    table.add_column("ID")
                    table.add_column("Version")

                    for pkg in packages[:5]:
                        table.add_row(pkg.name, pkg.package_id, pkg.version)

                    self.console.print(table)

            Prompt.ask("\nPress Enter to continue")

    def optimizer_menu(self):
        """System optimizer submenu"""
        from better11.system_optimizer import SystemOptimizer, OptimizationLevel

        self.clear_screen()
        self.show_header()

        rprint("[bold yellow]System Optimizer[/bold yellow]\n")

        options = [
            ("1", "Quick optimize (Gaming)"),
            ("2", "Quick optimize (Productivity)"),
            ("3", "View system metrics"),
            ("4", "Clean system"),
            ("5", "Custom optimization"),
            ("0", "Back")
        ]

        table = Table(show_header=False, box=None)
        for opt, desc in options:
            table.add_row(f"[cyan]{opt}[/cyan]", desc)

        self.console.print(table)
        choice = Prompt.ask("\nSelect option", choices=[o[0] for o in options])

        optimizer = SystemOptimizer()

        if choice == "1":
            if Confirm.ask("\nApply gaming optimizations?"):
                with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                    task = progress.add_task("Optimizing...", total=None)
                    results = optimizer.optimize_for_gaming()
                    progress.stop()

                success_count = sum(1 for r in results if r.success)
                rprint(f"\n[green]✓[/green] Applied {success_count}/{len(results)} optimizations")

                Prompt.ask("\nPress Enter to continue")

        elif choice == "3":
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
                task = progress.add_task("Collecting metrics...", total=None)
                metrics = optimizer.get_system_metrics()
                progress.stop()

            rprint("\n[bold]System Metrics:[/bold]\n")

            table = Table(show_header=False, box=None)
            table.add_row("CPU Usage", f"{metrics.cpu_percent}%")
            table.add_row("Memory Usage", f"{metrics.memory_percent}%")
            table.add_row("Disk Usage", f"{metrics.disk_usage_percent}%")
            table.add_row("Running Processes", str(metrics.running_processes))
            table.add_row("Running Services", str(metrics.running_services))

            self.console.print(table)

            Prompt.ask("\nPress Enter to continue")

    def run(self):
        """Main application loop"""
        while self.running:
            self.clear_screen()
            self.show_header()

            choice = self.show_main_menu()

            if choice == "1":
                self.image_management_menu()
            elif choice == "2":
                self.iso_usb_menu()
            elif choice == "3":
                self.updates_menu()
            elif choice == "4":
                self.driver_menu()
            elif choice == "5":
                self.package_menu()
            elif choice == "6":
                self.optimizer_menu()
            elif choice == "0":
                self.running = False
                rprint("\n[bold cyan]Thank you for using Better11![/bold cyan]")


def main():
    """Entry point for TUI"""
    try:
        tui = Better11TUI()
        tui.run()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
