using System.Collections.Generic;
using System.Threading.Tasks;
using Better11.Core.Models;

namespace Better11.Core.Interfaces
{
    /// <summary>
    /// Service for system optimization and tweaks.
    /// </summary>
    public interface ISystemToolsService
    {
        /// <summary>
        /// Applies registry tweaks with automatic backup.
        /// </summary>
        Task<TweakResult> ApplyRegistryTweaksAsync(List<RegistryTweak> tweaks, bool force = false);

        /// <summary>
        /// Removes bloatware applications.
        /// </summary>
        Task<RemovalResult> RemoveBloatwareAsync(List<string> packageNames, bool force = false);

        /// <summary>
        /// Manages Windows services.
        /// </summary>
        Task<ServiceResult> ManageServiceAsync(ServiceAction action);

        /// <summary>
        /// Applies a performance preset.
        /// </summary>
        Task<PresetResult> ApplyPerformancePresetAsync(string presetName, bool force = false);

        /// <summary>
        /// Lists available performance presets.
        /// </summary>
        Task<List<PerformancePreset>> ListPerformancePresetsAsync();

        /// <summary>
        /// Creates a system restore point.
        /// </summary>
        Task<bool> CreateRestorePointAsync(string description);
    }
}
