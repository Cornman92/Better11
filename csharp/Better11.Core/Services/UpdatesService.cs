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
    /// Service for Windows Update management.
    /// </summary>
    public class UpdatesService : IUpdatesService
    {
        private readonly PowerShellExecutor _psExecutor;
        private readonly ILogger<UpdatesService> _logger;

        public UpdatesService(PowerShellExecutor psExecutor, ILogger<UpdatesService> logger)
        {
            _psExecutor = psExecutor;
            _logger = logger;
        }

        /// <inheritdoc/>
        public async Task<List<WindowsUpdate>> GetAvailableUpdatesAsync()
        {
            try
            {
                _logger.LogInformation("Getting available updates");

                var result = await _psExecutor.ExecuteCommandAsync("Get-Better11AvailableUpdates");
                var updates = new List<WindowsUpdate>();

                if (result.Success)
                {
                    foreach (var item in result.Output)
                    {
                        dynamic update = item;
                        updates.Add(new WindowsUpdate
                        {
                            Title = update.Title?.ToString() ?? "",
                            Description = update.Description?.ToString() ?? "",
                            KBNumber = update.KBNumber?.ToString() ?? "",
                            SizeBytes = update.SizeBytes ?? 0,
                            IsImportant = update.IsImportant ?? false,
                            IsCritical = update.IsCritical ?? false,
                            IsDriver = update.IsDriver ?? false,
                            IsInstalled = false,
                            IsHidden = update.IsHidden ?? false
                        });
                    }
                }

                return updates;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get available updates");
                return new List<WindowsUpdate>();
            }
        }

        /// <inheritdoc/>
        public async Task<bool> InstallUpdatesAsync(List<string>? kbNumbers = null)
        {
            try
            {
                _logger.LogInformation("Installing updates");

                var parameters = new Dictionary<string, object>();
                if (kbNumbers != null && kbNumbers.Count > 0)
                {
                    parameters["KBNumbers"] = kbNumbers.ToArray();
                }

                var result = await _psExecutor.ExecuteCommandAsync("Install-Better11Updates", parameters);

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to install updates");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> SuspendUpdatesAsync(int days = 7)
        {
            try
            {
                _logger.LogInformation("Suspending updates for {Days} days", days);

                var result = await _psExecutor.ExecuteCommandAsync(
                    "Suspend-Better11Updates",
                    new() { { "Days", days } });

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to suspend updates");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> ResumeUpdatesAsync()
        {
            try
            {
                _logger.LogInformation("Resuming updates");

                var result = await _psExecutor.ExecuteCommandAsync("Resume-Better11Updates");

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to resume updates");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> SetActiveHoursAsync(int startHour, int endHour)
        {
            try
            {
                _logger.LogInformation("Setting active hours: {Start}:00 - {End}:00", startHour, endHour);

                var result = await _psExecutor.ExecuteCommandAsync(
                    "Set-Better11ActiveHours",
                    new() { { "Start", startHour }, { "End", endHour } });

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to set active hours");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<(int Start, int End)> GetActiveHoursAsync()
        {
            try
            {
                var result = await _psExecutor.ExecuteCommandAsync("Get-Better11ActiveHours");

                if (result.Success && result.Output.Count > 0)
                {
                    dynamic hours = result.Output[0];
                    return (hours.Start ?? 8, hours.End ?? 17);
                }

                return (8, 17);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get active hours");
                return (8, 17);
            }
        }

        /// <inheritdoc/>
        public async Task<List<UpdateHistoryEntry>> GetUpdateHistoryAsync(int days = 30)
        {
            try
            {
                _logger.LogInformation("Getting update history for last {Days} days", days);

                var result = await _psExecutor.ExecuteCommandAsync(
                    "Get-Better11UpdateHistory",
                    new() { { "Days", days } });

                var history = new List<UpdateHistoryEntry>();

                if (result.Success)
                {
                    foreach (var item in result.Output)
                    {
                        dynamic entry = item;
                        history.Add(new UpdateHistoryEntry
                        {
                            Title = entry.Title?.ToString() ?? "",
                            KBNumber = entry.KBNumber?.ToString() ?? "",
                            InstalledOn = entry.InstalledOn ?? DateTime.MinValue,
                            Result = entry.Result?.ToString() ?? "",
                            Category = entry.Category?.ToString() ?? ""
                        });
                    }
                }

                return history;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get update history");
                return new List<UpdateHistoryEntry>();
            }
        }

        /// <inheritdoc/>
        public async Task<bool> UninstallUpdateAsync(string kbNumber)
        {
            try
            {
                _logger.LogInformation("Uninstalling update {KB}", kbNumber);

                var result = await _psExecutor.ExecuteCommandAsync(
                    "Uninstall-Better11Update",
                    new() { { "KBNumber", kbNumber } });

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to uninstall update");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<UpdateSettings> GetUpdateSettingsAsync()
        {
            try
            {
                var result = await _psExecutor.ExecuteCommandAsync("Get-Better11UpdateSettings");

                if (result.Success && result.Output.Count > 0)
                {
                    dynamic settings = result.Output[0];
                    return new UpdateSettings
                    {
                        ActiveHoursStart = settings.ActiveHoursStart ?? 8,
                        ActiveHoursEnd = settings.ActiveHoursEnd ?? 17,
                        AutomaticUpdatesEnabled = settings.AutomaticUpdatesEnabled ?? true,
                        PausedUntil = settings.PausedUntil,
                        RestartPending = settings.RestartPending ?? false
                    };
                }

                return new UpdateSettings();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get update settings");
                return new UpdateSettings();
            }
        }
    }
}
