using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Better11.Core.Models;

namespace Better11.Core.Interfaces
{
    /// <summary>
    /// Interface for disk management operations.
    /// </summary>
    public interface IDiskService
    {
        /// <summary>
        /// Analyzes disk space for all available drives.
        /// </summary>
        /// <returns>Dictionary mapping drive letters to disk information.</returns>
        Task<Dictionary<string, DiskInfo>> AnalyzeDiskSpaceAsync();

        /// <summary>
        /// Analyzes disk space for a specific drive.
        /// </summary>
        /// <param name="driveLetter">Drive letter to analyze.</param>
        /// <returns>Disk information for the specified drive.</returns>
        Task<DiskInfo?> AnalyzeDiskSpaceAsync(string driveLetter);

        /// <summary>
        /// Cleans temporary files older than the specified number of days.
        /// </summary>
        /// <param name="ageDays">Delete files older than this many days.</param>
        /// <returns>Cleanup result with statistics.</returns>
        Task<CleanupResult> CleanupTempFilesAsync(int ageDays = 7);
    }
}
