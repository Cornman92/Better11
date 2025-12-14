using System.Collections.Generic;
using System.Threading.Tasks;
using Better11.Core.Models;

namespace Better11.Core.Interfaces
{
    /// <summary>
    /// Service for managing Windows optional features.
    /// </summary>
    public interface IFeaturesService
    {
        /// <summary>
        /// Lists all available Windows features.
        /// </summary>
        Task<List<WindowsFeature>> ListFeaturesAsync();

        /// <summary>
        /// Enables a Windows feature.
        /// </summary>
        Task<FeatureResult> EnableFeatureAsync(string featureName, bool force = false);

        /// <summary>
        /// Disables a Windows feature.
        /// </summary>
        Task<FeatureResult> DisableFeatureAsync(string featureName, bool force = false);

        /// <summary>
        /// Gets the status of a specific feature.
        /// </summary>
        Task<WindowsFeature?> GetFeatureStatusAsync(string featureName);
    }
}
