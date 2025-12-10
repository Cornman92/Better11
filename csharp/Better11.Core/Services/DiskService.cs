using System;
using System.Collections.Generic;
using System.Linq;
using System.Management.Automation;
using System.Threading.Tasks;
using Better11.Core.Interfaces;
using Better11.Core.Models;
using Better11.Core.PowerShell;
using Microsoft.Extensions.Logging;

namespace Better11.Core.Services
{
    /// <summary>
    /// Service for disk management operations.
    /// Communicates with PowerShell backend to perform disk operations.
    /// </summary>
    public class DiskService : IDiskService
    {
        private readonly PowerShellExecutor _psExecutor;
        private readonly ILogger<DiskService> _logger;

        public DiskService(PowerShellExecutor psExecutor, ILogger<DiskService> logger)
        {
            _psExecutor = psExecutor;
            _logger = logger;
        }

        /// <inheritdoc/>
        public async Task<Dictionary<string, DiskInfo>> AnalyzeDiskSpaceAsync()
        {
            try
            {
                _logger.LogInformation("Analyzing disk space for all drives");

                var result = await _psExecutor.ExecuteCommandAsync("Get-Better11DiskSpace");

                if (!result.Success)
                {
                    throw new InvalidOperationException(
                        $"Failed to analyze disk space: {string.Join(", ", result.Errors)}");
                }

                var disks = new Dictionary<string, DiskInfo>();

                foreach (var item in result.Output)
                {
                    var psObj = item as PSObject;
                    if (psObj == null) continue;

                    var driveLetter = psObj.Properties["DriveLetter"]?.Value?.ToString() ?? string.Empty;

                    disks[driveLetter] = new DiskInfo
                    {
                        DriveLetter = driveLetter,
                        Label = psObj.Properties["Label"]?.Value?.ToString() ?? string.Empty,
                        FileSystem = psObj.Properties["FileSystem"]?.Value?.ToString() ?? string.Empty,
                        DriveType = ParseDriveType(psObj.Properties["DriveType"]?.Value?.ToString() ?? "Unknown"),
                        TotalBytes = Convert.ToInt64((double)(psObj.Properties["TotalGB"]?.Value ?? 0.0) * 1024 * 1024 * 1024),
                        UsedBytes = Convert.ToInt64((double)(psObj.Properties["UsedGB"]?.Value ?? 0.0) * 1024 * 1024 * 1024),
                        FreeBytes = Convert.ToInt64((double)(psObj.Properties["FreeGB"]?.Value ?? 0.0) * 1024 * 1024 * 1024)
                    };
                }

                _logger.LogInformation("Retrieved disk space for {Count} drive(s)", disks.Count);
                return disks;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to analyze disk space");
                throw;
            }
        }

        /// <inheritdoc/>
        public async Task<DiskInfo?> AnalyzeDiskSpaceAsync(string driveLetter)
        {
            try
            {
                _logger.LogInformation("Analyzing disk space for drive {Drive}", driveLetter);

                var parameters = new Dictionary<string, object>
                {
                    { "DriveLetter", driveLetter.TrimEnd(':') }
                };

                var result = await _psExecutor.ExecuteCommandAsync("Get-Better11DiskSpace", parameters);

                if (!result.Success || result.Output.Count == 0)
                {
                    return null;
                }

                var psObj = result.Output[0] as PSObject;
                if (psObj == null) return null;

                return new DiskInfo
                {
                    DriveLetter = psObj.Properties["DriveLetter"]?.Value?.ToString() ?? string.Empty,
                    Label = psObj.Properties["Label"]?.Value?.ToString() ?? string.Empty,
                    FileSystem = psObj.Properties["FileSystem"]?.Value?.ToString() ?? string.Empty,
                    DriveType = ParseDriveType(psObj.Properties["DriveType"]?.Value?.ToString() ?? "Unknown"),
                    TotalBytes = Convert.ToInt64((double)(psObj.Properties["TotalGB"]?.Value ?? 0.0) * 1024 * 1024 * 1024),
                    UsedBytes = Convert.ToInt64((double)(psObj.Properties["UsedGB"]?.Value ?? 0.0) * 1024 * 1024 * 1024),
                    FreeBytes = Convert.ToInt64((double)(psObj.Properties["FreeGB"]?.Value ?? 0.0) * 1024 * 1024 * 1024)
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to analyze disk space for drive {Drive}", driveLetter);
                throw;
            }
        }

        /// <inheritdoc/>
        public async Task<CleanupResult> CleanupTempFilesAsync(int ageDays = 7)
        {
            try
            {
                _logger.LogInformation("Cleaning temporary files older than {Days} days", ageDays);

                var parameters = new Dictionary<string, object>
                {
                    { "AgeDays", ageDays }
                };

                var result = await _psExecutor.ExecuteCommandAsync("Clear-Better11TempFiles", parameters);

                if (!result.Success)
                {
                    throw new InvalidOperationException(
                        $"Failed to clean temporary files: {string.Join(", ", result.Errors)}");
                }

                if (result.Output.Count == 0)
                {
                    return new CleanupResult();
                }

                var psObj = result.Output[0] as PSObject;
                if (psObj == null) return new CleanupResult();

                var locations = new List<string>();
                var locationsObj = psObj.Properties["LocationsCleaned"]?.Value;
                if (locationsObj is IEnumerable<object> enumerable)
                {
                    locations = enumerable.Select(o => o.ToString() ?? string.Empty).ToList();
                }

                return new CleanupResult
                {
                    LocationsCleaned = locations,
                    FilesRemoved = Convert.ToInt32(psObj.Properties["FilesRemoved"]?.Value ?? 0),
                    SpaceFreedBytes = Convert.ToInt64((double)(psObj.Properties["SpaceFreedMB"]?.Value ?? 0.0) * 1024 * 1024)
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to clean temporary files");
                throw;
            }
        }

        private DriveType ParseDriveType(string typeString)
        {
            return typeString.ToLowerInvariant() switch
            {
                "hdd" or "local disk" => DriveType.HDD,
                "ssd" => DriveType.SSD,
                "removable" => DriveType.Removable,
                "network" => DriveType.Network,
                _ => DriveType.Unknown
            };
        }
    }
}
