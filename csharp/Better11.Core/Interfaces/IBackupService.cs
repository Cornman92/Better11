using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Better11.Core.Models;

namespace Better11.Core.Interfaces
{
    /// <summary>
    /// Interface for backup and restore operations.
    /// </summary>
    public interface IBackupService
    {
        /// <summary>
        /// Lists all available system restore points.
        /// </summary>
        /// <returns>List of restore points.</returns>
        Task<List<RestorePoint>> ListRestorePointsAsync();

        /// <summary>
        /// Creates a new system restore point.
        /// </summary>
        /// <param name="description">Description for the restore point.</param>
        /// <returns>Created restore point, or null if failed.</returns>
        Task<RestorePoint?> CreateRestorePointAsync(string description);

        /// <summary>
        /// Exports Better11 settings.
        /// </summary>
        /// <param name="outputPath">Path to export settings to.</param>
        /// <returns>Backup result.</returns>
        Task<BackupResult> ExportSettingsAsync(string outputPath);

        /// <summary>
        /// Imports Better11 settings.
        /// </summary>
        /// <param name="inputPath">Path to import settings from.</param>
        /// <returns>True if successful.</returns>
        Task<bool> ImportSettingsAsync(string inputPath);

        /// <summary>
        /// Backs up registry keys before modification.
        /// </summary>
        /// <param name="keyPaths">Registry key paths to backup.</param>
        /// <param name="outputPath">Path to save backup.</param>
        /// <returns>Backup result.</returns>
        Task<BackupResult> BackupRegistryAsync(IEnumerable<string> keyPaths, string outputPath);
    }
}
