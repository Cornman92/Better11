"""Configuration management for Better11.

This module handles loading, saving, and validating Better11 configuration
from TOML or YAML files. Configuration can be loaded from:
1. System-wide location (if available)
2. User directory (~/.better11/config.toml)
3. Environment variables (for overrides)
4. Programmatic defaults
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional, Any, Dict

import platform

from better11.interfaces import Version

try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:
        tomllib = None  # type: ignore

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore


@dataclass
class Better11Config:
    """Main Better11 application configuration."""
    
    version: str = "0.3.0"
    auto_update: bool = True
    check_updates_on_start: bool = True
    telemetry_enabled: bool = False


@dataclass
class ApplicationsConfig:
    """Application management configuration."""
    
    catalog_url: str = "default"
    auto_install_dependencies: bool = True
    verify_signatures: bool = True
    require_code_signing: bool = False  # Warn but don't block if False
    check_revocation: bool = False  # CRL/OCSP checking (slow)


@dataclass
class SystemToolsConfig:
    """System tools configuration."""

    always_create_restore_point: bool = True
    confirm_destructive_actions: bool = True
    backup_registry: bool = True
    safety_level: str = "high"  # low, medium, high, paranoid


@dataclass
class GaYmRPCConfig:
    """GaYmR-PC integration configuration."""

    enabled: bool = False
    source: str = "service"  # service or library
    service_name: str = "GaYmR-PC"
    library_path: str = "C:/Program Files/GaYmR-PC/gaymr_pc.dll"
    minimum_version: str = "1.0.0"
    license_name: str = "External vendor license"
    license_url: str = "https://vendor.example.com/gaymr-pc/license"


@dataclass
class GUIConfig:
    """GUI application configuration."""
    
    theme: str = "system"  # system, light, dark
    show_advanced_options: bool = False
    remember_window_size: bool = True
    default_tab: str = "applications"


@dataclass
class LoggingConfig:
    """Logging configuration."""
    
    level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    file_enabled: bool = True
    console_enabled: bool = True
    max_log_size_mb: int = 10
    backup_count: int = 5


@dataclass
class Config:
    """Complete Better11 configuration.
    
    This class manages all configuration aspects of Better11, including:
    - Application settings
    - System tools behavior
    - GUI preferences
    - Logging configuration
    
    Configuration is loaded from files in the following order (later overrides earlier):
    1. Built-in defaults
    2. System-wide config (if present)
    3. User config file
    4. Environment variables
    
    Examples
    --------
    Load configuration from default location:
    
    >>> config = Config.load()
    
    Load from specific file:
    
    >>> config = Config.load(Path("/path/to/config.toml"))
    
    Create with custom settings:
    
    >>> config = Config(
    ...     better11=Better11Config(auto_update=False),
    ...     applications=ApplicationsConfig(verify_signatures=True)
    ... )
    >>> config.save()
    """
    
    better11: Better11Config = field(default_factory=Better11Config)
    applications: ApplicationsConfig = field(default_factory=ApplicationsConfig)
    system_tools: SystemToolsConfig = field(default_factory=SystemToolsConfig)
    gaymr_pc: GaYmRPCConfig = field(default_factory=GaYmRPCConfig)
    gui: GUIConfig = field(default_factory=GUIConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    @classmethod
    def load(cls, path: Optional[Path] = None) -> "Config":
        """Load configuration from file with defaults.
        
        Parameters
        ----------
        path : Path, optional
            Path to configuration file. If None, uses default location.
        
        Returns
        -------
        Config
            Loaded configuration with defaults for missing values
        
        Raises
        ------
        ValueError
            If configuration file is malformed
        """
        if path is None:
            path = cls.get_default_path()
        
        # Start with defaults
        config = cls()
        
        # Load from file if it exists
        if path.exists():
            config = cls._load_from_file(path)
        
        # Apply environment variable overrides
        config = cls._apply_env_overrides(config)
        
        return config
    
    @classmethod
    def _load_from_file(cls, path: Path) -> "Config":
        """Load configuration from TOML or YAML file."""
        suffix = path.suffix.lower()
        
        try:
            with open(path, 'rb' if suffix == '.toml' else 'r') as f:
                if suffix == '.toml':
                    if tomllib is None:
                        raise ImportError("TOML support requires Python 3.11+ or tomli package")
                    data = tomllib.load(f)
                elif suffix in {'.yaml', '.yml'}:
                    if yaml is None:
                        raise ImportError("YAML support requires pyyaml package: pip install pyyaml")
                    data = yaml.safe_load(f)
                else:
                    raise ValueError(f"Unsupported configuration format: {suffix}")
            
            return cls._from_dict(data)
        
        except Exception as exc:
            raise ValueError(f"Failed to load configuration from {path}: {exc}") from exc
    
    @classmethod
    def _from_dict(cls, data: Dict[str, Any]) -> "Config":
        """Create Config from dictionary."""
        return cls(
            better11=Better11Config(**data.get('better11', {})),
            applications=ApplicationsConfig(**data.get('applications', {})),
            system_tools=SystemToolsConfig(**data.get('system_tools', {})),
            gaymr_pc=GaYmRPCConfig(**data.get('gaymr_pc', {})),
            gui=GUIConfig(**data.get('gui', {})),
            logging=LoggingConfig(**data.get('logging', {})),
        )
    
    @classmethod
    def _apply_env_overrides(cls, config: "Config") -> "Config":
        """Apply environment variable overrides.
        
        Environment variables in format: BETTER11_SECTION_KEY
        Example: BETTER11_APPLICATIONS_VERIFY_SIGNATURES=false
        """
        # Simple implementation - can be expanded
        if 'BETTER11_AUTO_UPDATE' in os.environ:
            config.better11.auto_update = os.environ['BETTER11_AUTO_UPDATE'].lower() == 'true'

        if 'BETTER11_LOG_LEVEL' in os.environ:
            config.logging.level = os.environ['BETTER11_LOG_LEVEL']

        if 'BETTER11_GAYMR_PC_ENABLED' in os.environ:
            config.gaymr_pc.enabled = os.environ['BETTER11_GAYMR_PC_ENABLED'].lower() == 'true'

        if 'BETTER11_GAYMR_PC_SOURCE' in os.environ:
            config.gaymr_pc.source = os.environ['BETTER11_GAYMR_PC_SOURCE']

        return config
    
    def save(self, path: Optional[Path] = None) -> None:
        """Save configuration to file.
        
        Parameters
        ----------
        path : Path, optional
            Path to save configuration. If None, uses default location.
        """
        if path is None:
            path = self.get_default_path()
        
        # Ensure directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to dict
        data = {
            'better11': asdict(self.better11),
            'applications': asdict(self.applications),
            'system_tools': asdict(self.system_tools),
            'gaymr_pc': asdict(self.gaymr_pc),
            'gui': asdict(self.gui),
            'logging': asdict(self.logging),
        }
        
        # Save based on file extension
        suffix = path.suffix.lower()
        
        with open(path, 'w') as f:
            if suffix == '.toml' or suffix == '':
                self._save_as_toml(f, data)
            elif suffix in {'.yaml', '.yml'}:
                if yaml is None:
                    raise ImportError("YAML support requires pyyaml package: pip install pyyaml")
                yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)
            else:
                raise ValueError(f"Unsupported configuration format: {suffix}")
    
    @staticmethod
    def _save_as_toml(file, data: dict) -> None:
        """Save data as TOML format.
        
        Note: tomllib is read-only, so we write TOML manually.
        For production, consider using tomli_w package.
        """
        for section, values in data.items():
            file.write(f"[{section}]\n")
            for key, value in values.items():
                if isinstance(value, bool):
                    file.write(f"{key} = {str(value).lower()}\n")
                elif isinstance(value, str):
                    file.write(f'{key} = "{value}"\n')
                else:
                    file.write(f"{key} = {value}\n")
            file.write("\n")
    
    @staticmethod
    def get_default_path() -> Path:
        """Get default configuration file path.
        
        Returns
        -------
        Path
            Default configuration file path (~/.better11/config.toml)
        """
        return Path.home() / ".better11" / "config.toml"
    
    @staticmethod
    def get_system_path() -> Path:
        """Get system-wide configuration file path.
        
        Returns
        -------
        Path
            System configuration file path (C:\\ProgramData\\Better11\\config.toml on Windows)
        """
        if platform.system().lower() == 'windows':
            program_data = os.environ.get('PROGRAMDATA', 'C:\\ProgramData')
            return Path(program_data) / "Better11" / "config.toml"

        return Path("/etc/better11/config.toml")
    
    def validate(self) -> bool:
        """Validate configuration values.
        
        Returns
        -------
        bool
            True if configuration is valid
        
        Raises
        ------
        ValueError
            If configuration contains invalid values
        """
        # Validate safety level
        valid_safety_levels = {'low', 'medium', 'high', 'paranoid'}
        if self.system_tools.safety_level not in valid_safety_levels:
            raise ValueError(
                f"Invalid safety_level: {self.system_tools.safety_level}. "
                f"Must be one of {valid_safety_levels}"
            )

        valid_sources = {'service', 'library'}
        if self.gaymr_pc.source not in valid_sources:
            raise ValueError(
                f"Invalid GaYmR-PC source: {self.gaymr_pc.source}. "
                f"Must be one of {valid_sources}"
            )

        # Validate GaYmR-PC version string
        Version.parse(self.gaymr_pc.minimum_version)

        # Validate theme
        valid_themes = {'system', 'light', 'dark'}
        if self.gui.theme not in valid_themes:
            raise ValueError(
                f"Invalid theme: {self.gui.theme}. Must be one of {valid_themes}"
            )
        
        # Validate log level
        valid_log_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
        if self.logging.level.upper() not in valid_log_levels:
            raise ValueError(
                f"Invalid log level: {self.logging.level}. "
                f"Must be one of {valid_log_levels}"
            )
        
        return True
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary.
        
        Returns
        -------
        dict
            Configuration as dictionary
        """
        return {
            'better11': asdict(self.better11),
            'applications': asdict(self.applications),
            'system_tools': asdict(self.system_tools),
            'gaymr_pc': asdict(self.gaymr_pc),
            'gui': asdict(self.gui),
            'logging': asdict(self.logging),
        }


def load_config(path: Optional[Path] = None) -> Config:
    """Load Better11 configuration.
    
    Convenience function for loading configuration.
    
    Parameters
    ----------
    path : Path, optional
        Path to configuration file
    
    Returns
    -------
    Config
        Loaded configuration
    """
    return Config.load(path)


__all__ = [
    "Better11Config",
    "ApplicationsConfig",
    "SystemToolsConfig",
    "GaYmRPCConfig",
    "GUIConfig",
    "LoggingConfig",
    "Config",
    "load_config",
]
