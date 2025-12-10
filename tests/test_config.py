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


    def test_save_and_load_yaml(self):
        """Test saving and loading YAML configuration."""
        try:
            import yaml as _yaml  # Check if yaml is available
        except ImportError:
            pytest.skip("PyYAML not installed")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "config.yaml"
            
            # Create and save config
            original = Config(
                better11=Better11Config(auto_update=False, telemetry_enabled=True),
                applications=ApplicationsConfig(verify_signatures=False)
            )
            original.save(path)
            
            # Load config
            loaded = Config.load(path)
            assert loaded.better11.auto_update is False
            assert loaded.better11.telemetry_enabled is True
            assert loaded.applications.verify_signatures is False
    
    def test_env_variable_override_auto_update(self, monkeypatch):
        """Test environment variable override for auto_update."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "config.toml"
            
            # Save config with auto_update=True
            config = Config(better11=Better11Config(auto_update=True))
            config.save(path)
            
            # Set env variable to override
            monkeypatch.setenv('BETTER11_AUTO_UPDATE', 'false')
            
            # Load config - should be overridden
            loaded = Config.load(path)
            assert loaded.better11.auto_update is False
    
    def test_env_variable_override_log_level(self, monkeypatch):
        """Test environment variable override for log level."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "config.toml"
            
            config = Config(logging=LoggingConfig(level="INFO"))
            config.save(path)
            
            monkeypatch.setenv('BETTER11_LOG_LEVEL', 'DEBUG')
            
            loaded = Config.load(path)
            assert loaded.logging.level == "DEBUG"
    
    def test_invalid_toml_file(self):
        """Test handling of invalid TOML file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "invalid.toml"
            
            # Write invalid TOML
            with open(path, 'w') as f:
                f.write("this is not valid TOML {][")
            
            # Should raise ValueError
            with pytest.raises(ValueError, match="Failed to load configuration"):
                Config.load(path)
    
    def test_unsupported_file_format(self):
        """Test unsupported configuration file format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "config.json"
            
            with open(path, 'w') as f:
                f.write('{}')
            
            with pytest.raises(ValueError, match="Unsupported configuration format"):
                Config.load(path)
    
    def test_system_path_windows(self, monkeypatch):
        """Test system configuration path on Windows."""
        path = Config.get_system_path(os_name='nt', env={'PROGRAMDATA': r'C:\ProgramData'})
        assert 'ProgramData' in str(path)
        assert 'Better11' in str(path)
    
    def test_from_dict_with_partial_data(self):
        """Test creating config from partial dictionary."""
        data = {
            'better11': {'auto_update': False},
            'applications': {}
        }
        
        config = Config._from_dict(data)
        assert config.better11.auto_update is False
        assert config.better11.version == "0.3.0"  # Default
        assert config.applications.verify_signatures is True  # Default
