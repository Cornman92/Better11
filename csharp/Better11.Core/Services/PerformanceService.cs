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
    /// Service for system performance optimization.
    /// </summary>
    public class PerformanceService : IPerformanceService
    {
        private readonly PowerShellExecutor _psExecutor;
        private readonly ILogger<PerformanceService> _logger;

        public PerformanceService(PowerShellExecutor psExecutor, ILogger<PerformanceService> logger)
        {
            _psExecutor = psExecutor;
            _logger = logger;
        }

        /// <inheritdoc/>
        public async Task<PerformanceSettings> GetPerformanceSettingsAsync()
        {
            try
            {
                _logger.LogInformation("Getting performance settings");

                var result = await _psExecutor.ExecuteCommandAsync("Get-Better11PerformanceSettings");

                if (result.Success && result.Output.Count > 0)
                {
                    dynamic settings = result.Output[0];
                    return new PerformanceSettings
                    {
                        VisualEffects = settings.VisualEffects?.ToString() ?? "",
                        MenuShowDelay = settings.MenuShowDelay?.ToString() ?? "",
                        MouseHoverTime = settings.MouseHoverTime?.ToString() ?? "",
                        PagingFileManaged = settings.PagingFileManaged?.ToString() ?? "",
                        Win32PrioritySeparation = settings.Win32PrioritySeparation ?? 0,
                        FastStartupEnabled = settings.FastStartupEnabled ?? false
                    };
                }

                return new PerformanceSettings();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get performance settings");
                throw;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> SetVisualEffectsAsync(VisualEffectsPreset preset)
        {
            try
            {
                _logger.LogInformation("Setting visual effects to {Preset}", preset);

                var result = await _psExecutor.ExecuteCommandAsync(
                    "Set-Better11VisualEffects",
                    new() { { "Preset", preset.ToString() } });

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to set visual effects");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> SetProcessorSchedulingAsync(ProcessorPriority priority)
        {
            try
            {
                _logger.LogInformation("Setting processor scheduling to {Priority}", priority);

                var result = await _psExecutor.ExecuteCommandAsync(
                    "Set-Better11ProcessorScheduling",
                    new() { { "Priority", priority.ToString() } });

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to set processor scheduling");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> SetVirtualMemoryAsync(VirtualMemorySettings settings)
        {
            try
            {
                _logger.LogInformation("Setting virtual memory");

                var parameters = new Dictionary<string, object>();
                
                if (settings.SystemManaged)
                {
                    parameters["SystemManaged"] = true;
                }
                else
                {
                    parameters["InitialSizeMB"] = settings.InitialSizeMB;
                    parameters["MaximumSizeMB"] = settings.MaximumSizeMB;
                    parameters["Drive"] = settings.Drive;
                }

                var result = await _psExecutor.ExecuteCommandAsync("Set-Better11VirtualMemory", parameters);

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to set virtual memory");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> EnableFastStartupAsync()
        {
            try
            {
                _logger.LogInformation("Enabling Fast Startup");

                var result = await _psExecutor.ExecuteCommandAsync("Enable-Better11FastStartup");

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to enable Fast Startup");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> DisableFastStartupAsync()
        {
            try
            {
                _logger.LogInformation("Disabling Fast Startup");

                var result = await _psExecutor.ExecuteCommandAsync("Disable-Better11FastStartup");

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to disable Fast Startup");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> SetSystemResponsivenessAsync(int reservedPercent)
        {
            try
            {
                _logger.LogInformation("Setting system responsiveness to {Percent}%", reservedPercent);

                var result = await _psExecutor.ExecuteCommandAsync(
                    "Set-Better11SystemResponsiveness",
                    new() { { "ReservedPercent", reservedPercent } });

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to set system responsiveness");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> ApplyPerformancePresetAsync(PerformancePreset preset)
        {
            try
            {
                _logger.LogInformation("Applying performance preset: {Preset}", preset);

                var result = await _psExecutor.ExecuteCommandAsync(
                    "Optimize-Better11Performance",
                    new() { { "Preset", preset.ToString() } });

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to apply performance preset");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<ResourceUsage> GetResourceUsageAsync()
        {
            try
            {
                var result = await _psExecutor.ExecuteCommandAsync("Get-Better11ResourceUsage");

                if (result.Success && result.Output.Count > 0)
                {
                    dynamic usage = result.Output[0];
                    return new ResourceUsage
                    {
                        CPUUsagePercent = usage.CPUUsagePercent ?? 0,
                        MemoryUsedGB = usage.MemoryUsedGB ?? 0,
                        MemoryTotalGB = usage.MemoryTotalGB ?? 0,
                        MemoryUsedPercent = usage.MemoryUsedPercent ?? 0,
                        Timestamp = usage.Timestamp ?? DateTime.Now
                    };
                }

                return new ResourceUsage { Timestamp = DateTime.Now };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get resource usage");
                return new ResourceUsage { Timestamp = DateTime.Now };
            }
        }
    }
}
