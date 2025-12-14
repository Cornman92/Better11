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
    public class SystemToolsService : ISystemToolsService
    {
        private readonly PowerShellExecutor _psExecutor;
        private readonly ILogger<SystemToolsService> _logger;

        public SystemToolsService(PowerShellExecutor psExecutor, ILogger<SystemToolsService> logger)
        {
            _psExecutor = psExecutor;
            _logger = logger;
        }

        public async Task<TweakResult> ApplyRegistryTweaksAsync(List<RegistryTweak> tweaks, bool force = false)
        {
            try
            {
                _logger.LogInformation("Applying {Count} registry tweaks", tweaks.Count);

                var parameters = new Dictionary<string, object>
                {
                    { "Tweaks", tweaks },
                    { "Force", force }
                };

                var result = await _psExecutor.ExecuteCommandAsync("Set-Better11RegistryTweak", parameters);

                if (!result.Success)
                {
                    return new TweakResult
                    {
                        TotalTweaks = tweaks.Count,
                        Failed = tweaks.Count,
                        ErrorMessage = string.Join("\n", result.Errors)
                    };
                }

                var output = result.Output.FirstOrDefault() as PSObject;
                return new TweakResult
                {
                    TotalTweaks = tweaks.Count,
                    AppliedSuccessfully = Convert.ToInt32(output?.Properties["AppliedSuccessfully"]?.Value ?? 0),
                    Failed = Convert.ToInt32(output?.Properties["Failed"]?.Value ?? 0)
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to apply registry tweaks");
                throw;
            }
        }

        public async Task<RemovalResult> RemoveBloatwareAsync(List<string> packageNames, bool force = false)
        {
            try
            {
                _logger.LogInformation("Removing {Count} bloatware packages", packageNames.Count);

                var parameters = new Dictionary<string, object>
                {
                    { "PackageNames", packageNames },
                    { "Force", force }
                };

                var result = await _psExecutor.ExecuteCommandAsync("Remove-Better11Bloatware", parameters);

                if (!result.Success)
                {
                    return new RemovalResult
                    {
                        Success = false,
                        PackagesFailed = packageNames.Count,
                        ErrorMessage = string.Join("\n", result.Errors)
                    };
                }

                var output = result.Output.FirstOrDefault() as PSObject;
                return new RemovalResult
                {
                    Success = true,
                    PackagesRemoved = Convert.ToInt32(output?.Properties["PackagesRemoved"]?.Value ?? 0),
                    PackagesFailed = Convert.ToInt32(output?.Properties["PackagesFailed"]?.Value ?? 0)
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to remove bloatware");
                throw;
            }
        }

        public async Task<ServiceResult> ManageServiceAsync(ServiceAction action)
        {
            try
            {
                _logger.LogInformation("Managing service: {Service} - {Action}", action.ServiceName, action.ActionType);

                var parameters = new Dictionary<string, object>
                {
                    { "ServiceName", action.ServiceName },
                    { "ActionType", action.ActionType.ToString() }
                };

                if (action.StartMode.HasValue)
                {
                    parameters["StartMode"] = action.StartMode.Value.ToString();
                }

                var result = await _psExecutor.ExecuteCommandAsync("Set-Better11Service", parameters);

                return new ServiceResult
                {
                    Success = result.Success,
                    ServiceName = action.ServiceName,
                    ErrorMessage = result.Success ? null : string.Join("\n", result.Errors)
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to manage service: {Service}", action.ServiceName);
                throw;
            }
        }

        public async Task<PresetResult> ApplyPerformancePresetAsync(string presetName, bool force = false)
        {
            try
            {
                _logger.LogInformation("Applying performance preset: {Preset}", presetName);

                var parameters = new Dictionary<string, object>
                {
                    { "PresetName", presetName },
                    { "Force", force }
                };

                var result = await _psExecutor.ExecuteCommandAsync("Set-Better11PerformancePreset", parameters);

                if (!result.Success)
                {
                    return new PresetResult
                    {
                        Success = false,
                        PresetName = presetName,
                        ErrorMessage = string.Join("\n", result.Errors)
                    };
                }

                var output = result.Output.FirstOrDefault() as PSObject;
                return new PresetResult
                {
                    Success = true,
                    PresetName = presetName,
                    TweaksApplied = Convert.ToInt32(output?.Properties["TweaksApplied"]?.Value ?? 0)
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to apply performance preset: {Preset}", presetName);
                throw;
            }
        }

        public async Task<List<PerformancePreset>> ListPerformancePresetsAsync()
        {
            try
            {
                var result = await _psExecutor.ExecuteCommandAsync("Get-Better11PerformancePresets");

                var presets = new List<PerformancePreset>();
                foreach (var item in result.Output)
                {
                    var psObj = item as PSObject;
                    if (psObj == null) continue;

                    presets.Add(new PerformancePreset
                    {
                        Name = psObj.Properties["Name"]?.Value?.ToString() ?? string.Empty,
                        Description = psObj.Properties["Description"]?.Value?.ToString() ?? string.Empty
                    });
                }

                return presets;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to list performance presets");
                throw;
            }
        }

        public async Task<bool> CreateRestorePointAsync(string description)
        {
            try
            {
                _logger.LogInformation("Creating restore point: {Description}", description);

                var parameters = new Dictionary<string, object>
                {
                    { "Description", description }
                };

                var result = await _psExecutor.ExecuteCommandAsync("New-Better11RestorePoint", parameters);
                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to create restore point");
                return false;
            }
        }
    }
}
