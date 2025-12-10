"""CLI entrypoints for Better11 utilities."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

from .unattend import UnattendBuilder


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Better11 deployment helpers")
    subparsers = parser.add_subparsers(dest="command", required=True)

    deploy_parser = subparsers.add_parser("deploy", help="Deployment related commands")
    deploy_sub = deploy_parser.add_subparsers(dest="deploy_command", required=True)

    unattend_parser = deploy_sub.add_parser("unattend", help="Generate an unattend XML answer file")
    unattend_parser.add_argument("output", type=Path, help="Path to write unattend.xml")
    unattend_parser.add_argument("--language", default="en-US", help="UI and system language (e.g. en-US)")
    unattend_parser.add_argument("--keyboard", default=None, help="Keyboard layout (defaults to language)")
    unattend_parser.add_argument("--timezone", default="UTC", help="Windows timezone ID")
    unattend_parser.add_argument("--product-key", dest="product_key", help="Product key to inject")
    unattend_parser.add_argument("--computer-name", dest="computer_name", default="Better11", help="Computer name")
    unattend_parser.add_argument("--admin-user", dest="admin_user", default="Administrator", help="Administrator account name")
    unattend_parser.add_argument("--admin-password", dest="admin_password", default=None, help="Administrator password")
    unattend_parser.add_argument("--autologon-count", dest="autologon_count", type=int, default=1, help="Number of automatic logons to perform")
    unattend_parser.add_argument("--network-location", dest="network_location", choices=["Home", "Work", "Other"], default="Work", help="Windows network location profile")
    unattend_parser.add_argument("--hide-eula", dest="hide_eula", action="store_true", help="Hide the EULA page during OOBE")
    unattend_parser.add_argument("--protect-pc", dest="protect_pc", choices=["1", "2", "3"], default="3", help="ProtectYourPC setting (1=auto updates, 3=off)")
    unattend_parser.add_argument(
        "--first-logon-command",
        dest="first_logon_commands",
        action="append",
        default=[],
        help="Command to run at first logon (can be repeated)",
    )
    unattend_parser.add_argument(
        "--setup-command",
        dest="setup_commands",
        action="append",
        default=[],
        help="Run-synchronous command during specialize (can be repeated)",
    )
    unattend_parser.add_argument(
        "--user",
        dest="users",
        action="append",
        default=[],
        help="Additional local user in the form name[:password][:group1,group2]",
    )

    return parser


def handle_unattend(args: argparse.Namespace) -> int:
    builder = UnattendBuilder(
        product_key=args.product_key,
        computer_name=args.computer_name,
        administrator=args.admin_user,
        administrator_password=args.admin_password,
        autologon_count=args.autologon_count,
    ).with_locale(args.language, keyboard=args.keyboard, timezone=args.timezone)
    builder.with_oobe_options(
        hide_eula=args.hide_eula,
        network_location=args.network_location,
        protect_your_pc=args.protect_pc,
    )

    for cmd in args.first_logon_commands:
        builder.add_first_logon_command(cmd)

    for cmd in args.setup_commands:
        builder.add_post_setup_command(cmd)

    for user_spec in args.users:
        username, password, groups = _parse_user_spec(user_spec)
        builder.add_user(username, password=password, groups=groups)

    try:
        builder.export(args.output)
    except ValueError as exc:
        print(f"Unable to build unattend.xml: {exc}", file=sys.stderr)
        return 1

    print(f"unattend.xml written to {args.output}")
    return 0


def _parse_user_spec(spec: str) -> tuple[str, Optional[str], list[str]]:
    """Parse a CLI user specification of the form name[:password][:group1,group2]."""

    parts = spec.split(":")
    username = parts[0]
    password = parts[1] if len(parts) > 1 and parts[1] else None
    groups: list[str] = []
    if len(parts) > 2 and parts[2]:
        groups = [g for g in parts[2].split(",") if g]
    if not groups:
        groups = ["Users"]
    return username, password, groups


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "deploy" and args.deploy_command == "unattend":
        return handle_unattend(args)

    parser.error("Unknown command")
    return 1


if __name__ == "__main__":
    sys.exit(main())
