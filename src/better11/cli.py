"""Command-line helpers for Better11."""
from __future__ import annotations

import sys
import json
from typing import TextIO

from .catalog import MediaCatalog


def _print_error(message: str, stream: TextIO | None = None) -> None:
    """Print an error message to the provided stream."""

    print(message, file=stream or sys.stderr)


def handle_fetch_media(raw_payload: str) -> int:
    """Load a media catalog from a JSON payload.

    Returns an exit code. ``0`` indicates success while ``1`` represents
    a validation or parsing error. Any errors are reported to stderr without
    emitting a Python traceback so that CLI consumers get concise feedback.
    """

    try:
        MediaCatalog.load(raw_payload)
    except (json.JSONDecodeError, ValueError) as exc:
        _print_error(f"Failed to load media catalog: {exc}")
        return 1

    return 0
