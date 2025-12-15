using System.Collections.Generic;
using System.Threading.Tasks;
using Better11.Core.Models;

namespace Better11.Core.Interfaces
{
    /// <summary>
    /// Interface for Windows optional features and capabilities management.
    /// </summary>
    public interface IFeaturesService
    {
        /// <summary>
        /// Gets all optional Windows features.
        /// </summary>
        Task<List<OptionalFeature>> GetOptionalFeaturesAsync(string? nameFilter = null);

        /// <summary>
        /// Enables a Windows optional feature.
        /// </summary>
        Task<bool> EnableOptionalFeatureAsync(string featureName, bool noRestart = true);

        /// <summary>
        /// Disables a Windows optional feature.
        /// </summary>
        Task<bool> DisableOptionalFeatureAsync(string featureName, bool noRestart = true);

        /// <summary>
        /// Gets installed Windows capabilities.
        /// </summary>
        Task<List<WindowsCapability>> GetCapabilitiesAsync(bool installedOnly = false);

        /// <summary>
        /// Adds a Windows capability.
        /// </summary>
        Task<bool> AddCapabilityAsync(string capabilityName);

        /// <summary>
        /// Removes a Windows capability.
        /// </summary>
        Task<bool> RemoveCapabilityAsync(string capabilityName);
    }
}
