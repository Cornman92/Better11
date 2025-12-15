from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Tuple

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
        destination, cache_hit = manager.download(app_id)
    except DownloadError as exc:
        print(f"Download failed: {exc}", file=sys.stderr)
        return 1
    prefix = "Using cached installer at" if cache_hit else "Downloaded to"
    print(f"{prefix} {destination}")
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


def plan_installation(manager: AppManager, app_id: str) -> int:
    try:
        plan = manager.build_install_plan(app_id)
    except KeyError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if not plan.steps:
        print("No plan steps found.")
        return 0

    headers = ("ACTION", "APP ID", "VERSION", "STATUS", "NOTES")
    rows = []
    for step in plan.steps:
        status = "installed" if step.installed else "pending"
        rows.append((step.action.upper(), step.app_id, step.version, status, step.notes or ""))

    widths = [len(header) for header in headers]
    for row in rows:
        widths = [max(widths[i], len(row[i])) for i in range(len(headers))]

    def format_row(row: Tuple[str, ...]) -> str:
        return "  ".join(value.ljust(widths[i]) for i, value in enumerate(row))

    print(format_row(headers))
    print("  ".join("-" * width for width in widths))
    for row in rows:
        print(format_row(row))

    if plan.warnings:
        print("\nWarnings:")
        for warning in plan.warnings:
            print(f"- {warning}")

    blocked = any(step.action == "blocked" for step in plan.steps)
    return 1 if blocked else 0


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

    plan_parser = subparsers.add_parser("plan", help="Show the installation plan for an app")
    plan_parser.add_argument("app_id")

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
    if args.command == "plan":
        return plan_installation(manager, args.app_id)

    return 1


if __name__ == "__main__":
    sys.exit(main())
