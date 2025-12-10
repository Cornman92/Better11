"""Tests for enhanced logging configuration."""
from __future__ import annotations

import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from better11.logging_config import (
    Better11Logger,
    LoggingConfig,
    audit,
    get_logger,
    setup_logging,
)


class TestLoggingConfig:
    """Test LoggingConfig dataclass."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = LoggingConfig()
        
        assert config.level == "INFO"
        assert config.file_enabled is True
        assert config.console_enabled is True
        assert config.max_log_size_mb == 10
        assert config.backup_count == 5
        assert config.audit_enabled is True
        assert "better11" in str(config.log_dir)
    
    def test_custom_config(self):
        """Test custom configuration."""
        log_dir = Path("/tmp/test_logs")
        config = LoggingConfig(
            level="DEBUG",
            file_enabled=False,
            max_log_size_mb=20,
            log_dir=log_dir
        )
        
        assert config.level == "DEBUG"
        assert config.file_enabled is False
        assert config.max_log_size_mb == 20
        assert config.log_dir == log_dir


class TestBetter11Logger:
    """Test Better11Logger class."""
    
    def test_logger_initialization(self, tmp_path):
        """Test logger initialization."""
        config = LoggingConfig(log_dir=tmp_path / "logs")
        logger = Better11Logger(config)
        
        assert logger.config == config
        assert logger._setup_complete is False
    
    def test_logger_setup(self, tmp_path):
        """Test logger setup."""
        config = LoggingConfig(log_dir=tmp_path / "logs")
        logger = Better11Logger(config)
        logger.setup()
        
        assert logger._setup_complete is True
        assert (tmp_path / "logs").exists()
    
    def test_get_logger(self, tmp_path):
        """Test getting a logger."""
        config = LoggingConfig(log_dir=tmp_path / "logs")
        logger = Better11Logger(config)
        
        log = logger.get_logger("test_module")
        
        assert isinstance(log, logging.Logger)
        assert "better11.test_module" in log.name
    
    def test_file_logging(self, tmp_path):
        """Test logging to file."""
        config = LoggingConfig(
            log_dir=tmp_path / "logs",
            file_enabled=True,
            console_enabled=False
        )
        logger = Better11Logger(config)
        logger.setup()
        
        log = logger.get_logger("test")
        log.info("Test message")
        
        log_file = tmp_path / "logs" / "better11.log"
        assert log_file.exists()
        
        content = log_file.read_text()
        assert "Test message" in content
        assert "INFO" in content
    
    def test_console_logging(self, tmp_path, capsys):
        """Test logging to console."""
        config = LoggingConfig(
            log_dir=tmp_path / "logs",
            file_enabled=False,
            console_enabled=True
        )
        logger = Better11Logger(config)
        logger.setup()
        
        log = logger.get_logger("test")
        log.info("Console message")
        
        captured = capsys.readouterr()
        assert "Console message" in captured.out
        assert "INFO" in captured.out
    
    def test_log_levels(self, tmp_path):
        """Test different log levels."""
        config = LoggingConfig(
            log_dir=tmp_path / "logs",
            level="DEBUG",
            console_enabled=False
        )
        logger = Better11Logger(config)
        logger.setup()
        
        log = logger.get_logger("test")
        log.debug("Debug message")
        log.info("Info message")
        log.warning("Warning message")
        log.error("Error message")
        
        log_file = tmp_path / "logs" / "better11.log"
        content = log_file.read_text()
        
        assert "Debug message" in content
        assert "Info message" in content
        assert "Warning message" in content
        assert "Error message" in content
    
    def test_audit_logging(self, tmp_path):
        """Test audit trail logging."""
        config = LoggingConfig(
            log_dir=tmp_path / "logs",
            audit_enabled=True,
            console_enabled=False
        )
        logger = Better11Logger(config)
        logger.setup()
        
        logger.audit("Test audit message")
        
        audit_file = tmp_path / "logs" / "audit.log"
        assert audit_file.exists()
        
        content = audit_file.read_text()
        assert "Test audit message" in content
        assert "AUDIT" in content
    
    def test_audit_with_username(self, tmp_path):
        """Test audit logging with username."""
        config = LoggingConfig(
            log_dir=tmp_path / "logs",
            audit_enabled=True,
            console_enabled=False
        )
        logger = Better11Logger(config)
        logger.setup()
        
        logger.audit("User action", username="testuser")
        
        audit_file = tmp_path / "logs" / "audit.log"
        content = audit_file.read_text()
        
        assert "User action" in content
        assert "testuser" in content
    
    def test_log_rotation_size(self, tmp_path):
        """Test log rotation based on file size."""
        config = LoggingConfig(
            log_dir=tmp_path / "logs",
            max_log_size_mb=0.001,  # Very small for testing (1KB)
            backup_count=2,
            console_enabled=False
        )
        logger = Better11Logger(config)
        logger.setup()
        
        log = logger.get_logger("test")
        
        # Write enough to trigger rotation
        for i in range(100):
            log.info(f"Message {i}: {'x' * 100}")
        
        # Check that backup files exist
        log_files = list((tmp_path / "logs").glob("better11.log*"))
        assert len(log_files) > 1
    
    def test_shutdown(self, tmp_path):
        """Test logger shutdown."""
        config = LoggingConfig(log_dir=tmp_path / "logs")
        logger = Better11Logger(config)
        logger.setup()
        
        log = logger.get_logger("test")
        log.info("Before shutdown")
        
        logger.shutdown()
        
        # Logging should still work but handlers might be closed
        # Just ensure shutdown doesn't crash
        assert True


class TestGlobalFunctions:
    """Test module-level convenience functions."""
    
    def test_setup_logging(self, tmp_path):
        """Test global setup_logging function."""
        config = LoggingConfig(log_dir=tmp_path / "logs")
        logger = setup_logging(config)
        
        assert isinstance(logger, Better11Logger)
        assert logger._setup_complete is True
    
    def test_get_logger_convenience(self, tmp_path):
        """Test get_logger convenience function."""
        config = LoggingConfig(log_dir=tmp_path / "logs")
        setup_logging(config)
        
        log = get_logger("test_module")
        
        assert isinstance(log, logging.Logger)
        assert "test_module" in log.name
    
    def test_audit_convenience(self, tmp_path):
        """Test audit convenience function."""
        # Reset global logger for this test
        import better11.logging_config
        better11.logging_config._global_logger = None
        
        config = LoggingConfig(
            log_dir=tmp_path / "logs",
            console_enabled=False,
            audit_enabled=True
        )
        setup_logging(config)
        
        audit("Test audit via convenience function")
        
        audit_file = tmp_path / "logs" / "audit.log"
        assert audit_file.exists()
        
        content = audit_file.read_text()
        assert "Test audit via convenience function" in content
    
    def test_get_logger_auto_setup(self, tmp_path):
        """Test that get_logger sets up logging automatically."""
        # Don't call setup_logging first
        log = get_logger("auto_setup_test")
        
        assert isinstance(log, logging.Logger)
        assert "auto_setup_test" in log.name


class TestLoggingIntegration:
    """Integration tests for logging system."""
    
    def test_multiple_loggers(self, tmp_path):
        """Test multiple loggers writing to same file."""
        config = LoggingConfig(
            log_dir=tmp_path / "logs",
            console_enabled=False
        )
        logger = Better11Logger(config)
        logger.setup()
        
        log1 = logger.get_logger("module1")
        log2 = logger.get_logger("module2")
        
        log1.info("Message from module1")
        log2.info("Message from module2")
        
        log_file = tmp_path / "logs" / "better11.log"
        content = log_file.read_text()
        
        assert "Message from module1" in content
        assert "Message from module2" in content
        assert "module1" in content
        assert "module2" in content
    
    def test_logging_with_exceptions(self, tmp_path):
        """Test logging exceptions with traceback."""
        config = LoggingConfig(
            log_dir=tmp_path / "logs",
            console_enabled=False
        )
        logger = Better11Logger(config)
        logger.setup()
        
        log = logger.get_logger("test")
        
        try:
            raise ValueError("Test error")
        except ValueError:
            log.exception("An error occurred")
        
        log_file = tmp_path / "logs" / "better11.log"
        content = log_file.read_text()
        
        assert "An error occurred" in content
        assert "ValueError: Test error" in content
        assert "Traceback" in content
    
    def test_audit_trail_separate_from_logs(self, tmp_path):
        """Test that audit trail is separate from regular logs."""
        config = LoggingConfig(
            log_dir=tmp_path / "logs",
            console_enabled=False
        )
        logger = Better11Logger(config)
        logger.setup()
        
        log = logger.get_logger("test")
        log.info("Regular log message")
        
        logger.audit("Audit trail message")
        
        # Check regular log
        log_file = tmp_path / "logs" / "better11.log"
        log_content = log_file.read_text()
        assert "Regular log message" in log_content
        assert "Audit trail message" not in log_content
        
        # Check audit log
        audit_file = tmp_path / "logs" / "audit.log"
        audit_content = audit_file.read_text()
        assert "Audit trail message" in audit_content
        assert "Regular log message" not in audit_content
    
    def test_format_customization(self, tmp_path):
        """Test custom log format."""
        config = LoggingConfig(
            log_dir=tmp_path / "logs",
            format_string="%(levelname)s - %(message)s",
            console_enabled=False
        )
        logger = Better11Logger(config)
        logger.setup()
        
        log = logger.get_logger("test")
        log.info("Custom format test")
        
        log_file = tmp_path / "logs" / "better11.log"
        content = log_file.read_text()
        
        assert "INFO - Custom format test" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
