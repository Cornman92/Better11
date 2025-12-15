using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Better11.Core.Interfaces;
using Better11.Core.Models;
using Better11.Core.PowerShell;
using Microsoft.Extensions.Logging;

namespace Better11.Core.Services
{
    /// <summary>
    /// Service for system safety and backup operations.
    /// </summary>
    public class SafetyService : ISafetyService
    {
        private readonly PowerShellExecutor _psExecutor;
        private readonly ILogger<SafetyService> _logger;

        public SafetyService(PowerShellExecutor psExecutor, ILogger<SafetyService> logger)
        {
            _psExecutor = psExecutor;
            _logger = logger;
        }

        /// <inheritdoc/>
        public async Task<bool> CreateRestorePointAsync(string description)
        {
            try
            {
                _logger.LogInformation("Creating restore point: {Description}", description);

                var result = await _psExecutor.ExecuteCommandAsync(
                    "New-Better11RestorePoint",
                    new() { { "Description", description } });

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to create restore point");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<List<RestorePoint>> GetRestorePointsAsync()
        {
            try
            {
                _logger.LogInformation("Getting restore points");

                var result = await _psExecutor.ExecuteCommandAsync("Get-Better11RestorePoints");
                var restorePoints = new List<RestorePoint>();

                if (result.Success)
                {
                    foreach (var item in result.Output)
                    {
                        dynamic rp = item;
                        restorePoints.Add(new RestorePoint
                        {
                            SequenceNumber = rp.SequenceNumber ?? 0,
                            Description = rp.Description?.ToString() ?? "",
                            CreationTime = rp.CreationTime ?? DateTime.MinValue,
                            Type = ParseRestorePointType(rp.RestorePointType)
                        });
                    }
                }

                return restorePoints;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get restore points");
                return new List<RestorePoint>();
            }
        }

        /// <inheritdoc/>
        public async Task<bool> IsAdministratorAsync()
        {
            try
            {
                var result = await _psExecutor.ExecuteCommandAsync("Test-Better11Administrator");

                if (result.Success && result.Output.Count > 0)
                {
                    return result.Output[0]?.ToString()?.ToLower() == "true";
                }

                return false;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to check administrator status");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<RegistryBackupResult> BackupRegistryKeyAsync(string keyPath, string? outputPath = null)
        {
            try
            {
                _logger.LogInformation("Backing up registry key: {Key}", keyPath);

                var parameters = new Dictionary<string, object> { { "KeyPath", keyPath } };
                if (!string.IsNullOrEmpty(outputPath))
                {
                    parameters["OutputPath"] = outputPath;
                }

                var result = await _psExecutor.ExecuteCommandAsync("Backup-Better11RegistryKey", parameters);

                if (result.Success && result.Output.Count > 0)
                {
                    dynamic output = result.Output[0];
                    return new RegistryBackupResult
                    {
                        Success = output.Success ?? false,
                        Path = output.Path?.ToString() ?? "",
                        RegistryKey = keyPath,
                        Timestamp = DateTime.Now
                    };
                }

                return new RegistryBackupResult { Success = false, RegistryKey = keyPath, Error = "No output from backup command" };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to backup registry key");
                return new RegistryBackupResult { Success = false, RegistryKey = keyPath, Error = ex.Message };
            }
        }

        /// <inheritdoc/>
        public async Task<bool> RestoreRegistryKeyAsync(string backupFilePath)
        {
            try
            {
                _logger.LogInformation("Restoring registry from: {Path}", backupFilePath);

                var result = await _psExecutor.ExecuteCommandAsync(
                    "Restore-Better11RegistryKey",
                    new() { { "BackupFilePath", backupFilePath } });

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to restore registry key");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<SafetyOperationResult> PerformSafeOperationAsync(
            string operationName,
            bool createRestorePoint = false,
            string? registryKeyToBackup = null)
        {
            try
            {
                _logger.LogInformation("Performing safe operation: {Operation}", operationName);

                var result = new SafetyOperationResult
                {
                    Operation = operationName,
                    BackupCreated = false
                };

                // Create restore point if requested
                if (createRestorePoint)
                {
                    var rpSuccess = await CreateRestorePointAsync($"Better11: {operationName}");
                    if (rpSuccess)
                    {
                        result.BackupCreated = true;
                        _logger.LogInformation("Restore point created for operation: {Operation}", operationName);
                    }
                }

                // Backup registry key if specified
                if (!string.IsNullOrEmpty(registryKeyToBackup))
                {
                    var backupResult = await BackupRegistryKeyAsync(registryKeyToBackup);
                    if (backupResult.Success)
                    {
                        result.BackupCreated = true;
                        result.BackupPath = backupResult.Path;
                        _logger.LogInformation("Registry backup created: {Path}", backupResult.Path);
                    }
                }

                result.Success = true;
                return result;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to perform safe operation");
                return new SafetyOperationResult
                {
                    Success = false,
                    Operation = operationName,
                    Error = ex.Message
                };
            }
        }

        private static RestorePointType ParseRestorePointType(dynamic type)
        {
            if (type == null) return RestorePointType.ModifySettings;

            int typeValue = type is int intVal ? intVal : 12;
            return typeValue switch
            {
                0 => RestorePointType.ApplicationInstall,
                1 => RestorePointType.ApplicationUninstall,
                10 => RestorePointType.DeviceDriverInstall,
                12 => RestorePointType.ModifySettings,
                13 => RestorePointType.CancelledOperation,
                _ => RestorePointType.ModifySettings
            };
        }
    }
}
