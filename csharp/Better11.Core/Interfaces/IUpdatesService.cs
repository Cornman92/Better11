using System.Collections.Generic;
using System.Threading.Tasks;
using Better11.Core.Models;

namespace Better11.Core.Interfaces
{
    /// <summary>
    /// Interface for managing Windows Updates.
    /// </summary>
    public interface IUpdatesService
    {
        /// <summary>
        /// Gets available Windows Updates.
        /// </summary>
        /// <param name="includeOptional">Whether to include optional updates.</param>
        /// <returns>Operation result with available updates.</returns>
        Task<UpdateOperationResult> GetUpdatesAsync(bool includeOptional = false);

        /// <summary>
        /// Checks for new Windows Updates.
        /// </summary>
        /// <returns>Operation result with found updates.</returns>
        Task<UpdateOperationResult> CheckForUpdatesAsync();

        /// <summary>
        /// Installs specific Windows Updates.
        /// </summary>
        /// <param name="updateIds">List of update IDs to install.</param>
        /// <returns>Operation result with installation status.</returns>
        Task<UpdateOperationResult> InstallUpdatesAsync(List<string> updateIds);

        /// <summary>
        /// Pauses Windows Updates for a specified number of days.
        /// </summary>
        /// <param name="days">Number of days to pause (1-35).</param>
        /// <param name="confirm">Whether to show confirmation prompt.</param>
        /// <returns>Operation result.</returns>
        Task<UpdateOperationResult> PauseUpdatesAsync(int days, bool confirm = true);

        /// <summary>
        /// Resumes Windows Updates.
        /// </summary>
        /// <param name="confirm">Whether to show confirmation prompt.</param>
        /// <returns>Operation result.</returns>
        Task<UpdateOperationResult> ResumeUpdatesAsync(bool confirm = true);

        /// <summary>
        /// Gets the current Windows Update service status.
        /// </summary>
        /// <returns>Update service status information.</returns>
        Task<UpdateServiceStatus> GetUpdateStatusAsync();

        /// <summary>
        /// Hides a specific Windows Update.
        /// </summary>
        /// <param name="updateId">The update ID to hide.</param>
        /// <returns>Operation result.</returns>
        Task<UpdateOperationResult> HideUpdateAsync(string updateId);

        /// <summary>
        /// Shows a previously hidden Windows Update.
        /// </summary>
        /// <param name="updateId">The update ID to show.</param>
        /// <returns>Operation result.</returns>
        Task<UpdateOperationResult> ShowUpdateAsync(string updateId);

        /// <summary>
        /// Gets the Windows Update history.
        /// </summary>
        /// <param name="maxResults">Maximum number of results to return.</param>
        /// <returns>List of update history items.</returns>
        Task<List<WindowsUpdate>> GetUpdateHistoryAsync(int maxResults = 50);
    }
}
