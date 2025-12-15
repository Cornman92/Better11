using System.Threading.Tasks;
using Better11.Core.Models;

namespace Better11.Core.Interfaces
{
    /// <summary>
    /// Interface for system information gathering.
    /// </summary>
    public interface ISysInfoService
    {
        /// <summary>
        /// Gets a complete system summary.
        /// </summary>
        Task<SystemSummary> GetSystemSummaryAsync();

        /// <summary>
        /// Gets Windows version information.
        /// </summary>
        Task<WindowsInfo> GetWindowsInfoAsync();

        /// <summary>
        /// Gets CPU information.
        /// </summary>
        Task<CPUInfo> GetCPUInfoAsync();

        /// <summary>
        /// Gets memory information.
        /// </summary>
        Task<MemoryInfo> GetMemoryInfoAsync();

        /// <summary>
        /// Gets GPU information.
        /// </summary>
        Task<System.Collections.Generic.List<GPUInfo>> GetGPUInfoAsync();

        /// <summary>
        /// Gets storage information.
        /// </summary>
        Task<System.Collections.Generic.List<StorageInfo>> GetStorageInfoAsync();

        /// <summary>
        /// Gets BIOS information.
        /// </summary>
        Task<BIOSInfo> GetBIOSInfoAsync();

        /// <summary>
        /// Gets current resource usage.
        /// </summary>
        Task<ResourceUsage> GetResourceUsageAsync();

        /// <summary>
        /// Exports system information to a file.
        /// </summary>
        Task<string> ExportSystemInfoAsync(string? path = null);
    }
}
