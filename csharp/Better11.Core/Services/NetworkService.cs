using System;
using System.Collections.Generic;
using System.Management.Automation;
using System.Threading.Tasks;
using Better11.Core.Interfaces;
using Better11.Core.Models;
using Better11.Core.PowerShell;
using Microsoft.Extensions.Logging;

namespace Better11.Core.Services
{
    public class NetworkService : INetworkService
    {
        private readonly PowerShellExecutor _psExecutor;
        private readonly ILogger<NetworkService> _logger;

        public NetworkService(PowerShellExecutor psExecutor, ILogger<NetworkService> logger)
        {
            _psExecutor = psExecutor;
            _logger = logger;
        }

        public async Task<List<NetworkAdapter>> ListNetworkAdaptersAsync()
        {
            try
            {
                var result = await _psExecutor.ExecuteCommandAsync("Get-Better11NetworkAdapters");

                var adapters = new List<NetworkAdapter>();
                foreach (var item in result.Output)
                {
                    var psObj = item as PSObject;
                    if (psObj == null) continue;

                    adapters.Add(new NetworkAdapter
                    {
                        Name = psObj.Properties["Name"]?.Value?.ToString() ?? string.Empty,
                        Description = psObj.Properties["Description"]?.Value?.ToString() ?? string.Empty,
                        Status = psObj.Properties["Status"]?.Value?.ToString() ?? string.Empty,
                        MACAddress = psObj.Properties["MACAddress"]?.Value?.ToString() ?? string.Empty
                    });
                }

                return adapters;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to list network adapters");
                throw;
            }
        }

        public async Task<bool> FlushDNSCacheAsync()
        {
            try
            {
                var result = await _psExecutor.ExecuteCommandAsync("Clear-Better11DNSCache");
                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to flush DNS cache");
                return false;
            }
        }

        public async Task<bool> ResetTcpIpAsync()
        {
            try
            {
                var result = await _psExecutor.ExecuteCommandAsync("Reset-Better11TcpIp");
                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to reset TCP/IP");
                return false;
            }
        }

        public async Task<bool> SetDNSServersAsync(string adapterName, List<string> dnsServers)
        {
            try
            {
                var parameters = new Dictionary<string, object>
                {
                    { "AdapterName", adapterName },
                    { "DNSServers", dnsServers }
                };

                var result = await _psExecutor.ExecuteCommandAsync("Set-Better11DNS", parameters);
                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to set DNS servers");
                return false;
            }
        }
    }
}
