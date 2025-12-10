from __future__ import annotations

import argparse
import sys
from pathlib import Path

from better11.apps.download import DownloadError
from better11.apps.manager import AppManager, DependencyError
from better11.apps.verification import VerificationError

# Import system_tools (optional - for startup manager)
try:
    from system_tools.startup import StartupManager, list_startup_items
    STARTUP_AVAILABLE = True
except ImportError:
    STARTUP_AVAILABLE = False


def build_manager(catalog_path: Path) -> AppManager:
    return AppManager(catalog_path)


def list_apps(manager: AppManager) -> int:
    for app in manager.list_available():
        print(f"{app.app_id}: {app.name} v{app.version} ({app.installer_type.value})")
    return 0


def download_app(manager: AppManager, app_id: str) -> int:
    try:
        destination = manager.download(app_id)
    except DownloadError as exc:
        print(f"Download failed: {exc}", file=sys.stderr)
        return 1
    print(f"Downloaded to {destination}")
    return 0


def install_app(manager: AppManager, app_id: str) -> int:
    try:
        status, result = manager.install(app_id)
    except (DownloadError, VerificationError, DependencyError) as exc:
        print(f"Installation failed: {exc}", file=sys.stderr)
        return 1
    print(f"Installed {status.app_id} v{status.version}: {' '.join(result.command) if result.command else 'already installed'}")
    return 0


def uninstall_app(manager: AppManager, app_id: str) -> int:
    try:
        result = manager.uninstall(app_id)
    except DependencyError as exc:
        print(f"Uninstall failed: {exc}", file=sys.stderr)
        return 1
    print(f"Uninstalled via: {' '.join(result.command)}")
    return 0


def show_status(manager: AppManager, app_id: str | None) -> int:
    statuses = manager.summarized_status(app_id)
    if not statuses:
        print("No status recorded")
        return 0
    for line in statuses:
        print(line)
    return 0


# Startup management commands
def list_startup(args: argparse.Namespace) -> int:
    """List all startup items."""
    if not STARTUP_AVAILABLE:
        print("Startup management not available", file=sys.stderr)
        return 1
    
    try:
        items = list_startup_items()
        
        if not items:
            print("No startup items found")
            return 0
        
        # Filter by location if specified
        if hasattr(args, 'location') and args.location:
            location_filter = args.location.upper()
            items = [item for item in items 
                    if location_filter in item.location.value.upper()]
        
        # Print results
        print(f"Found {len(items)} startup items:\n")
        for item in items:
            status = "✓ Enabled " if item.enabled else "✗ Disabled"
            impact = f"[{item.impact.value}]" if item.impact.value != "unknown" else ""
            print(f"{status:12} {item.name:40} {item.location.value:20} {impact}")
        
        return 0
    except Exception as exc:
        print(f"Failed to list startup items: {exc}", file=sys.stderr)
        return 1


def startup_info(args: argparse.Namespace) -> int:
    """Show startup information and recommendations."""
    if not STARTUP_AVAILABLE:
        print("Startup management not available", file=sys.stderr)
        return 1
    
    try:
        manager = StartupManager()
        items = manager.list_startup_items()
        
        enabled_count = sum(1 for item in items if item.enabled)
        boot_time = manager.get_boot_time_estimate()
        recommendations = manager.get_recommendations()
        
        print("=== Startup Information ===\n")
        print(f"Total startup items:    {len(items)}")
        print(f"Enabled items:          {enabled_count}")
        print(f"Disabled items:         {len(items) - enabled_count}")
        print(f"Estimated boot impact:  {boot_time:.1f} seconds")
        
        if recommendations:
            print("\n=== Recommendations ===\n")
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec}")
        else:
            print("\n✓ No optimization recommendations at this time.")
        
        return 0
    except Exception as exc:
        print(f"Failed to get startup info: {exc}", file=sys.stderr)
        return 1


def startup_disable(args: argparse.Namespace) -> int:
    """Disable a startup item."""
    if not STARTUP_AVAILABLE:
        print("Startup management not available", file=sys.stderr)
        return 1
    
    try:
        manager = StartupManager()
        items = manager.list_startup_items()
        
        # Find the item by name
        item = next((i for i in items if i.name == args.name), None)
        
        if not item:
            print(f"Startup item not found: {args.name}", file=sys.stderr)
            print(f"\nAvailable items:")
            for i in items:
                print(f"  - {i.name}")
            return 1
        
        if not item.enabled:
            print(f"Item '{item.name}' is already disabled")
            return 0
        
        # Confirm if not forced
        if not args.force:
            response = input(f"Disable '{item.name}'? [y/N]: ")
            if response.lower() not in ['y', 'yes']:
                print("Cancelled")
                return 0
        
        # Disable the item
        success = manager.disable_startup_item(item)
        
        if success:
            print(f"✓ Disabled: {item.name}")
            return 0
        else:
            print(f"✗ Failed to disable: {item.name}", file=sys.stderr)
            return 1
            
    except Exception as exc:
        print(f"Failed to disable startup item: {exc}", file=sys.stderr)
        return 1


