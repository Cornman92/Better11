using System;
using System.Threading.Tasks;
using Better11.Core.Interfaces;
using Better11.Core.Models;
using Better11.Core.PowerShell;
using Microsoft.Extensions.Logging;

namespace Better11.Core.Services
{
    /// <summary>
    /// Service for gaming optimization management.
    /// </summary>
    public class GamingService : IGamingService
    {
        private readonly PowerShellExecutor _psExecutor;
        private readonly ILogger<GamingService> _logger;

        public GamingService(PowerShellExecutor psExecutor, ILogger<GamingService> logger)
        {
            _psExecutor = psExecutor;
            _logger = logger;
        }

        /// <inheritdoc/>
        public async Task<GamingSettings> GetGamingSettingsAsync()
        {
            try
            {
                _logger.LogInformation("Getting gaming settings");

                var result = await _psExecutor.ExecuteCommandAsync("Get-Better11GamingSettings");

                if (result.Success && result.Output.Count > 0)
                {
                    dynamic settings = result.Output[0];
                    return new GamingSettings
                    {
                        GameModeEnabled = settings.GameModeEnabled ?? false,
                        GameBarEnabled = settings.GameBarEnabled ?? false,
                        GPUSchedulingEnabled = settings.GPUSchedulingEnabled ?? false,
                        MouseAccelerationEnabled = settings.MouseAccelerationEnabled ?? true,
                        NagleAlgorithmEnabled = settings.NagleAlgorithmEnabled ?? true,
                        CurrentPowerPlan = settings.CurrentPowerPlan?.ToString() ?? ""
                    };
                }

                return new GamingSettings();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get gaming settings");
                throw;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> SetGameModeAsync(bool enabled)
        {
            try
            {
                _logger.LogInformation("{Action} Game Mode", enabled ? "Enabling" : "Disabling");

                var result = await _psExecutor.ExecuteCommandAsync(
                    "Set-Better11GameMode",
                    new() { { "Enabled", enabled } });

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to set Game Mode");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> SetGameBarAsync(bool enabled)
        {
            try
            {
                _logger.LogInformation("{Action} Game Bar", enabled ? "Enabling" : "Disabling");

                var result = await _psExecutor.ExecuteCommandAsync(
                    "Set-Better11GameBar",
                    new() { { "Enabled", enabled } });

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to set Game Bar");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> SetGPUSchedulingAsync(bool enabled)
        {
            try
            {
                _logger.LogInformation("{Action} GPU Scheduling", enabled ? "Enabling" : "Disabling");

                var result = await _psExecutor.ExecuteCommandAsync(
                    "Set-Better11GPUScheduling",
                    new() { { "Enabled", enabled } });

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to set GPU Scheduling");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> SetMouseAccelerationAsync(bool enabled)
        {
            try
            {
                _logger.LogInformation("{Action} Mouse Acceleration", enabled ? "Enabling" : "Disabling");

                var result = await _psExecutor.ExecuteCommandAsync(
                    "Set-Better11MouseAcceleration",
                    new() { { "Enabled", enabled } });

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to set Mouse Acceleration");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> SetNagleAlgorithmAsync(bool enabled)
        {
            try
            {
                _logger.LogInformation("{Action} Nagle Algorithm", enabled ? "Enabling" : "Disabling");

                var command = enabled ? "Enable-Better11NagleAlgorithm" : "Disable-Better11NagleAlgorithm";
                var result = await _psExecutor.ExecuteCommandAsync(command);

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to set Nagle Algorithm");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> SetHighPerformancePowerAsync(bool ultimate = false)
        {
            try
            {
                _logger.LogInformation("Setting {Plan} power plan", ultimate ? "Ultimate Performance" : "High Performance");

                var result = await _psExecutor.ExecuteCommandAsync(
                    "Set-Better11HighPerformancePower",
                    new() { { "Ultimate", ultimate } });

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to set power plan");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> ApplyGamingPresetAsync(GamingPreset preset)
        {
            try
            {
                _logger.LogInformation("Applying gaming preset: {Preset}", preset);

                var result = await _psExecutor.ExecuteCommandAsync(
                    "Set-Better11GamingPreset",
                    new() { { "Preset", preset.ToString() } });

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to apply gaming preset");
                return false;
            }
        }
    }
}
