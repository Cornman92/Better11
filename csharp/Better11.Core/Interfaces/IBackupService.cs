using System.Collections.Generic;
using System.Threading.Tasks;

namespace Better11.Core.Interfaces
{
    /// <summary>
    /// Interface for backup and restore operations.
    /// </summary>
    public interface IBackupService
    {
        /// <summary>
        /// Creates a new system backup.
        /// </summary>
        Task<BackupResult> CreateBackupAsync(string description, bool includeRegistry = true, bool includeApps = true);

        /// <summary>
        /// Restores from a backup.
        /// </summary>
        Task<BackupResult> RestoreBackupAsync(string backupPath, bool restoreRegistry = true, bool force = false);

        /// <summary>
        /// Gets list of available backups.
        /// </summary>
        Task<List<BackupInfo>> GetBackupListAsync();

        /// <summary>
        /// Removes a backup.
        /// </summary>
        Task<BackupResult> RemoveBackupAsync(string backupPath, bool force = false);

        /// <summary>
        /// Exports configuration to file.
        /// </summary>
        Task<BackupResult> ExportConfigurationAsync(string outputPath);

        /// <summary>
        /// Imports configuration from file.
        /// </summary>
        Task<BackupResult> ImportConfigurationAsync(string configPath, bool installApps = false);
    }

    public class BackupResult
    {
        public bool Success { get; set; }
        public string Message { get; set; } = string.Empty;
        public string BackupPath { get; set; } = string.Empty;
        public List<string> Components { get; set; } = new();
    }

    public class BackupInfo
    {
        public string BackupName { get; set; } = string.Empty;
        public string Timestamp { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public string ComputerName { get; set; } = string.Empty;
        public List<string> Components { get; set; } = new();
        public string Path { get; set; } = string.Empty;
        public long SizeBytes { get; set; }
    }
}
