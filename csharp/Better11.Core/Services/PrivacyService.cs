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
    public class PrivacyService : IPrivacyService
    {
        private readonly PowerShellExecutor _psExecutor;
        private readonly ILogger<PrivacyService> _logger;

        public PrivacyService(PowerShellExecutor psExecutor, ILogger<PrivacyService> logger)
        {
            _psExecutor = psExecutor;
            _logger = logger;
        }

        public async Task<TelemetryLevel> GetTelemetryLevelAsync()
        {
            try
            {
                var result = await _psExecutor.ExecuteCommandAsync("Get-Better11TelemetryLevel");

                if (result.Success && result.Output.Count > 0)
                {
                    var level = result.Output[0]?.ToString() ?? "Basic";
                    return Enum.TryParse<TelemetryLevel>(level, out var telemetryLevel)
                        ? telemetryLevel
                        : TelemetryLevel.Basic;
                }

                return TelemetryLevel.Basic;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get telemetry level");
                throw;
            }
        }

        public async Task<bool> SetTelemetryLevelAsync(TelemetryLevel level, bool force = false)
        {
            try
            {
                _logger.LogInformation("Setting telemetry level to: {Level}", level);

                var parameters = new Dictionary<string, object>
                {
                    { "Level", level.ToString() },
                    { "Force", force }
                };

                var result = await _psExecutor.ExecuteCommandAsync("Set-Better11TelemetryLevel", parameters);
                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to set telemetry level");
                return false;
            }
        }

        public async Task<bool> DisableCortanaAsync(bool force = false)
        {
            try
            {
                var parameters = new Dictionary<string, object> { { "Force", force } };
                var result = await _psExecutor.ExecuteCommandAsync("Disable-Better11Cortana", parameters);
                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to disable Cortana");
                return false;
            }
        }

        public async Task<bool> SetWindowsFeedbackAsync(bool enabled)
        {
            try
            {
                var parameters = new Dictionary<string, object> { { "Enabled", enabled } };
                var result = await _psExecutor.ExecuteCommandAsync("Set-Better11WindowsFeedback", parameters);
                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to set Windows feedback");
                return false;
            }
        }

        public async Task<List<PrivacySetting>> GetPrivacySettingsAsync()
        {
            try
            {
                var result = await _psExecutor.ExecuteCommandAsync("Get-Better11PrivacySettings");

                var settings = new List<PrivacySetting>();
                foreach (var item in result.Output)
                {
                    var psObj = item as PSObject;
                    if (psObj == null) continue;

                    settings.Add(new PrivacySetting
                    {
                        Name = psObj.Properties["Name"]?.Value?.ToString() ?? string.Empty,
                        Category = psObj.Properties["Category"]?.Value?.ToString() ?? string.Empty,
                        Description = psObj.Properties["Description"]?.Value?.ToString(),
                        Enabled = Convert.ToBoolean(psObj.Properties["Enabled"]?.Value ?? false)
                    });
                }

                return settings;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get privacy settings");
                throw;
            }
        }

        public async Task<PrivacyResult> ApplyPrivacySettingsAsync(List<PrivacySetting> settings, bool force = false)
        {
            try
            {
                var parameters = new Dictionary<string, object>
                {
                    { "Settings", settings },
                    { "Force", force }
                };

                var result = await _psExecutor.ExecuteCommandAsync("Set-Better11PrivacySettings", parameters);

                if (!result.Success)
                {
                    return new PrivacyResult
                    {
                        Success = false,
                        ErrorMessage = string.Join("\n", result.Errors)
                    };
                }

                var output = result.Output.FirstOrDefault() as PSObject;
                return new PrivacyResult
                {
                    Success = true,
                    SettingsApplied = Convert.ToInt32(output?.Properties["SettingsApplied"]?.Value ?? 0)
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to apply privacy settings");
                throw;
            }
        }
    }
}
