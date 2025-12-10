using System.Collections.Generic;
using System.Threading.Tasks;

namespace Better11.Core.Interfaces
{
    /// <summary>
    /// Interface for network configuration and diagnostics.
    /// </summary>
    public interface INetworkService
    {
        /// <summary>
        /// Gets detailed network adapter information.
        /// </summary>
        Task<List<NetworkAdapterInfo>> GetNetworkInfoAsync();

        /// <summary>
        /// Tests network connectivity and speed.
        /// </summary>
        Task<List<NetworkSpeedTest>> TestNetworkSpeedAsync(List<string> testHosts = null);

        /// <summary>
        /// Resets network configuration.
        /// </summary>
        Task<NetworkOperationResult> ResetNetworkAsync(bool force = false);

        /// <summary>
        /// Optimizes network settings.
        /// </summary>
        Task<NetworkOperationResult> OptimizeNetworkSettingsAsync(bool force = false);

        /// <summary>
        /// Gets active network connections.
        /// </summary>
        Task<List<NetworkConnection>> GetActiveConnectionsAsync(string protocol = "All", string state = "All");
    }

    public class NetworkAdapterInfo
    {
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public string Status { get; set; } = string.Empty;
        public string Speed { get; set; } = string.Empty;
        public string MacAddress { get; set; } = string.Empty;
        public string IPv4Address { get; set; } = string.Empty;
        public string IPv6Address { get; set; } = string.Empty;
        public string Gateway { get; set; } = string.Empty;
        public string DNSServers { get; set; } = string.Empty;
        public long BytesReceived { get; set; }
        public long BytesSent { get; set; }
    }

    public class NetworkSpeedTest
    {
        public string Host { get; set; } = string.Empty;
        public string Status { get; set; } = string.Empty;
        public double AverageLatencyMs { get; set; }
        public double MinLatencyMs { get; set; }
        public double MaxLatencyMs { get; set; }
        public double PacketLossPercent { get; set; }
    }

    public class NetworkOperationResult
    {
        public bool Success { get; set; }
        public string Message { get; set; } = string.Empty;
        public List<string> ActionsPerformed { get; set; } = new();
    }

    public class NetworkConnection
    {
        public string Protocol { get; set; } = string.Empty;
        public string LocalAddress { get; set; } = string.Empty;
        public int LocalPort { get; set; }
        public string RemoteAddress { get; set; } = string.Empty;
        public int RemotePort { get; set; }
        public string State { get; set; } = string.Empty;
        public int ProcessId { get; set; }
        public string ProcessName { get; set; } = string.Empty;
    }
}
