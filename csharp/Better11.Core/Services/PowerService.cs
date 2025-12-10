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
    /// Service for power management operations.
    /// Communicates with PowerShell backend to manage power plans and hibernation.
    /// </summary>
    public class PowerService : IPowerService
    {
        private readonly PowerShellExecutor _psExecutor;
        private readonly ILogger<PowerService> _logger;

        public PowerService(PowerShellExecutor psExecutor, ILogger<PowerService> logger)
        {
            _psExecutor = psExecutor;
            _logger = logger;
        }

        /// <inheritdoc/>
        public async Task<List<PowerPlan>> ListPowerPlansAsync()
        {
            try
            {
                _logger.LogInformation("Listing power plans");

                var result = await _psExecutor.ExecuteCommandAsync("Get-Better11PowerPlans");

                if (!result.Success)
                {
                    throw new InvalidOperationException(
                        $"Failed to list power plans: {string.Join(", ", result.Errors)}");
                }

                var plans = new List<PowerPlan>();

                foreach (var item in result.Output)
                {
                    var psObj = item as PSObject;
                    if (psObj == null) continue;

                    plans.Add(new PowerPlan
                    {
                        Guid = psObj.Properties["Guid"]?.Value?.ToString() ?? string.Empty,
                        Name = psObj.Properties["Name"]?.Value?.ToString() ?? string.Empty,
                        Type = ParsePowerPlanType(psObj.Properties["Type"]?.Value?.ToString() ?? "Custom"),
                        IsActive = Convert.ToBoolean(psObj.Properties["IsActive"]?.Value ?? false)
                    });
                }

                _logger.LogInformation("Retrieved {Count} power plan(s)", plans.Count);
                return plans;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to list power plans");
                throw;
            }
        }

        /// <inheritdoc/>
        public async Task<PowerPlan?> GetActivePlanAsync()
        {
            var plans = await ListPowerPlansAsync();
            return plans.FirstOrDefault(p => p.IsActive);
        }

        /// <inheritdoc/>
        public async Task<bool> SetActivePlanAsync(string planGuid)
        {
            try
            {
                _logger.LogInformation("Setting active power plan: {Guid}", planGuid);

                var parameters = new Dictionary<string, object>
                {
                    { "Guid", planGuid },
                    { "Force", true }
                };

                var result = await _psExecutor.ExecuteCommandAsync("Set-Better11PowerPlan", parameters);

                if (result.Success)
                {
                    _logger.LogInformation("Power plan activated successfully");
                    return true;
                }
                else
                {
                    _logger.LogError("Failed to set power plan: {Errors}", string.Join(", ", result.Errors));
                    return false;
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to set active power plan");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> SetActivePlanByNameAsync(string planName)
        {
            try
            {
                _logger.LogInformation("Setting active power plan: {Name}", planName);

                var parameters = new Dictionary<string, object>
                {
                    { "Name", planName },
                    { "Force", true }
                };

                var result = await _psExecutor.ExecuteCommandAsync("Set-Better11PowerPlan", parameters);

                if (result.Success)
                {
                    _logger.LogInformation("Power plan activated successfully");
                    return true;
                }
                else
                {
                    _logger.LogError("Failed to set power plan: {Errors}", string.Join(", ", result.Errors));
                    return false;
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to set active power plan by name");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> EnableHibernationAsync()
        {
            try
            {
                _logger.LogInformation("Enabling hibernation");

                var parameters = new Dictionary<string, object>
                {
                    { "Force", true }
                };

                var result = await _psExecutor.ExecuteCommandAsync("Enable-Better11Hibernation", parameters);

                if (result.Success)
                {
                    _logger.LogInformation("Hibernation enabled successfully");
                    return true;
                }
                else
                {
                    _logger.LogError("Failed to enable hibernation: {Errors}", string.Join(", ", result.Errors));
                    return false;
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to enable hibernation");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> DisableHibernationAsync()
        {
            try
            {
                _logger.LogInformation("Disabling hibernation");

                var parameters = new Dictionary<string, object>
                {
                    { "Force", true }
                };

                var result = await _psExecutor.ExecuteCommandAsync("Disable-Better11Hibernation", parameters);

                if (result.Success)
                {
                    _logger.LogInformation("Hibernation disabled successfully");
                    return true;
                }
                else
                {
                    _logger.LogError("Failed to disable hibernation: {Errors}", string.Join(", ", result.Errors));
                    return false;
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to disable hibernation");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<string?> GenerateBatteryReportAsync(string? outputPath = null)
        {
            try
            {
                _logger.LogInformation("Generating battery report");

                var parameters = new Dictionary<string, object>();
                if (!string.IsNullOrEmpty(outputPath))
                {
                    parameters["OutputPath"] = outputPath;
                }

                var result = await _psExecutor.ExecuteCommandAsync("New-Better11BatteryReport", parameters);

                if (result.Success && result.Output.Count > 0)
                {
                    var reportPath = result.Output[0]?.ToString();
                    _logger.LogInformation("Battery report generated: {Path}", reportPath);
                    return reportPath;
                }
                else
                {
                    _logger.LogError("Failed to generate battery report: {Errors}", string.Join(", ", result.Errors));
                    return null;
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to generate battery report");
                return null;
            }
        }

        private PowerPlanType ParsePowerPlanType(string typeString)
        {
            return typeString.ToLowerInvariant() switch
            {
                "balanced" => PowerPlanType.Balanced,
                "highperformance" or "high performance" => PowerPlanType.HighPerformance,
                "powersaver" or "power saver" => PowerPlanType.PowerSaver,
                "ultimateperformance" or "ultimate performance" => PowerPlanType.UltimatePerformance,
                _ => PowerPlanType.Custom
            };
        }
    }
}
