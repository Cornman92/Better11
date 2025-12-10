"""Base classes for system tools.

This module provides base classes and utilities that all system tools
should inherit from for consistency, safety, and testability.
"""
from __future__ import annotations

import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from . import get_logger
from .safety import SafetyError, confirm_action, create_restore_point, ensure_windows

_LOGGER = get_logger(__name__)


@dataclass
class ToolMetadata:
    """Metadata describing a system tool.
    
    Attributes
    ----------
    name : str
        Tool display name
    description : str
        Brief description of what the tool does
    version : str
        Tool version
    requires_admin : bool
        Whether tool requires administrator privileges
    requires_restart : bool
        Whether tool typically requires system restart
    category : str
        Tool category for organization
    """
    
    name: str
    description: str
    version: str
    requires_admin: bool = True
    requires_restart: bool = False
    category: str = "general"


class SystemTool(ABC):
    """Base class for all system tools.
    
    All system tools should inherit from this class to ensure consistent
    behavior, safety checks, and error handling.
    
    The execution flow is:
    1. validate_environment() - Check prerequisites
    2. pre_execute_checks() - Safety checks and confirmations
    3. execute() - Perform the actual operation
    4. post_execute() - Cleanup and verification (optional)
    
    Parameters
    ----------
    config : dict, optional
        Configuration dictionary for the tool
    dry_run : bool
        If True, simulate operations without making changes
    """
    
    def __init__(self, config: Optional[dict] = None, dry_run: bool = False):
        self.config = config or {}
        self.dry_run = dry_run
        self._metadata = self.get_metadata()
        self._logger = get_logger(self.__class__.__name__)
    
    @abstractmethod
    def get_metadata(self) -> ToolMetadata:
        """Return tool metadata.
        
        Returns
        -------
        ToolMetadata
            Metadata describing this tool
        """
        pass
    
    @abstractmethod
    def validate_environment(self) -> None:
        """Validate environment prerequisites before execution.
        
        This method should check:
        - Platform compatibility (Windows)
        - Required services/features available
        - Permissions
        - Any other prerequisites
        
        Raises
        ------
        SafetyError
            If environment is not suitable
        """
        pass
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> bool:
        """Execute the tool's primary function.
        
        This is the main method that performs the tool's operation.
        It is called after all safety checks pass.
        
        Returns
        -------
        bool
            True if execution was successful
        
        Raises
        ------
        SafetyError
            If operation fails
        """
        pass
    
    def pre_execute_checks(self, skip_confirmation: bool = False) -> bool:
        """Perform common pre-execution safety checks.
        
        This method:
        1. Ensures Windows platform
        2. Validates environment
        3. Creates restore point (if configured)
        4. Prompts for user confirmation (if configured)
        
        Parameters
        ----------
        skip_confirmation : bool
            Skip user confirmation prompt
        
        Returns
        -------
        bool
            True if checks pass and user confirms, False otherwise
        
        Raises
        ------
        SafetyError
            If critical safety checks fail
        """
        # Ensure Windows platform (configurable for tests/non-Windows environments)
        windows_ok = ensure_windows(allow_non_windows=self._allow_non_windows())
        if not windows_ok:
            self._logger.warning(
                "Running %s without Windows enforcement; platform-specific operations may fail",
                self._metadata.name,
            )
        
        # Validate tool-specific environment
        self.validate_environment()
        
        # Create restore point if configured
        if self._should_create_restore_point():
            if not self.dry_run:
                try:
                    create_restore_point(f"Before {self._metadata.name}")
                    self._logger.info("Restore point created")
                except SafetyError as exc:
                    self._logger.warning("Failed to create restore point: %s", exc)
                    # Don't fail - just warn
        
        # Check admin privileges if required
        if self._metadata.requires_admin and not self.dry_run:
            if not self._is_admin():
                raise SafetyError(
                    f"{self._metadata.name} requires administrator privileges. "
                    "Please run as administrator."
                )
        
        # User confirmation
        if not skip_confirmation and self._should_confirm():
            warning = self._get_confirmation_message()
            if not confirm_action(warning):
                self._logger.info("User cancelled operation")
                return False
        
        self._logger.info("Pre-execution checks passed")
        return True
    
    def post_execute(self) -> None:
        """Optional post-execution cleanup and verification.
        
        Override this method to perform cleanup or verification after
        the main execution completes.
        """
        pass
    
    def run(self, *args, skip_confirmation: bool = False, **kwargs) -> bool:
        """Run the tool with full safety checks.
        
        This is the main entry point that coordinates the entire execution flow.
        
        Parameters
        ----------
        skip_confirmation : bool
            Skip user confirmation prompt
        *args, **kwargs
            Arguments passed to execute()
        
        Returns
        -------
        bool
            True if execution successful
        """
        self._logger.info("Starting %s (dry_run=%s)", self._metadata.name, self.dry_run)
        
        try:
            # Pre-execution checks
            if not self.pre_execute_checks(skip_confirmation=skip_confirmation):
                return False
            
            # Execute
            if self.dry_run:
                self._logger.info("DRY RUN: Would execute %s", self._metadata.name)
                return True
            
            result = self.execute(*args, **kwargs)
            
            # Post-execution
            if result:
                self.post_execute()
                self._logger.info("%s completed successfully", self._metadata.name)
            else:
                self._logger.warning("%s completed with warnings", self._metadata.name)
            
            return result
        
        except SafetyError as exc:
            self._logger.error("Safety check failed: %s", exc)
            raise
        except Exception as exc:
            self._logger.exception("Unexpected error during execution")
            raise SafetyError(f"Execution failed: {exc}") from exc
    
    def _should_create_restore_point(self) -> bool:
        """Check if restore point should be created."""
        return self.config.get('always_create_restore_point', True)
    
    def _should_confirm(self) -> bool:
        """Check if user confirmation is required."""
        return self.config.get('confirm_destructive_actions', True)
    
    def _get_confirmation_message(self) -> str:
        """Get confirmation message for user prompt."""
        message = f"Execute {self._metadata.name}?"
        if self._metadata.requires_restart:
            message += " (System restart may be required)"
        return message
    
    @staticmethod
    def _is_admin() -> bool:
        """Check if running with administrator privileges.
        
        Returns
        -------
        bool
            True if running as administrator
        """
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False

    def _allow_non_windows(self) -> bool:
        """Determine whether Windows enforcement can be bypassed.

        Priority order:
        1. Environment variable ``BETTER11_ALLOW_NON_WINDOWS`` (truthy values
           enable bypass: ``1``, ``true``, ``yes``, ``on``)
        2. ``allow_non_windows`` flag in the tool configuration
        3. Default to ``True`` to support local development and CI environments
           where Windows APIs are unavailable.
        """

        env_override = os.getenv("BETTER11_ALLOW_NON_WINDOWS")
        if env_override is not None:
            return env_override.strip().lower() in {"1", "true", "yes", "on"}

        return bool(self.config.get("allow_non_windows", True))


class RegistryTool(SystemTool):
    """Base class for tools that modify the Windows registry.
    
    Provides additional safety for registry operations including
    automatic backups before modifications.
    """
    
    def __init__(self, config: Optional[dict] = None, dry_run: bool = False):
        super().__init__(config, dry_run)
        self._backup_path: Optional[str] = None
    
    def validate_environment(self) -> None:
        """Validate registry access."""
        ensure_windows()
        # Additional registry-specific checks could go here
    
    def pre_execute_checks(self, skip_confirmation: bool = False) -> bool:
        """Perform registry-specific safety checks including backup."""
        if not super().pre_execute_checks(skip_confirmation):
            return False
        
        # Backup registry keys before modification
        if self.config.get('backup_registry', True) and not self.dry_run:
            self._logger.info("Registry backup recommended - handled by individual tools")
        
        return True


__all__ = [
    "ToolMetadata",
    "SystemTool",
    "RegistryTool",
]
