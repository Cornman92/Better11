using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Better11.Core.Models;

namespace Better11.Core.Interfaces
{
    /// <summary>
    /// Interface for Windows Update management.
    /// </summary>
    public interface IUpdatesService
    {
        /// <summary>
        /// Gets available Windows updates.
        /// </summary>
        Task<List<WindowsUpdate>> GetAvailableUpdatesAsync();

        /// <summary>
        /// Installs specified or all available updates.
        /// </summary>
        Task<bool> InstallUpdatesAsync(List<string>? kbNumbers = null);

        /// <summary>
        /// Pauses Windows updates for specified days.
        /// </summary>
        Task<bool> SuspendUpdatesAsync(int days = 7);

        /// <summary>
        /// Resumes Windows updates.
        /// </summary>
        Task<bool> ResumeUpdatesAsync();

        /// <summary>
        /// Sets active hours for Windows Update.
        /// </summary>
        Task<bool> SetActiveHoursAsync(int startHour, int endHour);

        /// <summary>
        /// Gets current active hours settings.
        /// </summary>
        Task<(int Start, int End)> GetActiveHoursAsync();

        /// <summary>
        /// Gets Windows Update history.
        /// </summary>
        Task<List<UpdateHistoryEntry>> GetUpdateHistoryAsync(int days = 30);

        /// <summary>
        /// Uninstalls a Windows update by KB number.
        /// </summary>
        Task<bool> UninstallUpdateAsync(string kbNumber);

        /// <summary>
        /// Gets current Windows Update settings.
        /// </summary>
        Task<UpdateSettings> GetUpdateSettingsAsync();
    }
}
