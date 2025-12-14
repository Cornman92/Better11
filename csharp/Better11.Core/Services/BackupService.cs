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
    public class BackupService : IBackupService
    {
        private readonly PowerShellExecutor _psExecutor;
        private readonly ILogger<BackupService> _logger;

        public BackupService(PowerShellExecutor psExecutor, ILogger<BackupService> logger)
        {
            _psExecutor = psExecutor;
            _logger = logger;
        }

        public async Task<List<RestorePoint>> ListRestorePointsAsync()
        {
            try
            {
                var result = await _psExecutor.ExecuteCommandAsync("Get-Better11RestorePoints");

                var points = new List<RestorePoint>();
                foreach (var item in result.Output)
                {
                    var psObj = item as PSObject;
                    if (psObj == null) continue;

                    points.Add(new RestorePoint
                    {
                        SequenceNumber = Convert.ToInt32(psObj.Properties["SequenceNumber"]?.Value ?? 0),
                        Description = psObj.Properties["Description"]?.Value?.ToString() ?? string.Empty,
                        CreationTime = Convert.ToDateTime(psObj.Properties["CreationTime"]?.Value ?? DateTime.Now),
                        RestorePointType = psObj.Properties["RestorePointType"]?.Value?.ToString() ?? string.Empty
                    });
                }

                return points;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to list restore points");
                throw;
            }
        }

        public async Task<RestorePoint?> CreateRestorePointAsync(string description)
        {
            try
            {
                var parameters = new Dictionary<string, object> { { "Description", description } };
                var result = await _psExecutor.ExecuteCommandAsync("New-Better11RestorePoint", parameters);

                if (result.Success && result.Output.Count > 0)
                {
                    var psObj = result.Output[0] as PSObject;
                    return new RestorePoint
                    {
                        SequenceNumber = Convert.ToInt32(psObj?.Properties["SequenceNumber"]?.Value ?? 0),
                        Description = description,
                        CreationTime = DateTime.Now
                    };
                }

                return null;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to create restore point");
                return null;
            }
        }

        public async Task<bool> RestoreToPointAsync(int sequenceNumber)
        {
            try
            {
                var parameters = new Dictionary<string, object> { { "SequenceNumber", sequenceNumber } };
                var result = await _psExecutor.ExecuteCommandAsync("Restore-Better11ToPoint", parameters);
                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to restore to point: {Sequence}", sequenceNumber);
                return false;
            }
        }

        public async Task<BackupResult> BackupRegistryAsync(string keyPath, string outputPath)
        {
            try
            {
                var parameters = new Dictionary<string, object>
                {
                    { "KeyPath", keyPath },
                    { "OutputPath", outputPath }
                };

                var result = await _psExecutor.ExecuteCommandAsync("Backup-Better11Registry", parameters);

                if (!result.Success)
                {
                    return new BackupResult
                    {
                        Success = false,
                        ErrorMessage = string.Join("\n", result.Errors)
                    };
                }

                return new BackupResult
                {
                    Success = true,
                    BackupPath = outputPath
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to backup registry");
                throw;
            }
        }

        public async Task<bool> RestoreRegistryAsync(string backupPath)
        {
            try
            {
                var parameters = new Dictionary<string, object> { { "BackupPath", backupPath } };
                var result = await _psExecutor.ExecuteCommandAsync("Restore-Better11Registry", parameters);
                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to restore registry");
                return false;
            }
        }

        public async Task<string> ExportSettingsAsync(string outputPath)
        {
            try
            {
                var parameters = new Dictionary<string, object> { { "OutputPath", outputPath } };
                var result = await _psExecutor.ExecuteCommandAsync("Export-Better11Settings", parameters);

                if (result.Success && result.Output.Count > 0)
                {
                    return result.Output[0]?.ToString() ?? outputPath;
                }

                return outputPath;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to export settings");
                throw;
            }
        }

        public async Task<bool> ImportSettingsAsync(string settingsPath)
        {
            try
            {
                var parameters = new Dictionary<string, object> { { "SettingsPath", settingsPath } };
                var result = await _psExecutor.ExecuteCommandAsync("Import-Better11Settings", parameters);
                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to import settings");
                return false;
            }
        }
    }
}
