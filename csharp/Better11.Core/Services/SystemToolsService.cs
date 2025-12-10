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
    /// Service for managing system tools and optimizations.
    /// Communicates with PowerShell backend to perform operations.
    /// </summary>
    public class SystemToolsService : ISystemToolsService
    {
        private readonly PowerShellExecutor _psExecutor;
        private readonly ILogger<SystemToolsService> _logger;

        public SystemToolsService(
            PowerShellExecutor psExecutor,
            ILogger<SystemToolsService> logger)
        {
            _psExecutor = psExecutor;
            _logger = logger;
        }

        /// <summary>
        /// Applies registry tweaks.
        /// </summary>
        public async Task<RegistryTweakResult> ApplyRegistryTweaksAsync(List<RegistryTweak> tweaks, bool force = false)
        {
            try
            {
                _logger.LogInformation("Applying {Count} registry tweaks", tweaks.Count);

                // Convert tweaks to PowerShell format
                var psHashtables = tweaks.Select(t => new
                {
                    Hive = t.Hive,
                    Path = t.Path,
                    Name = t.Name,
                    Value = t.Value,
                    Type = t.ValueType.ToString()
                }).ToArray();

                var parameters = new Dictionary<string, object>
                {
                    { "Tweaks", psHashtables },
                    { "Force", force }
                };

                var result = await _psExecutor.ExecuteCommandAsync(
                    "Set-Better11RegistryTweak",
                    parameters);

                if (!result.Success)
                {
                    return new RegistryTweakResult
                    {
                        TotalTweaks = tweaks.Count,
                        AppliedSuccessfully = 0,
                        Failed = tweaks.Count
                    };
                }

                var output = result.Output.FirstOrDefault() as PSObject;

                return new RegistryTweakResult
                {
                    TotalTweaks = GetPropertyValue<int>(output, "TotalTweaks"),
                    AppliedSuccessfully = GetPropertyValue<int>(output, "AppliedSuccessfully"),
                    Failed = GetPropertyValue<int>(output, "Failed")
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to apply registry tweaks");
                throw;
            }
        }

        /// <summary>
        /// Removes bloatware packages.
        /// </summary>
        public async Task<BloatwareRemovalResult> RemoveBloatwareAsync(List<string> packages, bool force = false)
        {
            try
            {
                _logger.LogInformation("Removing {Count} bloatware packages", packages.Count);

                var parameters = new Dictionary<string, object>
                {
                    { "Packages", packages.ToArray() },
                    { "Force", force }
                };

                var result = await _psExecutor.ExecuteCommandAsync(
                    "Remove-Better11Bloatware",
                    parameters);

                if (!result.Success)
                {
                    return new BloatwareRemovalResult
                    {
                        TotalPackages = packages.Count,
                        RemovedSuccessfully = 0,
                        Failed = packages.Count
                    };
                }

                var output = result.Output.FirstOrDefault() as PSObject;

                return new BloatwareRemovalResult
                {
                    TotalPackages = GetPropertyValue<int>(output, "TotalPackages"),
                    RemovedSuccessfully = GetPropertyValue<int>(output, "RemovedSuccessfully"),
                    Failed = GetPropertyValue<int>(output, "Failed")
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to remove bloatware");
                throw;
            }
        }

        /// <summary>
        /// Applies privacy settings.
        /// </summary>
        public async Task<PrivacyResult> ApplyPrivacySettingsAsync(PrivacyPreset preset, bool force = false)
        {
            try
            {
                _logger.LogInformation("Applying privacy preset: {Preset}", preset);

                var parameters = new Dictionary<string, object>
                {
                    { "Preset", preset.ToString() },
                    { "Force", force }
                };

                var result = await _psExecutor.ExecuteCommandAsync(
                    "Set-Better11PrivacySetting",
                    parameters);

                if (!result.Success)
                {
                    return new PrivacyResult
                    {
                        Preset = preset.ToString(),
                        SettingsApplied = 0,
                        Success = false
                    };
                }

                var output = result.Output.FirstOrDefault() as PSObject;

                return new PrivacyResult
                {
                    Preset = preset.ToString(),
                    SettingsApplied = GetPropertyValue<int>(output, "SettingsApplied"),
                    Success = GetPropertyValue<bool>(output, "Success")
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to apply privacy settings");
                throw;
            }
        }

        /// <summary>
        /// Gets startup items.
        /// </summary>
        public async Task<List<StartupItem>> GetStartupItemsAsync()
        {
            try
            {
                _logger.LogInformation("Getting startup items");

                var result = await _psExecutor.ExecuteCommandAsync("Get-Better11StartupItems");

                var items = new List<StartupItem>();

                foreach (var item in result.Output)
                {
                    var psObj = item as PSObject;
                    if (psObj == null) continue;

                    items.Add(new StartupItem
                    {
                        Name = GetPropertyValue<string>(psObj, "Name") ?? string.Empty,
                        Command = GetPropertyValue<string>(psObj, "Command") ?? string.Empty,
                        Location = GetPropertyValue<string>(psObj, "Location") ?? string.Empty,
                        Enabled = GetPropertyValue<bool>(psObj, "Enabled")
                    });
                }

                return items;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get startup items");
                throw;
            }
        }

        /// <summary>
        /// Manages a startup item.
        /// </summary>
        public async Task<bool> ManageStartupItemAsync(StartupItem item, bool enable)
        {
            try
            {
                _logger.LogInformation("{Action} startup item: {Name}",
                    enable ? "Enabling" : "Disabling", item.Name);

                var parameters = new Dictionary<string, object>
                {
                    { "Name", item.Name },
                    { "Enable", enable }
                };

                var result = await _psExecutor.ExecuteCommandAsync(
                    "Set-Better11StartupItem",
                    parameters);

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to manage startup item");
                throw;
            }
        }

        private T? GetPropertyValue<T>(PSObject? psObject, string propertyName)
        {
            if (psObject == null) return default;

            var property = psObject.Properties[propertyName];
            if (property == null) return default;

            try
            {
                if (typeof(T) == typeof(bool))
                {
                    return (T)(object)Convert.ToBoolean(property.Value);
                }
                return (T?)Convert.ChangeType(property.Value, typeof(T));
            }
            catch
            {
                return default;
            }
        }
    }
}
