using System.Threading.Tasks;
using Better11.Core.Models;

namespace Better11.Core.Interfaces
{
    /// <summary>
    /// Interface for system performance optimization.
    /// </summary>
    public interface IPerformanceService
    {
        /// <summary>
        /// Gets current performance settings.
        /// </summary>
        Task<PerformanceSettings> GetPerformanceSettingsAsync();

        /// <summary>
        /// Sets visual effects preset.
        /// </summary>
        Task<bool> SetVisualEffectsAsync(VisualEffectsPreset preset);

        /// <summary>
        /// Sets processor scheduling priority.
        /// </summary>
        Task<bool> SetProcessorSchedulingAsync(ProcessorPriority priority);

        /// <summary>
        /// Configures virtual memory settings.
        /// </summary>
        Task<bool> SetVirtualMemoryAsync(VirtualMemorySettings settings);

        /// <summary>
        /// Enables Windows Fast Startup.
        /// </summary>
        Task<bool> EnableFastStartupAsync();

        /// <summary>
        /// Disables Windows Fast Startup.
        /// </summary>
        Task<bool> DisableFastStartupAsync();

        /// <summary>
        /// Sets system responsiveness level.
        /// </summary>
        Task<bool> SetSystemResponsivenessAsync(int reservedPercent);

        /// <summary>
        /// Applies a performance optimization preset.
        /// </summary>
        Task<bool> ApplyPerformancePresetAsync(PerformancePreset preset);

        /// <summary>
        /// Gets current resource usage.
        /// </summary>
        Task<ResourceUsage> GetResourceUsageAsync();
    }
}
