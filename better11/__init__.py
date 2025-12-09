"""Better11 - Windows 11 Enhancement Toolkit.

A comprehensive toolkit for secure application management and system
optimization on Windows 11.
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
