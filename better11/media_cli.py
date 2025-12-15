"""Command-line helpers for Better11 media catalog."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TextIO

from better11.application_manager import ApplicationManager
from .media_catalog import MediaCatalog


def _print_error(message: str, stream: TextIO | None = None) -> None:
    """Print an error message to the provided stream."""

    print(message, file=stream or sys.stderr)


def handle_fetch_media(raw_payload: str) -> int:
    """Load a media catalog from a JSON payload."""

    try:
        MediaCatalog.load(raw_payload)
    except (json.JSONDecodeError, ValueError) as exc:
        _print_error(f"Failed to load media catalog: {exc}")
        return 1

    return 0


def fetch_media(
    catalog_path: Path,
    repository_root: Path,
    *,
    validate_checksums: bool = True,
    manager: ApplicationManager | None = None,
    output_stream: TextIO | None = None,
    error_stream: TextIO | None = None,
) -> int:
    """Fetch all media entries in *catalog_path* into *repository_root*."""

    manager = manager or ApplicationManager()
    try:
        catalog = manager.import_catalog(catalog_path)
    except (json.JSONDecodeError, ValueError, OSError) as exc:
        _print_error(f"Failed to load media catalog: {exc}", stream=error_stream)
        return 1

    failures: list[str] = []
    for entry in catalog.all_entries():
        try:
            destination = manager.fetch_catalog_entry(
                entry, repository_root, validate_checksum=validate_checksums
            )
            print(f"Fetched {entry.identifier} -> {destination}", file=output_stream or sys.stdout)
        except ValueError as exc:
            _print_error(
                f"Checksum verification failed for {entry.identifier}: {exc}", stream=error_stream
            )
            failures.append(entry.identifier)
        except Exception as exc:  # noqa: BLE001
            _print_error(f"Failed to fetch {entry.identifier}: {exc}", stream=error_stream)
            failures.append(entry.identifier)

    if failures:
        _print_error(
            f"{len(failures)} item(s) failed to download: {', '.join(failures)}",
            stream=error_stream,
        )
        return 1

    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Better11 deployment media helper")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="Validate a catalog payload")
    validate_parser.add_argument("catalog", type=Path, help="Path to a catalog JSON file")

    fetch_parser = subparsers.add_parser("fetch-media", help="Download media into a shared repository")
    fetch_parser.add_argument("catalog", type=Path, help="Path to a catalog JSON file")
    fetch_parser.add_argument("repository", type=Path, help="Repository root to store media")
    fetch_parser.add_argument(
        "--skip-checksums",
        action="store_true",
        help="Skip checksum verification even when checksums are provided",
    )

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])

    if args.command == "validate":
        return handle_fetch_media(args.catalog.read_text())

    if args.command == "fetch-media":
        return fetch_media(
            args.catalog,
            args.repository,
            validate_checksums=not args.skip_checksums,
        )

    return 1


if __name__ == "__main__":
    sys.exit(main())
