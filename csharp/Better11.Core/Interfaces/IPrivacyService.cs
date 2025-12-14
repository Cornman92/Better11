using System;
using System.Threading.Tasks;
using Better11.Core.Models;

namespace Better11.Core.Interfaces
{
    /// <summary>
    /// Interface for privacy and telemetry management.
    /// </summary>
    public interface IPrivacyService
    {
        /// <summary>
        /// Gets the current privacy status.
        /// </summary>
        /// <returns>Privacy status information.</returns>
        Task<PrivacyStatus> GetPrivacyStatusAsync();

        /// <summary>
        /// Gets the current telemetry level.
        /// </summary>
        /// <returns>Current telemetry level.</returns>
        Task<TelemetryLevel> GetTelemetryLevelAsync();

        /// <summary>
        /// Sets the telemetry level.
        /// </summary>
        /// <param name="level">Desired telemetry level.</param>
        /// <returns>True if successful.</returns>
        Task<bool> SetTelemetryLevelAsync(TelemetryLevel level);

        /// <summary>
        /// Enables or disables Cortana.
        /// </summary>
        /// <param name="enabled">Whether to enable Cortana.</param>
        /// <returns>True if successful.</returns>
        Task<bool> SetCortanaEnabledAsync(bool enabled);

        /// <summary>
        /// Enables or disables location services.
        /// </summary>
        /// <param name="enabled">Whether to enable location services.</param>
        /// <returns>True if successful.</returns>
        Task<bool> SetLocationEnabledAsync(bool enabled);

        /// <summary>
        /// Enables or disables advertising ID.
        /// </summary>
        /// <param name="enabled">Whether to enable advertising ID.</param>
        /// <returns>True if successful.</returns>
        Task<bool> SetAdvertisingIdEnabledAsync(bool enabled);

        /// <summary>
        /// Enables or disables activity history.
        /// </summary>
        /// <param name="enabled">Whether to enable activity history.</param>
        /// <returns>True if successful.</returns>
        Task<bool> SetActivityHistoryEnabledAsync(bool enabled);

        /// <summary>
        /// Applies recommended privacy settings.
        /// </summary>
        /// <returns>True if successful.</returns>
        Task<bool> ApplyRecommendedSettingsAsync();
    }
}
