using System.Collections.Generic;
using System.Threading.Tasks;
using Better11.Core.Models;

namespace Better11.Core.Interfaces
{
    /// <summary>
    /// Interface for driver management.
    /// </summary>
    public interface IDriversService
    {
        /// <summary>
        /// Gets installed drivers.
        /// </summary>
        Task<List<DriverInfo>> GetDriversAsync(string? category = null);

        /// <summary>
        /// Gets devices with driver issues.
        /// </summary>
        Task<List<DriverIssue>> GetDriverIssuesAsync();

        /// <summary>
        /// Backs up installed drivers.
        /// </summary>
        Task<DriverBackupResult> BackupDriversAsync(string? path = null);

        /// <summary>
        /// Updates a device driver.
        /// </summary>
        Task<bool> UpdateDriverAsync(string deviceId, string? infPath = null);

        /// <summary>
        /// Exports driver list to file.
        /// </summary>
        Task<string> ExportDriverListAsync(string? path = null, string format = "JSON");
    }
}
