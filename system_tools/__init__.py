"""Utilities for safely customizing Windows 11 systems.

This package provides comprehensive system management tools for Windows 11:

Core Modules:
- base: Base classes and interfaces for system tools
- safety: Safety utilities (restore points, backups)
- registry: Registry management
- bloatware: AppX package removal
- services: Windows service management
- performance: Performance optimization

System Management:
- updates: Windows Update management
- features: Windows optional features (DISM)
- startup: Startup program management
- privacy: Privacy and telemetry control
- drivers: Driver backup and management
- tasks: Scheduled tasks management

Customization:
- shell: Taskbar, Start menu, context menu customization
- gaming: Gaming optimization and performance tweaks

Utilities:
- disk: Disk space management
- network: Network configuration
- backup: System backup and restore
- power: Power plan management
- sysinfo: System information gathering
"""
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


# Lazy imports to avoid circular dependencies
def __getattr__(name: str):
    """Lazy loading of submodules."""
    module_map = {
        # Core modules
        "base": "system_tools.base",
        "safety": "system_tools.safety",
        "registry": "system_tools.registry",
        "bloatware": "system_tools.bloatware",
        "services": "system_tools.services",
        "performance": "system_tools.performance",
        # System management
        "updates": "system_tools.updates",
        "features": "system_tools.features",
        "startup": "system_tools.startup",
        "privacy": "system_tools.privacy",
        "drivers": "system_tools.drivers",
        "tasks": "system_tools.tasks",
        # Customization
        "shell": "system_tools.shell",
        "gaming": "system_tools.gaming",
        # Utilities
        "disk": "system_tools.disk",
        "network": "system_tools.network",
        "backup": "system_tools.backup",
        "power": "system_tools.power",
        "sysinfo": "system_tools.sysinfo",
    }
    
    if name in module_map:
        import importlib
        return importlib.import_module(module_map[name])
    
    raise AttributeError(f"module 'system_tools' has no attribute '{name}'")


__all__ = [
    # Functions
    "configure_logging",
    "get_logger",
    # Core modules
    "base",
    "safety",
    "registry",
    "bloatware",
    "services",
    "performance",
    # System management
    "updates",
    "features",
    "startup",
    "privacy",
    "drivers",
    "tasks",
    # Customization
    "shell",
    "gaming",
    # Utilities
    "disk",
    "network",
    "backup",
    "power",
    "sysinfo",
]
