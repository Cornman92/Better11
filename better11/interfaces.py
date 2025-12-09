"""Common interfaces and base classes for Better11 components.

This module defines the core interfaces that components implement for
consistency and extensibility.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Version:
    """Semantic version representation.
    
    Supports comparison operators and parsing from version strings.
    """
    
    major: int
    minor: int
    patch: int
    
    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"
    
    def __repr__(self) -> str:
        return f"Version({self.major}, {self.minor}, {self.patch})"
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)
    
    def __lt__(self, other: Version) -> bool:
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)
    
    def __le__(self, other: Version) -> bool:
        return self == other or self < other
    
    def __gt__(self, other: Version) -> bool:
        return not self <= other
    
    def __ge__(self, other: Version) -> bool:
        return not self < other
    
    @classmethod
    def parse(cls, version_str: str) -> "Version":
        """Parse version string like '1.2.3'.
        
        Parameters
        ----------
        version_str : str
            Version string in format "major.minor.patch"
        
        Returns
        -------
        Version
            Parsed version object
        
        Raises
        ------
        ValueError
            If version string format is invalid
        """
        try:
            parts = version_str.strip().split('.')
            if len(parts) != 3:
                raise ValueError(f"Version must have 3 parts (major.minor.patch), got: {version_str}")
            
            major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
            return cls(major, minor, patch)
        except (ValueError, IndexError) as exc:
            raise ValueError(f"Invalid version string: {version_str}") from exc


class Updatable(ABC):
    """Interface for components that can be updated.
    
    Implement this interface for any component that supports checking for
    updates, downloading, and installing new versions.
    """
    
    @abstractmethod
    def get_current_version(self) -> Version:
        """Get the currently installed version.
        
        Returns
        -------
        Version
            Current version
        """
        pass
    
    @abstractmethod
    def check_for_updates(self) -> Optional[Version]:
        """Check if updates are available.
        
        Returns
        -------
        Optional[Version]
            New version if available, None otherwise
        """
        pass
    
    @abstractmethod
    def download_update(self, version: Version) -> Path:
        """Download the update package for the specified version.
        
        Parameters
        ----------
        version : Version
            Version to download
        
        Returns
        -------
        Path
            Path to downloaded update package
        
        Raises
        ------
        DownloadError
            If download fails
        """
        pass
    
    @abstractmethod
    def install_update(self, package_path: Path) -> bool:
        """Install the downloaded update.
        
        Parameters
        ----------
        package_path : Path
            Path to update package
        
        Returns
        -------
        bool
            True if installation successful
        
        Raises
        ------
        InstallError
            If installation fails
        """
        pass
    
    @abstractmethod
    def rollback_update(self) -> bool:
        """Rollback to previous version if update fails.
        
        Returns
        -------
        bool
            True if rollback successful
        """
        pass


class Configurable(ABC):
    """Interface for configurable components.
    
    Implement this interface for components that can be configured
    through configuration files or programmatic API.
    """
    
    @abstractmethod
    def load_config(self, config: dict) -> None:
        """Load configuration from dictionary.
        
        Parameters
        ----------
        config : dict
            Configuration dictionary
        
        Raises
        ------
        ValueError
            If configuration is invalid
        """
        pass
    
    @abstractmethod
    def get_config_schema(self) -> dict:
        """Get JSON schema for configuration validation.
        
        Returns
        -------
        dict
            JSON schema describing valid configuration
        """
        pass
    
    @abstractmethod
    def validate_config(self, config: dict) -> bool:
        """Validate configuration against schema.
        
        Parameters
        ----------
        config : dict
            Configuration to validate
        
        Returns
        -------
        bool
            True if configuration is valid
        
        Raises
        ------
        ValueError
            If configuration is invalid with description
        """
        pass


class Monitorable(ABC):
    """Interface for components that can be monitored.
    
    Implement this interface for components that expose performance
    metrics and health status.
    """
    
    @abstractmethod
    def get_status(self) -> dict:
        """Get current status and metrics.
        
        Returns
        -------
        dict
            Status dictionary with metrics
        """
        pass
    
    @abstractmethod
    def get_health(self) -> str:
        """Get health status.
        
        Returns
        -------
        str
            Health status: "healthy", "degraded", or "unhealthy"
        """
        pass


class Backupable(ABC):
    """Interface for components that support backup and restore.
    
    Implement this interface for components whose state can be backed up
    and restored.
    """
    
    @abstractmethod
    def create_backup(self, destination: Path) -> Path:
        """Create a backup of current state.
        
        Parameters
        ----------
        destination : Path
            Directory to store backup
        
        Returns
        -------
        Path
            Path to created backup file
        """
        pass
    
    @abstractmethod
    def restore_backup(self, backup_path: Path) -> bool:
        """Restore state from backup.
        
        Parameters
        ----------
        backup_path : Path
            Path to backup file
        
        Returns
        -------
        bool
            True if restore successful
        """
        pass
    
    @abstractmethod
    def verify_backup(self, backup_path: Path) -> bool:
        """Verify backup integrity.
        
        Parameters
        ----------
        backup_path : Path
            Path to backup file
        
        Returns
        -------
        bool
            True if backup is valid
        """
        pass


__all__ = [
    "Version",
    "Updatable",
    "Configurable",
    "Monitorable",
    "Backupable",
]
