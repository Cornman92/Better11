"""Better11 - Windows 11 Enhancement Toolkit.

A comprehensive toolkit for secure application management and system
optimization on Windows 11.

Note: The frontend (CLI, GUI, TUI) has been migrated to C#.
See the csharp/Better11.CLI project for the command-line interface.
"""

__version__ = "0.3.0-dev"
__author__ = "Better11 Development Team"
__license__ = "MIT"

from .config import Config, load_config
from .interfaces import Version

__all__ = [
    "__version__",
    "__author__",
    "__license__",
    "Config",
    "load_config",
    "Version",
]
