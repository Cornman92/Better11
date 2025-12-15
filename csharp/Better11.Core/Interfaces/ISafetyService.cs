using System.Collections.Generic;
using System.Threading.Tasks;
using Better11.Core.Models;

namespace Better11.Core.Interfaces
{
    /// <summary>
    /// Interface for system safety and backup operations.
    /// </summary>
    public interface ISafetyService
    {
        /// <summary>
        /// Creates a system restore point.
        /// </summary>
        Task<bool> CreateRestorePointAsync(string description);

        /// <summary>
        /// Gets available restore points.
        /// </summary>
        Task<List<RestorePoint>> GetRestorePointsAsync();

        /// <summary>
        /// Checks if current user has administrator privileges.
        /// </summary>
        Task<bool> IsAdministratorAsync();

        /// <summary>
        /// Backs up a registry key to file.
        /// </summary>
        Task<RegistryBackupResult> BackupRegistryKeyAsync(string keyPath, string? outputPath = null);

        /// <summary>
        /// Restores a registry key from backup file.
        /// </summary>
        Task<bool> RestoreRegistryKeyAsync(string backupFilePath);

        /// <summary>
        /// Performs a safety check before an operation.
        /// </summary>
        Task<SafetyOperationResult> PerformSafeOperationAsync(
            string operationName,
            bool createRestorePoint = false,
            string? registryKeyToBackup = null);
    }
}
