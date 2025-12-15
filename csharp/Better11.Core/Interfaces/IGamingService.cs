using System.Threading.Tasks;
using Better11.Core.Models;

namespace Better11.Core.Interfaces
{
    /// <summary>
    /// Interface for gaming optimization management.
    /// </summary>
    public interface IGamingService
    {
        /// <summary>
        /// Gets current gaming optimization settings.
        /// </summary>
        Task<GamingSettings> GetGamingSettingsAsync();

        /// <summary>
        /// Enables or disables Windows Game Mode.
        /// </summary>
        Task<bool> SetGameModeAsync(bool enabled);

        /// <summary>
        /// Enables or disables Xbox Game Bar.
        /// </summary>
        Task<bool> SetGameBarAsync(bool enabled);

        /// <summary>
        /// Enables or disables hardware-accelerated GPU scheduling.
        /// </summary>
        Task<bool> SetGPUSchedulingAsync(bool enabled);

        /// <summary>
        /// Enables or disables mouse acceleration.
        /// </summary>
        Task<bool> SetMouseAccelerationAsync(bool enabled);

        /// <summary>
        /// Enables or disables Nagle's algorithm.
        /// </summary>
        Task<bool> SetNagleAlgorithmAsync(bool enabled);

        /// <summary>
        /// Activates high performance power plan for gaming.
        /// </summary>
        Task<bool> SetHighPerformancePowerAsync(bool ultimate = false);

        /// <summary>
        /// Applies a gaming optimization preset.
        /// </summary>
        Task<bool> ApplyGamingPresetAsync(GamingPreset preset);
    }
}
