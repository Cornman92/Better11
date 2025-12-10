"""Command line interface for Better11 deployment workflows."""

from __future__ import annotations

import sys
from typing import Optional

import click

from .deployment import WindowsDeploymentManager
from .windows_ops import UnsupportedPlatformError, is_windows


@click.group()
def cli() -> None:
    """Better11 command line utilities."""


@cli.group()
def deploy() -> None:
    """Deployment workflows for capturing and applying images."""


def _get_manager() -> Optional[WindowsDeploymentManager]:
    if not is_windows():
        click.echo("Deployment commands are only available on Windows hosts.")
        return None
    try:
        return WindowsDeploymentManager()
    except UnsupportedPlatformError as exc:
        click.echo(str(exc))
        return None


def _exit_if_no_manager(manager: Optional[WindowsDeploymentManager]) -> None:
    if manager is None:
        sys.exit(0)


@deploy.command()
@click.option("--volume", "volume_path", required=True, help="Volume or directory to capture.")
@click.option("--image", "image_path", required=True, help="Path to the destination WIM/ESD file.")
@click.option("--name", default="CapturedImage", show_default=True, help="Image name stored in the archive.")
@click.option("--description", default=None, help="Optional description for the image.")
@click.option("--format", "image_format", type=click.Choice(["wim", "esd"], case_sensitive=False), default="wim", show_default=True)
@click.option("--compression", default="max", show_default=True, help="Compression level to pass to DISM for WIM captures.")
def capture(
    volume_path: str,
    image_path: str,
    name: str,
    description: str | None,
    image_format: str,
    compression: str,
) -> None:
    """Capture a volume into a WIM or ESD image."""

    manager = _get_manager()
    _exit_if_no_manager(manager)
    try:
        manager.capture_volume_to_image(
            volume_path,
            image_path,
            name=name,
            description=description,
            image_format=image_format,
            compression=compression,
        )
        click.echo("Capture complete.")
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(str(exc)) from exc


@deploy.command()
@click.option("--image", "image_path", required=True, help="Path to the WIM/ESD image to apply.")
@click.option("--index", default=1, show_default=True, help="Image index to apply from the archive.")
@click.option("--target", "target_dir", required=True, help="Target directory or volume for the applied image.")
def apply(image_path: str, index: int, target_dir: str) -> None:
    """Apply an image to a target directory."""

    manager = _get_manager()
    _exit_if_no_manager(manager)
    try:
        manager.apply_image(image_path, target_dir, index=index)
        click.echo("Apply complete.")
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(str(exc)) from exc


@deploy.command()
@click.option("--image", "image_path", required=True, help="Path to the WIM/ESD image to service.")
@click.option("--mount", "mount_dir", required=True, help="Mount directory for servicing operations.")
@click.option("--index", default=1, show_default=True, help="Image index to service.")
@click.option("--driver", "drivers", multiple=True, help="Driver directories or INF files to inject.")
@click.option("--feature", "features", multiple=True, help="Windows feature names to enable.")
@click.option("--update", "updates", multiple=True, help="Package paths to add via DISM.")
def service(
    image_path: str,
    mount_dir: str,
    index: int,
    drivers: tuple[str, ...],
    features: tuple[str, ...],
    updates: tuple[str, ...],
) -> None:
    """Mount an image, apply servicing steps, and commit the changes."""

    manager = _get_manager()
    _exit_if_no_manager(manager)
    try:
        manager.service_image(
            image_path,
            mount_dir,
            index=index,
            drivers=list(drivers),
            features=list(features),
            updates=list(updates),
        )
        click.echo("Servicing complete.")
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(str(exc)) from exc


if __name__ == "__main__":
    cli()
