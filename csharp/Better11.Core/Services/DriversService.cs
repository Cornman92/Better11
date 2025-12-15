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
    /// Service for driver management.
    /// </summary>
    public class DriversService : IDriversService
    {
        private readonly PowerShellExecutor _psExecutor;
        private readonly ILogger<DriversService> _logger;

        public DriversService(PowerShellExecutor psExecutor, ILogger<DriversService> logger)
        {
            _psExecutor = psExecutor;
            _logger = logger;
        }

        /// <inheritdoc/>
        public async Task<List<DriverInfo>> GetDriversAsync(string? category = null)
        {
            try
            {
                _logger.LogInformation("Getting drivers");

                var parameters = new Dictionary<string, object>();
                if (!string.IsNullOrEmpty(category))
                {
                    parameters["Category"] = category;
                }

                var result = await _psExecutor.ExecuteCommandAsync("Get-Better11Drivers", parameters);
                var drivers = new List<DriverInfo>();

                if (result.Success)
                {
                    foreach (var item in result.Output)
                    {
                        dynamic driver = item;
                        drivers.Add(new DriverInfo
                        {
                            DeviceName = driver.DeviceName?.ToString() ?? "",
                            DriverVersion = driver.DriverVersion?.ToString() ?? "",
                            DriverDate = driver.DriverDate,
                            Manufacturer = driver.Manufacturer?.ToString() ?? "",
                            DeviceClass = driver.DeviceClass?.ToString() ?? "",
                            DeviceID = driver.DeviceID?.ToString() ?? "",
                            IsSigned = driver.IsSigned ?? false,
                            InfName = driver.InfName?.ToString()
                        });
                    }
                }

                return drivers;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get drivers");
                return new List<DriverInfo>();
            }
        }

        /// <inheritdoc/>
        public async Task<List<DriverIssue>> GetDriverIssuesAsync()
        {
            try
            {
                _logger.LogInformation("Getting driver issues");

                var result = await _psExecutor.ExecuteCommandAsync("Get-Better11DriverIssues");
                var issues = new List<DriverIssue>();

                if (result.Success)
                {
                    foreach (var item in result.Output)
                    {
                        dynamic issue = item;
                        issues.Add(new DriverIssue
                        {
                            DeviceName = issue.DeviceName?.ToString() ?? "",
                            Status = issue.Status?.ToString() ?? "",
                            ErrorCode = issue.ErrorCode ?? 0,
                            ErrorDescription = issue.ErrorDescription?.ToString(),
                            DeviceID = issue.DeviceID?.ToString() ?? "",
                            DeviceClass = issue.Class?.ToString()
                        });
                    }
                }

                return issues;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get driver issues");
                return new List<DriverIssue>();
            }
        }

        /// <inheritdoc/>
        public async Task<DriverBackupResult> BackupDriversAsync(string? path = null)
        {
            try
            {
                _logger.LogInformation("Backing up drivers");

                var parameters = new Dictionary<string, object>();
                if (!string.IsNullOrEmpty(path))
                {
                    parameters["Path"] = path;
                }

                var result = await _psExecutor.ExecuteCommandAsync("Backup-Better11Drivers", parameters);

                if (result.Success && result.Output.Count > 0)
                {
                    dynamic output = result.Output[0];
                    return new DriverBackupResult
                    {
                        Success = output.Success ?? false,
                        Path = output.Path?.ToString() ?? "",
                        DriversBackedUp = output.DriversBackedUp ?? 0,
                        Timestamp = output.Timestamp ?? DateTime.Now
                    };
                }

                return new DriverBackupResult { Success = false, Error = "No output from backup command" };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to backup drivers");
                return new DriverBackupResult { Success = false, Error = ex.Message };
            }
        }

        /// <inheritdoc/>
        public async Task<bool> UpdateDriverAsync(string deviceId, string? infPath = null)
        {
            try
            {
                _logger.LogInformation("Updating driver for device: {DeviceId}", deviceId);

                var parameters = new Dictionary<string, object> { { "DeviceID", deviceId } };
                if (!string.IsNullOrEmpty(infPath))
                {
                    parameters["InfPath"] = infPath;
                }

                var result = await _psExecutor.ExecuteCommandAsync("Update-Better11Driver", parameters);

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to update driver");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<string> ExportDriverListAsync(string? path = null, string format = "JSON")
        {
            try
            {
                _logger.LogInformation("Exporting driver list");

                var parameters = new Dictionary<string, object> { { "Format", format } };
                if (!string.IsNullOrEmpty(path))
                {
                    parameters["Path"] = path;
                }

                var result = await _psExecutor.ExecuteCommandAsync("Export-Better11DriverList", parameters);

                if (result.Success && result.Output.Count > 0)
                {
                    dynamic output = result.Output[0];
                    return output.Path?.ToString() ?? "";
                }

                return "";
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to export driver list");
                return "";
            }
        }
    }
}
