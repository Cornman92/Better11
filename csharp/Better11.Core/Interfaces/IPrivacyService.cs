using System.Collections.Generic;
using System.Threading.Tasks;
using Better11.Core.Models;

namespace Better11.Core.Interfaces
{
    /// <summary>
    /// Service for managing privacy and telemetry settings.
    /// </summary>
    public interface IPrivacyService
    {
        /// <summary>
        /// Gets the current telemetry level.
        /// </summary>
        Task<TelemetryLevel> GetTelemetryLevelAsync();

        /// <summary>
        /// Sets the telemetry level.
        /// </summary>
        Task<bool> SetTelemetryLevelAsync(TelemetryLevel level, bool force = false);

        /// <summary>
        /// Disables Cortana.
        /// </summary>
        Task<bool> DisableCortanaAsync(bool force = false);

        /// <summary>
        /// Enables/disables Windows feedback.
        /// </summary>
        Task<bool> SetWindowsFeedbackAsync(bool enabled);

        /// <summary>
        /// Gets all privacy settings.
        /// </summary>
        Task<List<PrivacySetting>> GetPrivacySettingsAsync();

        /// <summary>
        /// Applies privacy settings.
        /// </summary>
        Task<PrivacyResult> ApplyPrivacySettingsAsync(List<PrivacySetting> settings, bool force = false);
    }
}
