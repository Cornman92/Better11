"""Enhanced logging configuration for Better11.

This module provides structured logging with rotation, audit trails,
and multiple output targets.
"""
from __future__ import annotations

import logging
import logging.handlers
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class LoggingConfig:
    """Logging configuration settings.
    
    Attributes
    ----------
    level : str
        Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    file_enabled : bool
        Enable logging to file
    console_enabled : bool
        Enable logging to console
    max_log_size_mb : int
        Maximum log file size in MB before rotation
    backup_count : int
        Number of backup log files to keep
    log_dir : Path
        Directory for log files
    audit_enabled : bool
        Enable audit trail for system modifications
    format_string : str
        Log message format string
    """
    
    level: str = "INFO"
    file_enabled: bool = True
    console_enabled: bool = True
    max_log_size_mb: int = 10
    backup_count: int = 5
    log_dir: Path = Path.home() / ".better11" / "logs"
    audit_enabled: bool = True
    format_string: str = "[%(asctime)s] [%(levelname)-8s] [%(name)s] %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"


class Better11Logger:
    """Enhanced logger for Better11 with rotation and audit trail.
    
    This class provides a centralized logging system with:
    - File rotation based on size
    - Multiple log levels
    - Audit trail for system modifications
    - Console and file output
    
    Examples
    --------
    Configure and use logger:
    
    >>> config = LoggingConfig(level="DEBUG")
    >>> logger = Better11Logger(config)
    >>> logger.setup()
    >>> log = logger.get_logger(__name__)
    >>> log.info("Application started")
    >>> logger.audit("System modification: Disabled startup item 'Spotify'")
    """
    
    def __init__(self, config: Optional[LoggingConfig] = None):
        """Initialize the logger.
        
        Parameters
        ----------
        config : LoggingConfig, optional
            Logging configuration. If None, uses defaults.
        """
        self.config = config or LoggingConfig()
        self._setup_complete = False
        self._audit_logger: Optional[logging.Logger] = None
    
    def setup(self) -> None:
        """Set up logging handlers and formatters.
        
        This method:
        1. Creates log directory if needed
        2. Configures file rotation
        3. Sets up console handler
        4. Configures audit logger
        """
        if self._setup_complete:
            return
        
        # Ensure log directory exists
        self.config.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Get root logger
        root_logger = logging.getLogger("better11")
        root_logger.setLevel(getattr(logging, self.config.level.upper()))
        
        # Remove existing handlers
        root_logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            self.config.format_string,
            datefmt=self.config.date_format
        )
        
        # Add file handler with rotation
        if self.config.file_enabled:
            log_file = self.config.log_dir / "better11.log"
            max_bytes = self.config.max_log_size_mb * 1024 * 1024
            
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=self.config.backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        
        # Add console handler
        if self.config.console_enabled:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, self.config.level.upper()))
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)
        
        # Set up audit logger
        if self.config.audit_enabled:
            self._setup_audit_logger()
        
        self._setup_complete = True
        root_logger.info("Better11 logging system initialized")
    
    def _setup_audit_logger(self) -> None:
        """Set up dedicated audit trail logger."""
        audit_logger = logging.getLogger("better11.audit")
        audit_logger.setLevel(logging.INFO)
        audit_logger.propagate = False  # Don't propagate to root logger
        
        # Remove existing handlers
        audit_logger.handlers.clear()
        
        # Create audit log file with rotation
        audit_file = self.config.log_dir / "audit.log"
        max_bytes = self.config.max_log_size_mb * 1024 * 1024
        
        audit_handler = logging.handlers.RotatingFileHandler(
            audit_file,
            maxBytes=max_bytes,
            backupCount=self.config.backup_count * 2,  # Keep more audit logs
            encoding='utf-8'
        )
        
        # Audit format includes more detail
        audit_formatter = logging.Formatter(
            "[%(asctime)s] [AUDIT] [%(username)s] %(message)s",
            datefmt=self.config.date_format
        )
        audit_handler.setFormatter(audit_formatter)
        audit_logger.addHandler(audit_handler)
        
        self._audit_logger = audit_logger
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger for a specific module.
        
        Parameters
        ----------
        name : str
            Logger name (typically __name__ of the module)
        
        Returns
        -------
        logging.Logger
            Configured logger instance
        """
        if not self._setup_complete:
            self.setup()
        
        return logging.getLogger(f"better11.{name}")
    
    def audit(self, message: str, username: Optional[str] = None) -> None:
        """Log an audit trail entry.
        
        Audit entries are logged to a separate file and include
        user information for tracking system modifications.
        
        Parameters
        ----------
        message : str
            Audit message describing the action
        username : str, optional
            Username performing the action. If None, uses current user.
        
        Examples
        --------
        >>> logger.audit("Disabled startup item: Spotify")
        >>> logger.audit("Removed bloatware: CandyCrush", username="admin")
        """
        if not self._audit_logger:
            return
        
        # Get username if not provided
        if username is None:
            try:
                import getpass
                username = getpass.getuser()
            except Exception:
                username = "unknown"
        
        # Log with username in extra dict
        self._audit_logger.info(
            message,
            extra={'username': username}
        )
    
    def shutdown(self) -> None:
        """Shut down logging system and flush all handlers."""
        logging.shutdown()


# Global logger instance
_global_logger: Optional[Better11Logger] = None


def setup_logging(config: Optional[LoggingConfig] = None) -> Better11Logger:
    """Set up global logging configuration.
    
    This function should be called once at application startup.
    
    Parameters
    ----------
    config : LoggingConfig, optional
        Logging configuration. If None, uses defaults.
    
    Returns
    -------
    Better11Logger
        Configured logger instance
    
    Examples
    --------
    >>> from better11.logging_config import setup_logging
    >>> logger = setup_logging()
    >>> log = logger.get_logger(__name__)
    >>> log.info("Application started")
    """
    global _global_logger
    
    if _global_logger is None:
        _global_logger = Better11Logger(config)
        _global_logger.setup()
    
    return _global_logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a specific module.
    
    This is a convenience function that uses the global logger instance.
    If logging hasn't been set up yet, it will use default configuration.
    
    Parameters
    ----------
    name : str
        Logger name (typically __name__ of the module)
    
    Returns
    -------
    logging.Logger
        Configured logger instance
    
    Examples
    --------
    >>> from better11.logging_config import get_logger
    >>> logger = get_logger(__name__)
    >>> logger.info("Module initialized")
    """
    global _global_logger
    
    if _global_logger is None:
        setup_logging()
    
    return _global_logger.get_logger(name)  # type: ignore


def audit(message: str, username: Optional[str] = None) -> None:
    """Log an audit trail entry.
    
    This is a convenience function that uses the global logger instance.
    
    Parameters
    ----------
    message : str
        Audit message describing the action
    username : str, optional
        Username performing the action
    
    Examples
    --------
    >>> from better11.logging_config import audit
    >>> audit("System modification: Disabled telemetry")
    """
    global _global_logger
    
    if _global_logger is None:
        setup_logging()
    
    _global_logger.audit(message, username)  # type: ignore


__all__ = [
    "LoggingConfig",
    "Better11Logger",
    "setup_logging",
    "get_logger",
    "audit",
]
