"""Utilities for safely customizing Windows 11 systems."""
from __future__ import annotations

import logging
from logging import Logger


_DEFAULT_LOG_LEVEL = logging.INFO


def configure_logging(level: int = _DEFAULT_LOG_LEVEL) -> None:
    """Configure global logging for the package.

    The configuration is intentionally minimal: it logs to stdout with timestamps,
    module names, and message levels. Calling this function multiple times is
    idempotent; once handlers exist on the root logger, it leaves them intact.
    """
    if logging.getLogger().handlers:
        return

    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


def get_logger(name: str) -> Logger:
    """Return a configured logger instance."""
    configure_logging()
    return logging.getLogger(name)


__all__ = ["configure_logging", "get_logger"]
