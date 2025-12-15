using System;
using System.Collections.Generic;
using System.Linq;
using System.Management.Automation;
using System.Net.NetworkInformation;
using System.Threading.Tasks;
using Better11.Core.Interfaces;
using Better11.Core.Models;
using Better11.Core.PowerShell;
using Microsoft.Extensions.Logging;

namespace Better11.Core.Services
{
    /// <summary>
    /// Service for network management operations.
    /// </summary>
    public class NetworkService : INetworkService
    {
        private readonly PowerShellExecutor _psExecutor;
        private readonly ILogger<NetworkService> _logger;

        public NetworkService(PowerShellExecutor psExecutor, ILogger<NetworkService> logger)
        {
            _psExecutor = psExecutor;
            _logger = logger;
        }

        /// <inheritdoc/>
        public async Task<List<NetworkAdapter>> ListAdaptersAsync()
        {
            try
            {
                _logger.LogInformation("Listing network adapters");

                var adapters = new List<NetworkAdapter>();

                // Use .NET's NetworkInterface to get basic info
                var interfaces = NetworkInterface.GetAllNetworkInterfaces();
                
                foreach (var nic in interfaces.Where(n => 
                    n.NetworkInterfaceType != NetworkInterfaceType.Loopback))
                {
                    var properties = nic.GetIPProperties();
                    var ipv4Address = properties.UnicastAddresses
                        .FirstOrDefault(a => a.Address.AddressFamily == System.Net.Sockets.AddressFamily.InterNetwork)?
                        .Address.ToString();

                    var gateway = properties.GatewayAddresses
                        .FirstOrDefault()?.Address.ToString();

                    var dnsServers = properties.DnsAddresses
                        .Select(d => d.ToString())
                        .ToList();

                    adapters.Add(new NetworkAdapter
                    {
                        Name = nic.Name,
                        Description = nic.Description,
                        MacAddress = FormatMacAddress(nic.GetPhysicalAddress()),
                        Status = nic.OperationalStatus == OperationalStatus.Up ? AdapterStatus.Up : AdapterStatus.Down,
                        IPv4Address = ipv4Address,
                        IPv4Gateway = gateway,
                        DnsServers = dnsServers,
                        DhcpEnabled = properties.GetIPv4Properties()?.IsDhcpEnabled ?? false
                    });
                }

                _logger.LogInformation("Found {Count} network adapter(s)", adapters.Count);
                return adapters;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to list network adapters");
                throw;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> ConfigureDNSAsync(string adapterName, DNSConfiguration dnsConfig)
        {
            try
            {
                _logger.LogInformation("Configuring DNS for adapter: {Adapter}", adapterName);

                var dnsServers = new List<string> { dnsConfig.Primary };
                if (!string.IsNullOrEmpty(dnsConfig.Secondary))
                    dnsServers.Add(dnsConfig.Secondary);
                if (!string.IsNullOrEmpty(dnsConfig.Tertiary))
                    dnsServers.Add(dnsConfig.Tertiary);

                var script = $@"
                    $adapter = Get-NetAdapter -Name '{adapterName}' -ErrorAction SilentlyContinue
                    if ($adapter) {{
                        Set-DnsClientServerAddress -InterfaceIndex $adapter.InterfaceIndex -ServerAddresses @('{string.Join("','", dnsServers)}')
                        $true
                    }} else {{
                        $false
                    }}
                ";

                var result = await _psExecutor.ExecuteCommandAsync(script);
                
                if (result.Success)
                {
                    _logger.LogInformation("DNS configured successfully for {Adapter}", adapterName);
                    return true;
                }
                
                _logger.LogError("Failed to configure DNS: {Errors}", string.Join(", ", result.Errors));
                return false;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to configure DNS");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> FlushDNSCacheAsync()
        {
            try
            {
                _logger.LogInformation("Flushing DNS cache");

                var result = await _psExecutor.ExecuteCommandAsync("Clear-DnsClientCache");
                
                if (result.Success)
                {
                    _logger.LogInformation("DNS cache flushed successfully");
                    return true;
                }
                
                _logger.LogError("Failed to flush DNS cache: {Errors}", string.Join(", ", result.Errors));
                return false;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to flush DNS cache");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> ResetTcpIpAsync()
        {
            try
            {
                _logger.LogInformation("Resetting TCP/IP stack");

                var result = await _psExecutor.ExecuteCommandAsync("netsh int ip reset");
                
                if (result.Success)
                {
                    _logger.LogInformation("TCP/IP stack reset successfully");
                    return true;
                }
                
                _logger.LogError("Failed to reset TCP/IP: {Errors}", string.Join(", ", result.Errors));
                return false;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to reset TCP/IP");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> ResetWinsockAsync()
        {
            try
            {
                _logger.LogInformation("Resetting Winsock");

                var result = await _psExecutor.ExecuteCommandAsync("netsh winsock reset");
                
                if (result.Success)
                {
                    _logger.LogInformation("Winsock reset successfully");
                    return true;
                }
                
                _logger.LogError("Failed to reset Winsock: {Errors}", string.Join(", ", result.Errors));
                return false;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to reset Winsock");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> TestConnectivityAsync(string host = "8.8.8.8")
        {
            try
            {
                _logger.LogInformation("Testing connectivity to {Host}", host);

                using var ping = new Ping();
                var reply = await ping.SendPingAsync(host, 5000);
                
                var success = reply.Status == IPStatus.Success;
                _logger.LogInformation("Connectivity test: {Result}", success ? "Success" : "Failed");
                
                return success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Connectivity test failed");
                return false;
            }
        }

        private static string FormatMacAddress(PhysicalAddress address)
        {
            var bytes = address.GetAddressBytes();
            return string.Join(":", bytes.Select(b => b.ToString("X2")));
        }
    }
}
