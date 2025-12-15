"""Network configuration and diagnostics.

This module provides network adapter management, DNS configuration,
and network diagnostics tools.
"""
from __future__ import annotations

import platform
import re
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
        adapters: List[NetworkAdapter] = []

        current: Optional[NetworkAdapter] = None
        pending_dns: List[str] = []
        in_dns_block = False

        def flush_current() -> None:
            nonlocal current, pending_dns, in_dns_block
            if current is None:
                return
            # Heuristic: if ipconfig doesn't provide Media State, treat adapters
            # with an IPv4 address (or gateway) as UP.
            if current.status == AdapterStatus.UNKNOWN and (current.ipv4_address or current.ipv4_gateway):
                current.status = AdapterStatus.UP
            if pending_dns:
                current.dns_servers = pending_dns.copy()
            adapters.append(current)
            current = None
            pending_dns = []
            in_dns_block = False

        # Example headers:
        # "Ethernet adapter Ethernet:"
        # "Wireless LAN adapter Wi-Fi:"
        adapter_header = re.compile(r"^(?P<prefix>.+?)\s+adapter\s+(?P<name>.+?):\s*$", re.IGNORECASE)

        def normalize_bool(value: str) -> Optional[bool]:
            lowered = value.strip().lower()
            if lowered in ("yes", "true"):
                return True
            if lowered in ("no", "false"):
                return False
            return None

        def parse_value(line: str) -> Optional[str]:
            # Matches the "Key . . . : Value" layout.
            if ":" not in line:
                return None
            return line.split(":", 1)[1].strip()

        for raw_line in output.splitlines():
            line = raw_line.rstrip("\r\n")
            stripped = line.strip()

            if not stripped:
                # Blank line ends current DNS multi-line block and often separates adapters.
                in_dns_block = False
                continue

            header_match = adapter_header.match(stripped)
            if header_match:
                flush_current()
                name = header_match.group("name").strip()
                current = NetworkAdapter(
                    name=name,
                    description="",
                    mac_address="",
                    status=AdapterStatus.UNKNOWN,
                    dns_servers=[],
                )
                continue

            if current is None:
                continue

            # Continuation line for DNS servers block (indented line without key).
            if in_dns_block and ":" not in stripped:
                candidate = stripped
                if candidate:
                    pending_dns.append(candidate)
                continue

            lower = stripped.lower()

            if lower.startswith("description"):
                value = parse_value(stripped) or ""
                current.description = value
            elif lower.startswith("physical address"):
                value = parse_value(stripped) or ""
                current.mac_address = value
            elif lower.startswith("dhcp enabled"):
                value = parse_value(stripped) or ""
                parsed = normalize_bool(value)
                if parsed is not None:
                    current.dhcp_enabled = parsed
            elif lower.startswith("media state"):
                value = parse_value(stripped) or ""
                if "disconnected" in value.lower():
                    current.status = AdapterStatus.DOWN
                else:
                    current.status = AdapterStatus.UP
            elif lower.startswith("ipv4 address"):
                value = parse_value(stripped) or ""
                # Usually: "192.168.1.10(Preferred)"
                current.ipv4_address = value.split("(")[0].strip()
            elif lower.startswith("subnet mask"):
                value = parse_value(stripped) or ""
                current.ipv4_subnet = value
            elif lower.startswith("default gateway"):
                value = parse_value(stripped) or ""
                # Sometimes gateway is blank, or appears on following indented line.
                if value:
                    current.ipv4_gateway = value
            elif lower.startswith("dns servers"):
                value = parse_value(stripped) or ""
                pending_dns = []
                in_dns_block = True
                if value:
                    pending_dns.append(value)

        flush_current()
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
