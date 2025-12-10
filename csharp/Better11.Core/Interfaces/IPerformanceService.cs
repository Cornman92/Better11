using System.Collections.Generic;
using System.Threading.Tasks;

namespace Better11.Core.Interfaces
{
    /// <summary>
    /// Interface for performance monitoring and optimization.
    /// </summary>
    public interface IPerformanceService
    {
        /// <summary>
        /// Gets comprehensive system information.
        /// </summary>
        Task<SystemInfo> GetSystemInfoAsync();

        /// <summary>
        /// Gets current performance metrics.
        /// </summary>
        Task<PerformanceMetrics> GetPerformanceMetricsAsync(int sampleInterval = 1);

        /// <summary>
        /// Optimizes system performance.
        /// </summary>
        Task<OptimizationResult> OptimizePerformanceAsync(OptimizationLevel level, bool force = false);

        /// <summary>
        /// Gets startup program impact analysis.
        /// </summary>
        Task<List<StartupItem>> GetStartupImpactAsync();

        /// <summary>
        /// Performs system health check.
        /// </summary>
        Task<HealthReport> TestSystemHealthAsync();
    }

    public enum OptimizationLevel
    {
        Light,
        Moderate,
        Aggressive
    }

    public class SystemInfo
    {
        public string ComputerName { get; set; } = string.Empty;
        public string Manufacturer { get; set; } = string.Empty;
        public string Model { get; set; } = string.Empty;
        public string OSName { get; set; } = string.Empty;
        public string OSVersion { get; set; } = string.Empty;
        public string Architecture { get; set; } = string.Empty;
        public double TotalMemoryGB { get; set; }
        public string CPUName { get; set; } = string.Empty;
        public int CPUCores { get; set; }
        public double DiskTotalGB { get; set; }
        public double DiskFreeGB { get; set; }
        public double DiskUsedPercent { get; set; }
    }

    public class PerformanceMetrics
    {
        public System.DateTime Timestamp { get; set; }
        public double CPUUsagePercent { get; set; }
        public double MemoryUsagePercent { get; set; }
        public double MemoryUsedMB { get; set; }
        public double MemoryFreeMB { get; set; }
        public double DiskUsagePercent { get; set; }
        public int ProcessCount { get; set; }
    }

    public class OptimizationResult
    {
        public bool Success { get; set; }
        public string Message { get; set; } = string.Empty;
        public OptimizationLevel Level { get; set; }
        public List<string> OptimizationsApplied { get; set; } = new();
        public double SpaceFreedMB { get; set; }
    }

    public class StartupItem
    {
        public string Name { get; set; } = string.Empty;
        public string Command { get; set; } = string.Empty;
        public string Location { get; set; } = string.Empty;
        public string Type { get; set; } = string.Empty;
        public string EstimatedImpact { get; set; } = string.Empty;
    }

    public class HealthReport
    {
        public System.DateTime Timestamp { get; set; }
        public string OverallStatus { get; set; } = string.Empty;
        public List<HealthCheck> Checks { get; set; } = new();
        public List<string> Warnings { get; set; } = new();
        public List<string> Recommendations { get; set; } = new();
    }

    public class HealthCheck
    {
        public string Name { get; set; } = string.Empty;
        public string Status { get; set; } = string.Empty;
        public string Value { get; set; } = string.Empty;
    }
}
