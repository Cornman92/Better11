"""Tests for NetworkManager ipconfig parsing."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from system_tools.network import AdapterStatus, NetworkManager


_IPCONFIG_SAMPLE = r"""
Windows IP Configuration

   Host Name . . . . . . . . . . . . : demo

Ethernet adapter Ethernet:

   Connection-specific DNS Suffix  . : lan
   Description . . . . . . . . . . . : Intel(R) Ethernet Connection
   Physical Address. . . . . . . . . : AA-BB-CC-DD-EE-FF
   DHCP Enabled. . . . . . . . . . . : Yes
   Autoconfiguration Enabled . . . . : Yes
   Media State . . . . . . . . . . . : Media disconnected

Wireless LAN adapter Wi-Fi:

   Connection-specific DNS Suffix  . : home
   Description . . . . . . . . . . . : Intel(R) Wi-Fi 6 AX200
   Physical Address. . . . . . . . . : 11-22-33-44-55-66
   DHCP Enabled. . . . . . . . . . . : Yes
   IPv4 Address. . . . . . . . . . . : 192.168.1.50(Preferred)
   Subnet Mask . . . . . . . . . . . : 255.255.255.0
   Default Gateway . . . . . . . . . : 192.168.1.1
   DNS Servers . . . . . . . . . . . : 1.1.1.1
                                       1.0.0.1
"""


def test_parse_ipconfig_output_extracts_adapters():
    manager = NetworkManager(dry_run=True)
    adapters = manager._parse_ipconfig_output(_IPCONFIG_SAMPLE)

    assert len(adapters) == 2

    eth = adapters[0]
    assert eth.name.lower() == "ethernet"
    assert eth.description.startswith("Intel")
    assert eth.mac_address == "AA-BB-CC-DD-EE-FF"
    assert eth.dhcp_enabled is True
    assert eth.status == AdapterStatus.DOWN

    wifi = adapters[1]
    assert wifi.name.lower() == "wi-fi"
    assert wifi.status == AdapterStatus.UP
    assert wifi.ipv4_address == "192.168.1.50"
    assert wifi.ipv4_subnet == "255.255.255.0"
    assert wifi.ipv4_gateway == "192.168.1.1"
    assert wifi.dns_servers == ["1.1.1.1", "1.0.0.1"]


@patch("system_tools.network.platform.system")
@patch("system_tools.network.subprocess.run")
def test_list_adapters_windows_parses_ipconfig(mock_run, mock_system):
    mock_system.return_value = "Windows"

    completed = MagicMock()
    completed.stdout = _IPCONFIG_SAMPLE
    completed.returncode = 0
    mock_run.return_value = completed

    manager = NetworkManager(dry_run=True)
    adapters = manager.list_adapters()

    assert len(adapters) == 2
    mock_run.assert_called_once()
