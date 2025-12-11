using System;
using System.Collections.Generic;

namespace Better11.Core.Models
{
    /// <summary>
    /// Represents a network adapter.
    /// </summary>
    public class NetworkAdapter
    {
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public string MacAddress { get; set; } = string.Empty;
        public AdapterStatus Status { get; set; }
        public string? IPv4Address { get; set; }
        public string? IPv4Subnet { get; set; }
        public string? IPv4Gateway { get; set; }
        public List<string>? DnsServers { get; set; }
        public bool DhcpEnabled { get; set; } = true;
    }

    /// <summary>
    /// Network adapter status.
    /// </summary>
    public enum AdapterStatus
    {
        Up,
        Down,
        Unknown
    }

    /// <summary>
    /// DNS configuration.
    /// </summary>
    public class DNSConfiguration
    {
        public string Primary { get; set; } = string.Empty;
        public string? Secondary { get; set; }
        public string? Tertiary { get; set; }

        // Predefined DNS providers
        public static DNSConfiguration GoogleDNS => new()
        {
            Primary = "8.8.8.8",
            Secondary = "8.8.4.4"
        };

        public static DNSConfiguration CloudflareDNS => new()
        {
            Primary = "1.1.1.1",
            Secondary = "1.0.0.1"
        };

        public static DNSConfiguration Quad9DNS => new()
        {
            Primary = "9.9.9.9",
            Secondary = "149.112.112.112"
        };

        public static DNSConfiguration OpenDNS => new()
        {
            Primary = "208.67.222.222",
            Secondary = "208.67.220.220"
        };
    }
}
