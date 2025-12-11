using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Better11.Core.Models;

namespace Better11.Core.Interfaces
{
    /// <summary>
    /// Interface for network management operations.
    /// </summary>
    public interface INetworkService
    {
        /// <summary>
        /// Lists all network adapters.
        /// </summary>
        /// <returns>List of network adapters.</returns>
        Task<List<NetworkAdapter>> ListAdaptersAsync();

        /// <summary>
        /// Configures DNS servers for a network adapter.
        /// </summary>
        /// <param name="adapterName">Name of the adapter.</param>
        /// <param name="dnsConfig">DNS configuration.</param>
        /// <returns>True if successful.</returns>
        Task<bool> ConfigureDNSAsync(string adapterName, DNSConfiguration dnsConfig);

        /// <summary>
        /// Flushes the DNS resolver cache.
        /// </summary>
        /// <returns>True if successful.</returns>
        Task<bool> FlushDNSCacheAsync();

        /// <summary>
        /// Resets the TCP/IP stack.
        /// </summary>
        /// <returns>True if successful.</returns>
        Task<bool> ResetTcpIpAsync();

        /// <summary>
        /// Resets the Winsock catalog.
        /// </summary>
        /// <returns>True if successful.</returns>
        Task<bool> ResetWinsockAsync();

        /// <summary>
        /// Tests network connectivity to a host.
        /// </summary>
        /// <param name="host">Host to test.</param>
        /// <returns>True if host is reachable.</returns>
        Task<bool> TestConnectivityAsync(string host = "8.8.8.8");
    }
}
