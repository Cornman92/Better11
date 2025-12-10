from __future__ import annotations

import argparse
import sys
from pathlib import Path

from better11 import __version__
from better11.apps.download import DownloadError
from better11.apps.manager import AppManager, DependencyError
from better11.apps.verification import VerificationError


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


def list_startup_items() -> int:
    """List all startup programs."""
    try:
        from system_tools.startup import StartupManager
        
        manager = StartupManager()
        items = manager.list_startup_items()
        
        if not items:
            print("No startup items found.")
            return 0
        
        print(f"\nFound {len(items)} startup items:\n")
        
        # Group by location
        from collections import defaultdict
        by_location = defaultdict(list)
        for item in items:
            by_location[item.location].append(item)
        
        for location, location_items in sorted(by_location.items()):
            print(f"📍 {location.value.upper()}:")
            for item in location_items:
                status = "✅" if item.enabled else "❌"
                print(f"  {status} {item.name}")
                print(f"     Command: {item.command}")
            print()
        
        return 0
    except Exception as exc:
        print(f"Error listing startup items: {exc}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


def privacy_status() -> int:
    """Show current privacy settings."""
    try:
        from system_tools.privacy import PrivacyManager
        
        manager = PrivacyManager()
        level = manager.get_telemetry_level()
        
        print(f"\n🔒 Privacy Status:\n")
        print(f"Telemetry Level: {level.name} (Value: {level.value})")
        
        if level == manager.MAXIMUM_PRIVACY.telemetry_level:
            print("  Status: ✅ Maximum privacy")
        elif level == manager.BALANCED.telemetry_level:
            print("  Status: ⚖️  Balanced")
        else:
            print("  Status: ⚠️  Default Windows settings")
        
        print(f"\nAvailable levels:")
        print(f"  • security (0) - Security updates only (Enterprise)")
        print(f"  • basic (1)    - Basic telemetry")
        print(f"  • enhanced (2) - Enhanced telemetry")
        print(f"  • full (3)     - Full telemetry (default)")
        
        return 0
    except Exception as exc:
        print(f"Error getting privacy status: {exc}", file=sys.stderr)
        return 1


def set_telemetry_level(level_str: str) -> int:
    """Set telemetry level."""
    try:
        from system_tools.privacy import PrivacyManager, TelemetryLevel
        
        # Map string to enum
        level_map = {
            "security": TelemetryLevel.SECURITY,
            "basic": TelemetryLevel.BASIC,
            "enhanced": TelemetryLevel.ENHANCED,
            "full": TelemetryLevel.FULL,
        }
        
        level = level_map[level_str]
        
        print(f"Setting telemetry level to {level.name}...")
        manager = PrivacyManager()
        success = manager.set_telemetry_level(level)
        
        if success:
            print(f"✅ Telemetry level set to {level.name}")
            return 0
        else:
            print(f"❌ Failed to set telemetry level")
            print(f"⚠️  This operation requires administrator rights on Windows")
            return 1
    
    except Exception as exc:
        print(f"Error setting telemetry: {exc}", file=sys.stderr)
        return 1


def disable_advertising_id() -> int:
    """Disable advertising ID."""
    try:
        from system_tools.privacy import PrivacyManager
        
        print("Disabling advertising ID...")
        manager = PrivacyManager()
        success = manager.disable_advertising_id()
        
        if success:
            print("✅ Advertising ID disabled")
            return 0
        else:
            print("❌ Failed to disable advertising ID")
            return 1
    
    except Exception as exc:
        print(f"Error disabling advertising ID: {exc}", file=sys.stderr)
        return 1


def pause_windows_updates(days: int) -> int:
    """Pause Windows updates."""
    try:
        from system_tools.updates import WindowsUpdateManager
        
        print(f"Pausing Windows updates for {days} days...")
        manager = WindowsUpdateManager()
        success = manager.pause_updates(days)
        
        if success:
            print(f"✅ Windows updates paused for {days} days")
            print(f"⏸️  Updates will resume automatically after this period")
            return 0
        else:
            print(f"❌ Failed to pause updates")
            print(f"⚠️  This operation requires administrator rights on Windows")
            return 1
    
    except ValueError as exc:
        print(f"❌ Invalid input: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Error pausing updates: {exc}", file=sys.stderr)
        return 1


def resume_windows_updates() -> int:
    """Resume Windows updates."""
    try:
        from system_tools.updates import WindowsUpdateManager
        
        print("Resuming Windows updates...")
        manager = WindowsUpdateManager()
        success = manager.resume_updates()
        
        if success:
            print("✅ Windows updates resumed")
            print("🔄 Updates will check and install normally")
            return 0
        else:
            print("❌ Failed to resume updates")
            return 1
    
    except Exception as exc:
        print(f"Error resuming updates: {exc}", file=sys.stderr)
        return 1


def set_active_hours(start: int, end: int) -> int:
    """Set Windows Update active hours."""
    try:
        from system_tools.updates import WindowsUpdateManager
        
        print(f"Setting active hours to {start}:00 - {end}:00...")
        manager = WindowsUpdateManager()
        success = manager.set_active_hours(start, end)
        
        if success:
            print(f"✅ Active hours set to {start}:00 - {end}:00")
            print(f"⏰ Windows will avoid restarting during these hours")
            return 0
        else:
            print(f"❌ Failed to set active hours")
            print(f"⚠️  This operation requires administrator rights")
            return 1
    
    except ValueError as exc:
        print(f"❌ Invalid input: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Error setting active hours: {exc}", file=sys.stderr)
        return 1


def disable_startup_program(name: str, location_str: str) -> int:
    """Disable a startup program."""
    try:
        from system_tools.startup import StartupManager, StartupLocation
        
        # First, list items to find the one to disable
        manager = StartupManager()
        items = manager.list_startup_items()
        
        # Find matching item
        matching = [item for item in items if item.name.lower() == name.lower()]
        
        if not matching:
            print(f"❌ Startup program '{name}' not found")
            print(f"\nUse 'startup list' to see available programs")
            return 1
        
        # If multiple matches, show them
        if len(matching) > 1:
            print(f"Found {len(matching)} programs named '{name}':")
            for i, item in enumerate(matching, 1):
                print(f"  {i}. {item.name} in {item.location.value}")
            
            # For now, disable the first one
            item = matching[0]
            print(f"\nDisabling first match: {item.name} from {item.location.value}")
        else:
            item = matching[0]
        
        # Disable it
        print(f"Disabling '{item.name}' from {item.location.value}...")
        success = manager.disable_startup_item(item)
        
        if success:
            print(f"✅ Disabled: {item.name}")
            print(f"⚠️  Changes take effect after restart")
            return 0
        else:
            print(f"❌ Failed to disable startup program")
            print(f"⚠️  This operation may require administrator rights")
            return 1
    
    except Exception as exc:
        print(f"Error disabling startup program: {exc}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Better11 - Windows 11 Enhancement Toolkit")
    parser.add_argument(
        "--catalog",
        default=Path(__file__).parent / "apps" / "catalog.json",
        type=Path,
        help="Path to the app catalog JSON",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version information",
    )

    subparsers = parser.add_subparsers(dest="command", required=False)

    subparsers.add_parser("list", help="List available applications")

    download_parser = subparsers.add_parser("download", help="Download an application")
    download_parser.add_argument("app_id")

    install_parser = subparsers.add_parser("install", help="Download, verify, and install an application")
    install_parser.add_argument("app_id")

    uninstall_parser = subparsers.add_parser("uninstall", help="Uninstall an installed application")
    uninstall_parser.add_argument("app_id")

    status_parser = subparsers.add_parser("status", help="Show installation status")
    status_parser.add_argument("app_id", nargs="?")
    
    # Startup management commands
    startup_parser = subparsers.add_parser("startup", help="Manage startup programs")
    startup_subparsers = startup_parser.add_subparsers(dest="startup_command")
    startup_subparsers.add_parser("list", help="List all startup programs")
    
    disable_parser = startup_subparsers.add_parser("disable", help="Disable a startup program")
    disable_parser.add_argument("name", help="Name of startup program to disable")
    disable_parser.add_argument("--location", help="Location (hklm_run, hkcu_run, etc.)", default="hkcu_run")
    
    # Privacy management commands
    privacy_parser = subparsers.add_parser("privacy", help="Manage privacy and telemetry")
    privacy_subparsers = privacy_parser.add_subparsers(dest="privacy_command")
    privacy_subparsers.add_parser("status", help="Show current privacy settings")
    
    telemetry_parser = privacy_subparsers.add_parser("set-telemetry", help="Set telemetry level")
    telemetry_parser.add_argument("level", choices=["security", "basic", "enhanced", "full"])
    
    privacy_subparsers.add_parser("disable-ads", help="Disable advertising ID")
    
    # Windows Update management commands
    updates_parser = subparsers.add_parser("updates", help="Manage Windows Updates")
    updates_subparsers = updates_parser.add_subparsers(dest="updates_command")
    
    pause_parser = updates_subparsers.add_parser("pause", help="Pause Windows updates")
    pause_parser.add_argument("--days", type=int, default=7, help="Number of days to pause (default: 7, max: 35)")
    
    updates_subparsers.add_parser("resume", help="Resume Windows updates")
    
    active_hours_parser = updates_subparsers.add_parser("set-active-hours", help="Set active hours")
    active_hours_parser.add_argument("start", type=int, help="Start hour (0-23)")
    active_hours_parser.add_argument("end", type=int, help="End hour (0-23)")

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    
    # Handle version flag
    if args.version:
        print(f"Better11 version {__version__}")
        return 0
    
    # Handle startup commands (don't need catalog)
    if args.command == "startup":
        if args.startup_command == "list":
            return list_startup_items()
        elif args.startup_command == "disable":
            return disable_startup_program(args.name, args.location)
        else:
            print("Use: better11-cli startup [list|disable]")
            return 1
    
    # Handle privacy commands (don't need catalog)
    if args.command == "privacy":
        if args.privacy_command == "status":
            return privacy_status()
        elif args.privacy_command == "set-telemetry":
            return set_telemetry_level(args.level)
        elif args.privacy_command == "disable-ads":
            return disable_advertising_id()
        else:
            print("Use: better11-cli privacy [status|set-telemetry|disable-ads]")
            return 1
    
    # Handle Windows Update commands (don't need catalog)
    if args.command == "updates":
        if args.updates_command == "pause":
            return pause_windows_updates(args.days)
        elif args.updates_command == "resume":
            return resume_windows_updates()
        elif args.updates_command == "set-active-hours":
            return set_active_hours(args.start, args.end)
        else:
            print("Use: better11-cli updates [pause|resume|set-active-hours]")
            return 1
    
    # Handle app management commands (need catalog)
    if not args.command:
        print("Better11 - Windows 11 Enhancement Toolkit")
        print(f"Version: {__version__}")
        print("\nUse --help for available commands")
        return 0
    
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
