"""
Configuration Management System

Provides centralized configuration for Better11 with support for:
- YAML and TOML config files
- Preset profiles
- User preferences
- Module-specific settings
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict, field
from enum import Enum


try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

try:
    import tomli
    TOML_AVAILABLE = True
except ImportError:
    TOML_AVAILABLE = False


class ConfigFormat(Enum):
    """Supported config file formats"""
    JSON = "json"
    YAML = "yaml"
    TOML = "toml"


@dataclass
class ImageConfig:
    """Image management configuration"""
    work_dir: str = ""
    mount_dir: str = ""
    default_index: int = 1
    auto_optimize: bool = False
    compression: str = "max"


@dataclass
class UpdateConfig:
    """Windows Update configuration"""
    auto_check: bool = True
    auto_download: bool = False
    auto_install: bool = False
    pause_days: int = 0
    include_drivers: bool = True


@dataclass
class DriverConfig:
    """Driver management configuration"""
    backup_dir: str = ""
    auto_backup: bool = True
    include_inbox: bool = False
    force_unsigned: bool = False


@dataclass
class PackageConfig:
    """Package manager configuration"""
    cache_dir: str = ""
    preferred_manager: str = "winget"
    auto_update: bool = False
    verify_signatures: bool = True


@dataclass
class OptimizerConfig:
    """System optimizer configuration"""
    default_level: str = "balanced"
    auto_backup_registry: bool = True
    create_restore_point: bool = True
    disable_telemetry: bool = False


@dataclass
class FileConfig:
    """File manager configuration"""
    buffer_size: int = 1048576  # 1MB
    use_robocopy: bool = True
    secure_delete: bool = False


@dataclass
class UIConfig:
    """User interface configuration"""
    theme: str = "default"
    verbose: bool = False
    show_progress: bool = True
    confirm_destructive: bool = True


@dataclass
class Better11Config:
    """Main configuration"""
    version: str = "0.3.0"
    image: ImageConfig = field(default_factory=ImageConfig)
    updates: UpdateConfig = field(default_factory=UpdateConfig)
    drivers: DriverConfig = field(default_factory=DriverConfig)
    packages: PackageConfig = field(default_factory=PackageConfig)
    optimizer: OptimizerConfig = field(default_factory=OptimizerConfig)
    files: FileConfig = field(default_factory=FileConfig)
    ui: UIConfig = field(default_factory=UIConfig)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Better11Config':
        """Create from dictionary"""
        config = cls()

        # Update version
        if 'version' in data:
            config.version = data['version']

        # Update each section
        if 'image' in data:
            config.image = ImageConfig(**data['image'])
        if 'updates' in data:
            config.updates = UpdateConfig(**data['updates'])
        if 'drivers' in data:
            config.drivers = DriverConfig(**data['drivers'])
        if 'packages' in data:
            config.packages = PackageConfig(**data['packages'])
        if 'optimizer' in data:
            config.optimizer = OptimizerConfig(**data['optimizer'])
        if 'files' in data:
            config.files = FileConfig(**data['files'])
        if 'ui' in data:
            config.ui = UIConfig(**data['ui'])

        return config


class ConfigManager:
    """Manage Better11 configuration"""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self.config = Better11Config()

        # Load config if it exists
        if os.path.exists(self.config_path):
            self.load()

    def _get_default_config_path(self) -> str:
        """Get default configuration file path"""
        # Try to use user's home directory
        home = Path.home()
        config_dir = home / ".better11"
        config_dir.mkdir(exist_ok=True)

        return str(config_dir / "config.json")

    def load(self, path: Optional[str] = None) -> bool:
        """Load configuration from file"""
        load_path = path or self.config_path

        if not os.path.exists(load_path):
            return False

        # Determine format from extension
        ext = Path(load_path).suffix.lower()

        try:
            if ext == ".json":
                with open(load_path, 'r') as f:
                    data = json.load(f)
            elif ext in [".yaml", ".yml"]:
                if not YAML_AVAILABLE:
                    raise ImportError("PyYAML not installed")
                with open(load_path, 'r') as f:
                    data = yaml.safe_load(f)
            elif ext == ".toml":
                if not TOML_AVAILABLE:
                    raise ImportError("tomli not installed")
                with open(load_path, 'rb') as f:
                    data = tomli.load(f)
            else:
                # Default to JSON
                with open(load_path, 'r') as f:
                    data = json.load(f)

            self.config = Better11Config.from_dict(data)
            return True

        except Exception as e:
            print(f"Error loading config: {e}")
            return False

    def save(self, path: Optional[str] = None, format: ConfigFormat = ConfigFormat.JSON) -> bool:
        """Save configuration to file"""
        save_path = path or self.config_path

        # Ensure directory exists
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)

        try:
            data = self.config.to_dict()

            if format == ConfigFormat.JSON:
                with open(save_path, 'w') as f:
                    json.dump(data, f, indent=2)
            elif format == ConfigFormat.YAML:
                if not YAML_AVAILABLE:
                    raise ImportError("PyYAML not installed")
                with open(save_path, 'w') as f:
                    yaml.dump(data, f, default_flow_style=False)
            elif format == ConfigFormat.TOML:
                # TOML writing requires tomli-w
                raise NotImplementedError("TOML writing not yet implemented")

            return True

        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.config = Better11Config()

    def get(self, section: str) -> Any:
        """Get configuration section"""
        return getattr(self.config, section, None)

    def set(self, section: str, key: str, value: Any):
        """Set configuration value"""
        section_obj = getattr(self.config, section, None)
        if section_obj:
            setattr(section_obj, key, value)

    def apply_profile(self, profile_name: str) -> bool:
        """Apply a predefined configuration profile"""
        profiles = self.get_available_profiles()

        if profile_name not in profiles:
            return False

        profile = profiles[profile_name]
        self.config = Better11Config.from_dict(profile)

        return True

    def get_available_profiles(self) -> Dict[str, Dict]:
        """Get available configuration profiles"""
        return {
            "default": {
                "version": "0.3.0",
                "optimizer": {"default_level": "balanced"},
                "ui": {"verbose": False}
            },
            "gaming": {
                "version": "0.3.0",
                "optimizer": {
                    "default_level": "gaming",
                    "disable_telemetry": True
                },
                "updates": {
                    "auto_install": False,
                    "pause_days": 7
                },
                "ui": {"verbose": True}
            },
            "productivity": {
                "version": "0.3.0",
                "optimizer": {
                    "default_level": "productivity"
                },
                "updates": {
                    "auto_check": True,
                    "auto_download": True
                },
                "ui": {"verbose": False}
            },
            "developer": {
                "version": "0.3.0",
                "optimizer": {
                    "default_level": "balanced"
                },
                "packages": {
                    "preferred_manager": "winget"
                },
                "ui": {"verbose": True}
            },
            "server": {
                "version": "0.3.0",
                "optimizer": {
                    "default_level": "aggressive",
                    "disable_telemetry": True
                },
                "updates": {
                    "auto_check": True,
                    "auto_install": False
                },
                "ui": {"verbose": True, "confirm_destructive": True}
            }
        }

    def export_current(self, path: str) -> bool:
        """Export current configuration to file"""
        return self.save(path)

    def import_config(self, path: str) -> bool:
        """Import configuration from file"""
        return self.load(path)


# Global configuration instance
_global_config: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """Get global configuration instance"""
    global _global_config

    if _global_config is None:
        _global_config = ConfigManager()

    return _global_config


def set_config(config: ConfigManager):
    """Set global configuration instance"""
    global _global_config
    _global_config = config


# Convenience functions
def load_config(path: Optional[str] = None) -> ConfigManager:
    """Load and return configuration"""
    config = ConfigManager(path)
    set_config(config)
    return config


def save_config(path: Optional[str] = None) -> bool:
    """Save current configuration"""
    config = get_config()
    return config.save(path)


def get_setting(section: str, key: str, default: Any = None) -> Any:
    """Get a configuration setting"""
    config = get_config()
    section_obj = config.get(section)

    if section_obj:
        return getattr(section_obj, key, default)

    return default


def set_setting(section: str, key: str, value: Any):
    """Set a configuration setting"""
    config = get_config()
    config.set(section, key, value)
