"""Network configuration and diagnostics.

This module provides network adapter management, DNS configuration,
and network diagnostics tools.
"""
from __future__ import annotations

import subprocess
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from . import get_logger
from .base import SystemTool, ToolMetadata

_LOGGER = get_logger(__name__)


class AdapterStatus(Enum):
    """Network adapter status."""
    
    UP = "up"
    DOWN = "down"
    UNKNOWN = "unknown"


@dataclass
class NetworkAdapter:
    """Network adapter information."""
    
    name: str
    description: str
    mac_address: str
    status: AdapterStatus
    ipv4_address: Optional[str] = None
    ipv4_subnet: Optional[str] = None
    ipv4_gateway: Optional[str] = None
    dns_servers: Optional[List[str]] = None
    dhcp_enabled: bool = True


@dataclass
class DNSConfiguration:
    """DNS configuration."""
    
    primary: str
    secondary: Optional[str] = None
    tertiary: Optional[str] = None


class NetworkManager(SystemTool):
    """Manage network configuration and diagnostics.
    
    This class provides methods for network adapter management,
    DNS configuration, and network diagnostics.
    
    Parameters
    ----------
    config : dict, optional
        Configuration dictionary
    dry_run : bool
        If True, simulate operations without making changes
    """
    
    # Common DNS providers
    GOOGLE_DNS = DNSConfiguration("8.8.8.8", "8.8.4.4")
    CLOUDFLARE_DNS = DNSConfiguration("1.1.1.1", "1.0.0.1")
    QUAD9_DNS = DNSConfiguration("9.9.9.9", "149.112.112.112")
    OPENDNS = DNSConfiguration("208.67.222.222", "208.67.220.220")
    
    def __init__(self, config: Optional[dict] = None, dry_run: bool = False):
        super().__init__(config, dry_run)
    
    def get_metadata(self) -> ToolMetadata:
        """Return tool metadata."""
        return ToolMetadata(
            name="Network Manager",
            description="Manage network configuration and diagnostics",
            version="0.3.0",
            requires_admin=True,  # Most operations need admin
            requires_restart=False,
            category="network"
        )
    
    def validate_environment(self) -> None:
        """Validate network management prerequisites."""
        pass
    
    def execute(self) -> bool:
        """Execute default network listing operation."""
        adapters = self.list_adapters()
        _LOGGER.info("Found %d network adapters", len(adapters))
        return True
    
    def list_adapters(self) -> List[NetworkAdapter]:
        """List all network adapters.
        
        Returns
        -------
        List[NetworkAdapter]
            List of network adapters
        """
        _LOGGER.info("Listing network adapters")
        
        import platform
        if platform.system() != "Windows":
            _LOGGER.warning("Full adapter listing only supported on Windows")
            return []
        
        # Use ipconfig to list adapters
        try:
            result = subprocess.run(
                ["ipconfig", "/all"],
                capture_output=True,
                text=True,
                check=True
            )
            
            adapters = self._parse_ipconfig_output(result.stdout)
            _LOGGER.info("Found %d adapters", len(adapters))
            return adapters
        
        except subprocess.CalledProcessError as exc:
            _LOGGER.error("Failed to list adapters: %s", exc)
            return []
    
    def _parse_ipconfig_output(self, output: str) -> List[NetworkAdapter]:
        """Parse ipconfig output into adapter list."""
        # Simplified parser - in production, use more robust parsing
        adapters: List[NetworkAdapter] = []
        # TODO: Implement proper ipconfig parsing
        return adapters
    
    def configure_dns(self, adapter_name: str, dns_config: DNSConfiguration) -> bool:
        """Configure DNS servers for an adapter.
        
        Parameters
        ----------
        adapter_name : str
            Name of network adapter
        dns_config : DNSConfiguration
            DNS configuration to apply
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Configuring DNS for adapter: %s", adapter_name)
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would configure DNS to %s", dns_config.primary)
            return True
        
        import platform
        if platform.system() != "Windows":
            _LOGGER.error("DNS configuration only supported on Windows")
            return False
        
        try:
            # Set primary DNS
            cmd = [
                "netsh", "interface", "ip", "set", "dns",
                adapter_name, "static", dns_config.primary
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Set secondary DNS if provided
            if dns_config.secondary:
                cmd = [
                    "netsh", "interface", "ip", "add", "dns",
                    adapter_name, dns_config.secondary, "index=2"
                ]
                subprocess.run(cmd, check=True, capture_output=True)
            
            _LOGGER.info("DNS configured successfully")
            return True
        
        except subprocess.CalledProcessError as exc:
            _LOGGER.error("Failed to configure DNS: %s", exc)
            return False
    
    def flush_dns_cache(self) -> bool:
        """Flush DNS resolver cache.
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Flushing DNS cache")
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would flush DNS cache")
            return True
        
        import platform
        if platform.system() != "Windows":
            _LOGGER.error("DNS flush only supported on Windows")
            return False
        
        try:
            subprocess.run(
                ["ipconfig", "/flushdns"],
                check=True,
                capture_output=True
            )
            _LOGGER.info("DNS cache flushed successfully")
            return True
        
        except subprocess.CalledProcessError as exc:
            _LOGGER.error("Failed to flush DNS cache: %s", exc)
            return False
    
    def reset_tcp_ip(self) -> bool:
        """Reset TCP/IP stack.
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Resetting TCP/IP stack")
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would reset TCP/IP stack")
            return True
        
        import platform
        if platform.system() != "Windows":
            _LOGGER.error("TCP/IP reset only supported on Windows")
            return False
        
        try:
            subprocess.run(
                ["netsh", "int", "ip", "reset"],
                check=True,
                capture_output=True
            )
            _LOGGER.info("TCP/IP stack reset successfully")
            _LOGGER.warning("System restart required for changes to take effect")
            return True
        
        except subprocess.CalledProcessError as exc:
            _LOGGER.error("Failed to reset TCP/IP: %s", exc)
            return False
    
    def reset_winsock(self) -> bool:
        """Reset Winsock catalog.
        
        Returns
        -------
        bool
            True if successful
        """
        _LOGGER.info("Resetting Winsock catalog")
        
        if self.dry_run:
            _LOGGER.info("[DRY RUN] Would reset Winsock")
            return True
        
        import platform
        if platform.system() != "Windows":
            _LOGGER.error("Winsock reset only supported on Windows")
            return False
        
        try:
            subprocess.run(
                ["netsh", "winsock", "reset"],
                check=True,
                capture_output=True
            )
            _LOGGER.info("Winsock reset successfully")
            _LOGGER.warning("System restart required for changes to take effect")
            return True
        
        except subprocess.CalledProcessError as exc:
            _LOGGER.error("Failed to reset Winsock: %s", exc)
            return False
    
    def test_connectivity(self, host: str = "8.8.8.8") -> bool:
        """Test network connectivity to a host.
        
        Parameters
        ----------
        host : str
            Host to ping
        
        Returns
        -------
        bool
            True if host is reachable
        """
        _LOGGER.info("Testing connectivity to %s", host)
        
        import platform
        
        # Build ping command based on platform
        if platform.system() == "Windows":
            cmd = ["ping", "-n", "4", host]
        else:
            cmd = ["ping", "-c", "4", host]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=10)
            _LOGGER.info("Host %s is reachable", host)
            return True
        
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            _LOGGER.warning("Host %s is not reachable", host)
            return False


__all__ = [
    "AdapterStatus",
    "NetworkAdapter",
    "DNSConfiguration",
    "NetworkManager",
]
