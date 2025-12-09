"""Tests for configuration management."""
import tempfile
from pathlib import Path

import pytest

from better11.config import (
    Config,
    Better11Config,
    ApplicationsConfig,
    SystemToolsConfig,
    GUIConfig,
    LoggingConfig,
    load_config,
)


class TestConfig:
    """Test configuration loading and saving."""
    
    def test_default_config_creation(self):
        """Test creating config with default values."""
        config = Config()
        assert config.better11.version == "0.3.0"
        assert config.better11.auto_update is True
        assert config.applications.verify_signatures is True
        assert config.system_tools.always_create_restore_point is True
        assert config.gui.theme == "system"
        assert config.logging.level == "INFO"
    
    def test_custom_config_creation(self):
        """Test creating config with custom values."""
        config = Config(
            better11=Better11Config(auto_update=False),
            applications=ApplicationsConfig(require_code_signing=True)
        )
        assert config.better11.auto_update is False
        assert config.applications.require_code_signing is True
    
    def test_config_validation_valid(self):
        """Test config validation with valid values."""
        config = Config()
        assert config.validate() is True
    
    def test_config_validation_invalid_safety_level(self):
        """Test config validation with invalid safety level."""
        config = Config(
            system_tools=SystemToolsConfig(safety_level="invalid")
        )
        with pytest.raises(ValueError, match="Invalid safety_level"):
            config.validate()
    
    def test_config_validation_invalid_theme(self):
        """Test config validation with invalid theme."""
        config = Config(gui=GUIConfig(theme="invalid"))
        with pytest.raises(ValueError, match="Invalid theme"):
            config.validate()
    
    def test_config_validation_invalid_log_level(self):
        """Test config validation with invalid log level."""
        config = Config(logging=LoggingConfig(level="INVALID"))
        with pytest.raises(ValueError, match="Invalid log level"):
            config.validate()
    
    def test_save_and_load_toml(self):
        """Test saving and loading TOML configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "config.toml"
            
            # Create and save config
            original = Config(
                better11=Better11Config(auto_update=False),
                applications=ApplicationsConfig(verify_signatures=False)
            )
            original.save(path)
            
            # Load config
            loaded = Config.load(path)
            assert loaded.better11.auto_update is False
            assert loaded.applications.verify_signatures is False
    
    def test_load_nonexistent_file_returns_defaults(self):
        """Test loading nonexistent file returns default config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "nonexistent.toml"
            config = Config.load(path)
            assert config.better11.version == "0.3.0"
    
    def test_get_default_path(self):
        """Test getting default configuration path."""
        path = Config.get_default_path()
        assert path == Path.home() / ".better11" / "config.toml"
    
    def test_to_dict(self):
        """Test converting config to dictionary."""
        config = Config()
        config_dict = config.to_dict()
        
        assert 'better11' in config_dict
        assert 'applications' in config_dict
        assert 'system_tools' in config_dict
        assert 'gui' in config_dict
        assert 'logging' in config_dict
        assert config_dict['better11']['version'] == "0.3.0"
    
    def test_load_config_convenience_function(self):
        """Test load_config convenience function."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "config.toml"
            Config().save(path)
            config = load_config(path)
            assert isinstance(config, Config)


# TODO: Add tests for:
# - YAML configuration support
# - Environment variable overrides
# - System-wide configuration
# - Configuration migration
# - Invalid TOML/YAML handling
