using System.Collections.Generic;
using System.Threading.Tasks;
using Better11.Core.Models;

namespace Better11.Core.Interfaces
{
    /// <summary>
    /// Service for backup and restore operations.
    /// </summary>
    public interface IBackupService
    {
        /// <summary>
        /// Lists all restore points.
        /// </summary>
        Task<List<RestorePoint>> ListRestorePointsAsync();

        /// <summary>
        /// Creates a new restore point.
        /// </summary>
        Task<RestorePoint?> CreateRestorePointAsync(string description);

        /// <summary>
        /// Restores to a specific restore point.
        /// </summary>
        Task<bool> RestoreToPointAsync(int sequenceNumber);

        /// <summary>
        /// Backs up registry hive.
        /// </summary>
        Task<BackupResult> BackupRegistryAsync(string keyPath, string outputPath);

        /// <summary>
        /// Restores registry from backup.
        /// </summary>
        Task<bool> RestoreRegistryAsync(string backupPath);

        /// <summary>
        /// Exports Better11 settings.
        /// </summary>
        Task<string> ExportSettingsAsync(string outputPath);

        /// <summary>
        /// Imports Better11 settings.
        /// </summary>
        Task<bool> ImportSettingsAsync(string settingsPath);
    }
}
