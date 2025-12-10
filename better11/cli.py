from __future__ import annotations

import argparse
import sys
from pathlib import Path

import click

from better11.apps.download import DownloadError
from better11.apps.manager import AppManager, DependencyError
from better11.apps.verification import VerificationError
from better11.deployment import WindowsDeploymentManager
from better11.windows_ops import UnsupportedPlatformError, is_windows


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

    return parser.parse_args(argv)


def _create_deployment_manager() -> WindowsDeploymentManager:
    return WindowsDeploymentManager()


@click.group(help="Deployment workflows for Windows images.")
def deploy() -> None:
    """Manage Windows deployment tasks."""


@deploy.command("capture")
@click.argument("source_volume")
@click.argument("destination_image")
@click.option("--name", "image_name", required=True, help="Friendly name for the captured image")
@click.option("--description", help="Optional description for the image")
@click.option("--esd", "compress_to_esd", is_flag=True, help="Capture using ESD compression")
def deploy_capture(source_volume: str, destination_image: str, image_name: str, description: str | None, compress_to_esd: bool) -> None:
    """Capture a Windows volume to a WIM/ESD image."""

    if not is_windows():
        click.echo("Deployment commands are only available on Windows.", err=True)
        raise SystemExit(1)

    manager = _create_deployment_manager()
    try:
        manager.capture_image(
            source_volume,
            destination_image,
            image_name=image_name,
            description=description,
            compress_to_esd=compress_to_esd,
        )
    except UnsupportedPlatformError as exc:
        raise click.ClickException(str(exc))
    click.echo(f"Captured {source_volume} to {destination_image}")


@deploy.command("apply")
@click.argument("image_path")
@click.argument("target_partition")
@click.option("--index", default=1, show_default=True, type=int, help="Image index to apply")
@click.option("--skip-verify", is_flag=True, help="Skip DISM integrity verification")
def deploy_apply(image_path: str, target_partition: str, index: int, skip_verify: bool) -> None:
    """Apply a captured image to a target partition."""

    if not is_windows():
        click.echo("Deployment commands are only available on Windows.", err=True)
        raise SystemExit(1)

    manager = _create_deployment_manager()
    try:
        manager.apply_image(image_path, target_partition, index=index, verify=not skip_verify)
    except UnsupportedPlatformError as exc:
        raise click.ClickException(str(exc))
    click.echo(f"Applied image index {index} from {image_path} to {target_partition}")


@deploy.command("service")
@click.argument("image_path")
@click.argument("mount_dir")
@click.option("--index", default=1, show_default=True, type=int, help="Image index to mount")
@click.option("--driver", "drivers", multiple=True, help="Driver folder or INF to inject (repeatable)")
@click.option("--feature", "features", multiple=True, help="Windows feature name to enable (repeatable)")
@click.option("--update", "updates", multiple=True, help=".cab or .msu update package to add (repeatable)")
@click.option("--commit/--discard", default=True, show_default=True, help="Commit or discard servicing changes")
def deploy_service(
    image_path: str,
    mount_dir: str,
    index: int,
    drivers: tuple[str, ...],
    features: tuple[str, ...],
    updates: tuple[str, ...],
    commit: bool,
) -> None:
    """Mount and service an offline Windows image."""

    if not is_windows():
        click.echo("Deployment commands are only available on Windows.", err=True)
        raise SystemExit(1)

    manager = _create_deployment_manager()
    try:
        manager.service_image(
            image_path,
            mount_dir,
            index=index,
            drivers=list(drivers),
            features=list(features),
            updates=list(updates),
            commit=commit,
        )
    except UnsupportedPlatformError as exc:
        raise click.ClickException(str(exc))
    click.echo("Servicing completed")


def _run_deploy(argv: list[str]) -> int:
    try:
        deploy.main(args=argv, prog_name="better11 deploy", standalone_mode=False)
    except SystemExit as exc:
        return int(exc.code)
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    if argv and argv[0] == "deploy":
        return _run_deploy(argv[1:])

    args = parse_args(argv)
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
