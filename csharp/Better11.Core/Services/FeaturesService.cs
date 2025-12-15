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
    /// Service for Windows optional features and capabilities management.
    /// </summary>
    public class FeaturesService : IFeaturesService
    {
        private readonly PowerShellExecutor _psExecutor;
        private readonly ILogger<FeaturesService> _logger;

        public FeaturesService(PowerShellExecutor psExecutor, ILogger<FeaturesService> logger)
        {
            _psExecutor = psExecutor;
            _logger = logger;
        }

        /// <inheritdoc/>
        public async Task<List<OptionalFeature>> GetOptionalFeaturesAsync(string? nameFilter = null)
        {
            try
            {
                _logger.LogInformation("Getting optional features");

                var parameters = new Dictionary<string, object>();
                if (!string.IsNullOrEmpty(nameFilter))
                {
                    parameters["Name"] = nameFilter;
                }

                var result = await _psExecutor.ExecuteCommandAsync("Get-Better11OptionalFeatures", parameters);
                var features = new List<OptionalFeature>();

                if (result.Success)
                {
                    foreach (var item in result.Output)
                    {
                        dynamic feature = item;
                        features.Add(new OptionalFeature
                        {
                            Name = feature.Name?.ToString() ?? "",
                            State = ParseFeatureState(feature.State?.ToString()),
                            RestartRequired = feature.RestartRequired ?? false,
                            Description = feature.Description?.ToString()
                        });
                    }
                }

                return features;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get optional features");
                return new List<OptionalFeature>();
            }
        }

        /// <inheritdoc/>
        public async Task<bool> EnableOptionalFeatureAsync(string featureName, bool noRestart = true)
        {
            try
            {
                _logger.LogInformation("Enabling feature: {Feature}", featureName);

                var result = await _psExecutor.ExecuteCommandAsync(
                    "Enable-Better11OptionalFeature",
                    new() { { "Name", featureName }, { "NoRestart", noRestart } });

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to enable feature: {Feature}", featureName);
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> DisableOptionalFeatureAsync(string featureName, bool noRestart = true)
        {
            try
            {
                _logger.LogInformation("Disabling feature: {Feature}", featureName);

                var result = await _psExecutor.ExecuteCommandAsync(
                    "Disable-Better11OptionalFeature",
                    new() { { "Name", featureName }, { "NoRestart", noRestart } });

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to disable feature: {Feature}", featureName);
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<List<WindowsCapability>> GetCapabilitiesAsync(bool installedOnly = false)
        {
            try
            {
                _logger.LogInformation("Getting Windows capabilities");

                var parameters = new Dictionary<string, object>();
                if (installedOnly)
                {
                    parameters["Installed"] = true;
                }

                var result = await _psExecutor.ExecuteCommandAsync("Get-Better11InstalledCapabilities", parameters);
                var capabilities = new List<WindowsCapability>();

                if (result.Success)
                {
                    foreach (var item in result.Output)
                    {
                        dynamic cap = item;
                        capabilities.Add(new WindowsCapability
                        {
                            Name = cap.Name?.ToString() ?? "",
                            State = ParseCapabilityState(cap.State?.ToString()),
                            DisplayName = cap.DisplayName?.ToString() ?? ""
                        });
                    }
                }

                return capabilities;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get capabilities");
                return new List<WindowsCapability>();
            }
        }

        /// <inheritdoc/>
        public async Task<bool> AddCapabilityAsync(string capabilityName)
        {
            try
            {
                _logger.LogInformation("Adding capability: {Capability}", capabilityName);

                var result = await _psExecutor.ExecuteCommandAsync(
                    "Add-Better11Capability",
                    new() { { "Name", capabilityName } });

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to add capability: {Capability}", capabilityName);
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> RemoveCapabilityAsync(string capabilityName)
        {
            try
            {
                _logger.LogInformation("Removing capability: {Capability}", capabilityName);

                var result = await _psExecutor.ExecuteCommandAsync(
                    "Remove-Better11Capability",
                    new() { { "Name", capabilityName } });

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to remove capability: {Capability}", capabilityName);
                return false;
            }
        }

        private static FeatureState ParseFeatureState(string? state)
        {
            return state?.ToLower() switch
            {
                "enabled" => FeatureState.Enabled,
                "disabled" => FeatureState.Disabled,
                "enablepending" => FeatureState.EnablePending,
                "disablepending" => FeatureState.DisablePending,
                _ => FeatureState.Disabled
            };
        }

        private static CapabilityState ParseCapabilityState(string? state)
        {
            return state?.ToLower() switch
            {
                "installed" => CapabilityState.Installed,
                "notpresent" => CapabilityState.NotPresent,
                "staged" => CapabilityState.Staged,
                _ => CapabilityState.NotPresent
            };
        }
    }
}