def startup_enable(args: argparse.Namespace) -> int:
    """Enable a startup item."""
    if not STARTUP_AVAILABLE:
        print("Startup management not available", file=sys.stderr)
        return 1
    
    try:
        manager = StartupManager()
        items = manager.list_startup_items()
        
        # Find the item by name
        item = next((i for i in items if i.name == args.name), None)
        
        if not item:
            print(f"Startup item not found: {args.name}", file=sys.stderr)
            return 1
        
        if item.enabled:
            print(f"Item '{item.name}' is already enabled")
            return 0
        
        # Enable the item
        success = manager.enable_startup_item(item)
        
        if success:
            print(f"✓ Enabled: {item.name}")
            return 0
        else:
            print(f"✗ Failed to enable: {item.name}", file=sys.stderr)
            print("Note: Some items may require manual restoration")
            return 1
            
    except Exception as exc:
        print(f"Failed to enable startup item: {exc}", file=sys.stderr)
        return 1


def startup_remove(args: argparse.Namespace) -> int:
    """Permanently remove a startup item."""
    if not STARTUP_AVAILABLE:
        print("Startup management not available", file=sys.stderr)
        return 1
    
    try:
        manager = StartupManager()
        items = manager.list_startup_items()
        
        # Find the item by name
        item = next((i for i in items if i.name == args.name), None)
        
        if not item:
            print(f"Startup item not found: {args.name}", file=sys.stderr)
            return 1
        
        # Confirm if not forced
        if not args.force:
            print(f"WARNING: This will permanently remove '{item.name}'")
            print("Use 'disable' instead if you want to restore it later.")
            response = input(f"Permanently remove '{item.name}'? [y/N]: ")
            if response.lower() not in ['y', 'yes']:
                print("Cancelled")
                return 0
        
        # Remove the item
        success = manager.remove_startup_item(item)
        
        if success:
            print(f"✓ Permanently removed: {item.name}")
            return 0
        else:
            print(f"✗ Failed to remove: {item.name}", file=sys.stderr)
            return 1
            
    except Exception as exc:
        print(f"Failed to remove startup item: {exc}", file=sys.stderr)
        return 1


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Better11 application manager")
    parser.add_argument(
        "--catalog",
        default=Path(__file__).parent / "apps" / "catalog.json",
        type=Path,
        help="Path to the app catalog JSON",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="List available applications")

    download_parser = subparsers.add_parser("download", help="Download an application")
    download_parser.add_argument("app_id")

    install_parser = subparsers.add_parser("install", help="Download, verify, and install an application")
    install_parser.add_argument("app_id")

    uninstall_parser = subparsers.add_parser("uninstall", help="Uninstall an installed application")
    uninstall_parser.add_argument("app_id")

    status_parser = subparsers.add_parser("status", help="Show installation status")
    status_parser.add_argument("app_id", nargs="?")
    
    # Startup management commands (v0.3.0)
    if STARTUP_AVAILABLE:
        startup_parser = subparsers.add_parser("startup", help="Manage startup programs")
        startup_subparsers = startup_parser.add_subparsers(dest="startup_command", required=True)
        
        # List command
        list_startup_parser = startup_subparsers.add_parser("list", help="List startup items")
        list_startup_parser.add_argument(
            "--location",
            help="Filter by location (registry, folder, all)",
            choices=["registry", "folder", "all"],
            default=None
        )
        
        # Info command
        startup_subparsers.add_parser("info", help="Show startup information and recommendations")
        
        # Disable command
        disable_parser = startup_subparsers.add_parser("disable", help="Disable a startup item")
        disable_parser.add_argument("name", help="Name of the startup item to disable")
        disable_parser.add_argument("--force", action="store_true", help="Skip confirmation")
        
        # Enable command
        enable_parser = startup_subparsers.add_parser("enable", help="Enable a startup item")
        enable_parser.add_argument("name", help="Name of the startup item to enable")
        
        # Remove command
        remove_parser = startup_subparsers.add_parser("remove", help="Permanently remove a startup item")
        remove_parser.add_argument("name", help="Name of the startup item to remove")
        remove_parser.add_argument("--force", action="store_true", help="Skip confirmation")

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    
    # Handle startup commands (don't need app manager)
    if args.command == "startup":
        if args.startup_command == "list":
            return list_startup(args)
        if args.startup_command == "info":
            return startup_info(args)
        if args.startup_command == "disable":
            return startup_disable(args)
        if args.startup_command == "enable":
            return startup_enable(args)
        if args.startup_command == "remove":
            return startup_remove(args)
        return 1
    
    # Handle app management commands
    manager = build_manager(args.catalog)

    if args.command == "list":
        return list_apps(manager)
    if args.command == "download":
        return download_app(manager, args.app_id)
    if args.command == "install":
        return install_app(manager, args.app_id)
    if args.command == "uninstall":
        return uninstall_app(manager, args.app_id)
    if args.command == "status":
        return show_status(manager, getattr(args, "app_id", None))

    return 1


if __name__ == "__main__":
    sys.exit(main())
