using System;
using System.Collections.Generic;

namespace Better11.Core.Models
{
    /// <summary>
    /// Complete system information summary.
    /// </summary>
    public class SystemSummary
    {
        public string ComputerName { get; set; } = string.Empty;
        public string Domain { get; set; } = string.Empty;
        public string Manufacturer { get; set; } = string.Empty;
        public string Model { get; set; } = string.Empty;
        public string SystemType { get; set; } = string.Empty;
        public WindowsInfo? Windows { get; set; }
        public CPUInfo? CPU { get; set; }
        public MemoryInfo? Memory { get; set; }
        public List<GPUInfo> GPUs { get; set; } = new();
        public List<StorageInfo> Storage { get; set; } = new();
        public List<NetworkAdapterInfo> Network { get; set; } = new();
        public BIOSInfo? BIOS { get; set; }
    }

    /// <summary>
    /// Windows version information.
    /// </summary>
    public class WindowsInfo
    {
        public string Version { get; set; } = string.Empty;
        public string Build { get; set; } = string.Empty;
        public string Edition { get; set; } = string.Empty;
        public string ProductId { get; set; } = string.Empty;
        public DateTime InstallDate { get; set; }
        public DateTime LastBoot { get; set; }
        public double UptimeHours { get; set; }
        public string RegisteredOwner { get; set; } = string.Empty;
        public string SystemRoot { get; set; } = string.Empty;
        public string Architecture { get; set; } = string.Empty;
    }

    /// <summary>
    /// CPU information.
    /// </summary>
    public class CPUInfo
    {
        public string Name { get; set; } = string.Empty;
        public string Manufacturer { get; set; } = string.Empty;
        public int Cores { get; set; }
        public int LogicalProcessors { get; set; }
        public int MaxClockMHz { get; set; }
        public string Architecture { get; set; } = string.Empty;
        public int? CurrentUsage { get; set; }
        public int? L2CacheKB { get; set; }
        public int? L3CacheKB { get; set; }
    }

    /// <summary>
    /// Memory information.
    /// </summary>
    public class MemoryInfo
    {
        public double TotalGB { get; set; }
        public double AvailableGB { get; set; }
        public double UsedGB { get; set; }
        public double UsagePercent { get; set; }
        public int SlotsUsed { get; set; }
        public int SlotsTotal { get; set; }
        public int? SpeedMHz { get; set; }
        public string? Type { get; set; }
    }

    /// <summary>
    /// GPU information.
    /// </summary>
    public class GPUInfo
    {
        public string Name { get; set; } = string.Empty;
        public string Manufacturer { get; set; } = string.Empty;
        public string DriverVersion { get; set; } = string.Empty;
        public DateTime? DriverDate { get; set; }
        public int VideoMemoryMB { get; set; }
        public string CurrentResolution { get; set; } = string.Empty;
        public int? RefreshRate { get; set; }
        public string Status { get; set; } = string.Empty;
    }

    /// <summary>
    /// Storage device information.
    /// </summary>
    public class StorageInfo
    {
        public string Name { get; set; } = string.Empty;
        public string Model { get; set; } = string.Empty;
        public string MediaType { get; set; } = string.Empty;
        public double SizeGB { get; set; }
        public string InterfaceType { get; set; } = string.Empty;
        public string Status { get; set; } = string.Empty;
        public int Partitions { get; set; }
        public string? SerialNumber { get; set; }
    }

    /// <summary>
    /// Network adapter information.
    /// </summary>
    public class NetworkAdapterInfo
    {
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public string MacAddress { get; set; } = string.Empty;
        public string Status { get; set; } = string.Empty;
        public int SpeedMbps { get; set; }
        public List<string> IPAddresses { get; set; } = new();
        public string? Gateway { get; set; }
        public string MediaType { get; set; } = string.Empty;
    }

    /// <summary>
    /// BIOS/UEFI information.
    /// </summary>
    public class BIOSInfo
    {
        public string Manufacturer { get; set; } = string.Empty;
        public string Version { get; set; } = string.Empty;
        public DateTime? ReleaseDate { get; set; }
        public string? SerialNumber { get; set; }
        public bool IsUEFI { get; set; }
        public string SMBIOSVersion { get; set; } = string.Empty;
    }

    /// <summary>
    /// Current resource usage.
    /// </summary>
    public class ResourceUsage
    {
        public double CPUUsagePercent { get; set; }
        public double MemoryUsedGB { get; set; }
        public double MemoryTotalGB { get; set; }
        public double MemoryUsedPercent { get; set; }
        public List<DiskUsage> Disks { get; set; } = new();
        public DateTime Timestamp { get; set; }
    }

    /// <summary>
    /// Disk usage information.
    /// </summary>
    public class DiskUsage
    {
        public string Drive { get; set; } = string.Empty;
        public double TotalGB { get; set; }
        public double FreeGB { get; set; }
        public double UsedPercent { get; set; }
    }
}
