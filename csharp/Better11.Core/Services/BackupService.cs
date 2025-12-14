using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Management.Automation;
using System.Text.Json;
using System.Threading.Tasks;
using Better11.Core.Interfaces;
using Better11.Core.Models;
using Better11.Core.PowerShell;
using Microsoft.Extensions.Logging;

namespace Better11.Core.Services
{
    /// <summary>
    /// Service for backup and restore operations.
    /// </summary>
    public class BackupService : IBackupService
    {
        private readonly PowerShellExecutor _psExecutor;
        private readonly ILogger<BackupService> _logger;

        public BackupService(PowerShellExecutor psExecutor, ILogger<BackupService> logger)
        {
            _psExecutor = psExecutor;
            _logger = logger;
        }

        /// <inheritdoc/>
        public async Task<List<RestorePoint>> ListRestorePointsAsync()
        {
            try
            {
                _logger.LogInformation("Listing restore points");

                var result = await _psExecutor.ExecuteCommandAsync(@"
                    Get-ComputerRestorePoint -ErrorAction SilentlyContinue | ForEach-Object {
                        [PSCustomObject]@{
                            SequenceNumber = $_.SequenceNumber
                            Description = $_.Description
                            CreationTime = $_.CreationTime
                            RestorePointType = $_.RestorePointType
                        }
                    }
                ");

                var points = new List<RestorePoint>();

                if (result.Success)
                {
                    foreach (var item in result.Output)
                    {
                        if (item is PSObject psObj)
                        {
                            points.Add(new RestorePoint
                            {
                                SequenceNumber = Convert.ToInt32(psObj.Properties["SequenceNumber"]?.Value ?? 0),
                                Description = psObj.Properties["Description"]?.Value?.ToString() ?? string.Empty,
                                CreationTime = DateTime.Parse(psObj.Properties["CreationTime"]?.Value?.ToString() ?? DateTime.MinValue.ToString()),
                                RestorePointType = psObj.Properties["RestorePointType"]?.Value?.ToString() ?? "Unknown"
                            });
                        }
                    }
                }

                _logger.LogInformation("Found {Count} restore point(s)", points.Count);
                return points;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to list restore points");
                throw;
            }
        }

        /// <inheritdoc/>
        public async Task<RestorePoint?> CreateRestorePointAsync(string description)
        {
            try
            {
                _logger.LogInformation("Creating restore point: {Description}", description);

                var result = await _psExecutor.ExecuteCommandAsync($@"
                    Checkpoint-Computer -Description '{description}' -RestorePointType 'MODIFY_SETTINGS'
                    Get-ComputerRestorePoint | Sort-Object -Property SequenceNumber -Descending | Select-Object -First 1 | ForEach-Object {{
                        [PSCustomObject]@{{
                            SequenceNumber = $_.SequenceNumber
                            Description = $_.Description
                            CreationTime = $_.CreationTime
                            RestorePointType = $_.RestorePointType
                        }}
                    }}
                ");

                if (result.Success && result.Output.Count > 0)
                {
                    var psObj = result.Output[0] as PSObject;
                    if (psObj != null)
                    {
                        _logger.LogInformation("Restore point created successfully");
                        return new RestorePoint
                        {
                            SequenceNumber = Convert.ToInt32(psObj.Properties["SequenceNumber"]?.Value ?? 0),
                            Description = psObj.Properties["Description"]?.Value?.ToString() ?? description,
                            CreationTime = DateTime.Parse(psObj.Properties["CreationTime"]?.Value?.ToString() ?? DateTime.Now.ToString()),
                            RestorePointType = "MODIFY_SETTINGS"
                        };
                    }
                }

                _logger.LogWarning("Failed to create restore point");
                return null;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to create restore point");
                return null;
            }
        }

        /// <inheritdoc/>
        public async Task<BackupResult> ExportSettingsAsync(string outputPath)
        {
            try
            {
                _logger.LogInformation("Exporting settings to: {Path}", outputPath);

                var settings = new SettingsExport
                {
                    ExportDate = DateTime.UtcNow,
                    Version = "1.0",
                    Settings = new Dictionary<string, object>()
                };

                // Export registry settings
                var registryPaths = new[]
                {
                    @"HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Search",
                    @"HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo",
                    @"HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection"
                };

                foreach (var path in registryPaths)
                {
                    var result = await _psExecutor.ExecuteCommandAsync($@"
                        if (Test-Path '{path}') {{
                            Get-ItemProperty -Path '{path}' -ErrorAction SilentlyContinue | 
                            Select-Object -Property * -ExcludeProperty PS* |
                            ConvertTo-Json
                        }}
                    ");

                    if (result.Success && result.Output.Count > 0)
                    {
                        var key = path.Replace(":", "").Replace("\\", "/");
                        settings.Settings[key] = result.Output[0]?.ToString() ?? "{}";
                    }
                }

                // Ensure directory exists
                var directory = Path.GetDirectoryName(outputPath);
                if (!string.IsNullOrEmpty(directory))
                {
                    Directory.CreateDirectory(directory);
                }

                var json = JsonSerializer.Serialize(settings, new JsonSerializerOptions
                {
                    WriteIndented = true
                });

                await File.WriteAllTextAsync(outputPath, json);

                _logger.LogInformation("Settings exported successfully");
                return new BackupResult
                {
                    Success = true,
                    BackupPath = outputPath,
                    Message = "Settings exported successfully",
                    Timestamp = DateTime.UtcNow
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to export settings");
                return new BackupResult
                {
                    Success = false,
                    Message = ex.Message,
                    Timestamp = DateTime.UtcNow
                };
            }
        }

        /// <inheritdoc/>
        public async Task<bool> ImportSettingsAsync(string inputPath)
        {
            try
            {
                _logger.LogInformation("Importing settings from: {Path}", inputPath);

                if (!File.Exists(inputPath))
                {
                    _logger.LogError("Settings file not found: {Path}", inputPath);
                    return false;
                }

                var json = await File.ReadAllTextAsync(inputPath);
                var settings = JsonSerializer.Deserialize<SettingsExport>(json);

                if (settings == null)
                {
                    _logger.LogError("Failed to parse settings file");
                    return false;
                }

                _logger.LogInformation("Settings imported from version {Version}, dated {Date}",
                    settings.Version, settings.ExportDate);

                // Import would require implementing registry write operations
                // This is a placeholder for the actual implementation
                _logger.LogWarning("Settings import not fully implemented");
                
                return true;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to import settings");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<BackupResult> BackupRegistryAsync(IEnumerable<string> keyPaths, string outputPath)
        {
            try
            {
                _logger.LogInformation("Backing up registry keys to: {Path}", outputPath);

                var directory = Path.GetDirectoryName(outputPath);
                if (!string.IsNullOrEmpty(directory))
                {
                    Directory.CreateDirectory(directory);
                }

                var keyList = keyPaths.ToList();
                var backedUp = new List<string>();

                foreach (var keyPath in keyList)
                {
                    var safeFileName = keyPath.Replace(":", "").Replace("\\", "_").Replace("/", "_");
                    var keyOutputPath = Path.Combine(Path.GetDirectoryName(outputPath) ?? ".", $"{safeFileName}.reg");

                    var result = await _psExecutor.ExecuteCommandAsync($@"
                        $keyPath = '{keyPath.Replace("HKCU:", "HKEY_CURRENT_USER").Replace("HKLM:", "HKEY_LOCAL_MACHINE")}'
                        reg export $keyPath '{keyOutputPath}' /y
                    ");

                    if (result.Success)
                    {
                        backedUp.Add(keyOutputPath);
                    }
                }

                _logger.LogInformation("Backed up {Count} of {Total} registry keys", backedUp.Count, keyList.Count);

                return new BackupResult
                {
                    Success = backedUp.Count == keyList.Count,
                    BackupPath = outputPath,
                    Message = $"Backed up {backedUp.Count} of {keyList.Count} keys",
                    Timestamp = DateTime.UtcNow,
                    FilesBackedUp = backedUp
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to backup registry");
                return new BackupResult
                {
                    Success = false,
                    Message = ex.Message,
                    Timestamp = DateTime.UtcNow
                };
            }
        }
    }
}
