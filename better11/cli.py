from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Tuple

from better11.apps.download import DownloadError
from better11.apps.manager import AppManager, DependencyError
from better11.apps.verification import VerificationError
from better11.unattend import UnattendBuilder


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


def _parse_first_logon_commands(raw_commands: list[str]) -> list[dict[str, str | int]]:
    parsed: list[dict[str, str | int]] = []
    for index, raw in enumerate(raw_commands, start=1):
        order = index
        description: str | None = None
        text = raw.strip()
        if ":" in text:
            prefix, remainder = text.split(":", 1)
            if prefix.isdigit():
                order = int(prefix)
                text = remainder.strip()
        if "|" in text:
            description, text = (part.strip() for part in text.split("|", 1))
        parsed.append({"order": order, "command": text, "description": description or None})
    return parsed


def generate_unattend(args: argparse.Namespace) -> int:
    if args.template == "workstation":
        builder = UnattendBuilder.workstation_template(
            product_key=args.product_key,
            admin_user=args.admin_user,
            admin_password=args.admin_password,
            language=args.language,
            time_zone=args.timezone,
        )
    elif args.template == "lab":
        builder = UnattendBuilder.lab_template(
            product_key=args.product_key, language=args.language, time_zone=args.timezone
        )
    else:
        builder = UnattendBuilder(
            language=args.language,
            time_zone=args.timezone,
            computer_name=args.computer_name,
        )
        builder.set_product_key(args.product_key).set_admin_password(args.admin_password)
        builder.add_local_account(
            args.admin_user,
            password=args.admin_password,
            auto_logon=args.auto_logon,
        )

    for command in _parse_first_logon_commands(args.first_logon_command):
        builder.add_first_logon_command(
            order=command["order"],
            command=command["command"],
            description=command.get("description"),
        )

    output_path = builder.export(args.output)
    print(f"Wrote unattend file to {output_path}")
    return 0


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

    plan_parser = subparsers.add_parser("plan", help="Show the installation plan for an app")
    plan_parser.add_argument("app_id")

    deploy_parser = subparsers.add_parser("deploy", help="Deployment utilities")
    deploy_subparsers = deploy_parser.add_subparsers(dest="deploy_command", required=True)

    unattend_parser = deploy_subparsers.add_parser("unattend", help="Generate a Windows unattend file")
    unattend_parser.add_argument("--product-key", required=True, help="Product key to embed in the answer file")
    unattend_parser.add_argument("--output", required=True, type=Path, help="Path to write unattend.xml")
    unattend_parser.add_argument("--language", default="en-US", help="UI language tag (default: en-US)")
    unattend_parser.add_argument(
        "--timezone",
        default="Pacific Standard Time",
        help="Windows time zone name (e.g., 'UTC', 'Pacific Standard Time')",
    )
    unattend_parser.add_argument("--computer-name", help="Optional computer name to assign during setup")
    unattend_parser.add_argument("--admin-user", default="Administrator", help="Administrative account to create")
    unattend_parser.add_argument("--admin-password", help="Password for the administrative account")
    unattend_parser.add_argument(
        "--auto-logon",
        action="store_true",
        help="Enable automatic logon for the administrative account during setup",
    )
    unattend_parser.add_argument(
        "--first-logon-command",
        action="append",
        default=[],
        help=(
            "Add a synchronous first-logon command. Use 'order:command' to set execution order or "
            "'order:description|command' to include a description."
        ),
    )
    unattend_parser.add_argument(
        "--template",
        choices=["workstation", "lab"],
        help="Start from a predefined template and optionally layer additional commands",
    )

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
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
    if args.command == "deploy" and args.deploy_command == "unattend":
        return generate_unattend(args)

    return 1


if __name__ == "__main__":
    sys.exit(main())
