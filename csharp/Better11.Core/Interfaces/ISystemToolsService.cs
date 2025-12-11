using System.Collections.Generic;
using System.Threading.Tasks;
using Better11.Core.Models;

namespace Better11.Core.Interfaces
{
    /// <summary>
    /// Interface for system tools service.
    /// </summary>
    public interface ISystemToolsService
    {
        /// <summary>
        /// Applies registry tweaks.
        /// </summary>
        Task<RegistryTweakResult> ApplyRegistryTweaksAsync(List<RegistryTweak> tweaks, bool force = false);

        /// <summary>
        /// Removes bloatware packages.
        /// </summary>
        Task<BloatwareRemovalResult> RemoveBloatwareAsync(List<string> packages, bool force = false);

        /// <summary>
        /// Applies privacy settings.
        /// </summary>
        Task<PrivacyResult> ApplyPrivacySettingsAsync(PrivacyPreset preset, bool force = false);

        /// <summary>
        /// Gets startup items.
        /// </summary>
        Task<List<StartupItem>> GetStartupItemsAsync();

        /// <summary>
        /// Manages a startup item.
        /// </summary>
        Task<bool> ManageStartupItemAsync(StartupItem item, bool enable);
    }

    public class BloatwareRemovalResult
    {
        public int TotalPackages { get; set; }
        public int RemovedSuccessfully { get; set; }
        public int Failed { get; set; }
        public bool Success => Failed == 0;
    }

    public class PrivacyResult
    {
        public string Preset { get; set; } = string.Empty;
        public int SettingsApplied { get; set; }
        public bool Success { get; set; }
    }

    public enum PrivacyPreset
    {
        MaximumPrivacy,
        Balanced,
        Default
    }

    public class StartupItem
    {
        public string Name { get; set; } = string.Empty;
        public string Command { get; set; } = string.Empty;
        public string Location { get; set; } = string.Empty;
        public bool Enabled { get; set; }
    }
}
