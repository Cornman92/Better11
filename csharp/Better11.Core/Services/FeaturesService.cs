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
    public class FeaturesService : IFeaturesService
    {
        private readonly PowerShellExecutor _psExecutor;
        private readonly ILogger<FeaturesService> _logger;

        public FeaturesService(PowerShellExecutor psExecutor, ILogger<FeaturesService> logger)
        {
            _psExecutor = psExecutor;
            _logger = logger;
        }

        public async Task<List<WindowsFeature>> ListFeaturesAsync()
        {
            try
            {
                var result = await _psExecutor.ExecuteCommandAsync("Get-Better11WindowsFeatures");

                var features = new List<WindowsFeature>();
                foreach (var item in result.Output)
                {
                    var psObj = item as PSObject;
                    if (psObj == null) continue;

                    features.Add(new WindowsFeature
                    {
                        FeatureName = psObj.Properties["FeatureName"]?.Value?.ToString() ?? string.Empty,
                        DisplayName = psObj.Properties["DisplayName"]?.Value?.ToString() ?? string.Empty,
                        State = ParseFeatureState(psObj.Properties["State"]?.Value?.ToString() ?? "Disabled"),
                        RestartRequired = Convert.ToBoolean(psObj.Properties["RestartRequired"]?.Value ?? false)
                    });
                }

                return features;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to list Windows features");
                throw;
            }
        }

        public async Task<FeatureResult> EnableFeatureAsync(string featureName, bool force = false)
        {
            try
            {
                var parameters = new Dictionary<string, object>
                {
                    { "FeatureName", featureName },
                    { "Force", force }
                };

                var result = await _psExecutor.ExecuteCommandAsync("Enable-Better11WindowsFeature", parameters);

                if (!result.Success)
                {
                    return new FeatureResult
                    {
                        Success = false,
                        FeatureName = featureName,
                        ErrorMessage = string.Join("\n", result.Errors)
                    };
                }

                var output = result.Output.FirstOrDefault() as PSObject;
                return new FeatureResult
                {
                    Success = true,
                    FeatureName = featureName,
                    RestartRequired = Convert.ToBoolean(output?.Properties["RestartRequired"]?.Value ?? false)
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to enable feature: {Feature}", featureName);
                throw;
            }
        }

        public async Task<FeatureResult> DisableFeatureAsync(string featureName, bool force = false)
        {
            try
            {
                var parameters = new Dictionary<string, object>
                {
                    { "FeatureName", featureName },
                    { "Force", force }
                };

                var result = await _psExecutor.ExecuteCommandAsync("Disable-Better11WindowsFeature", parameters);

                if (!result.Success)
                {
                    return new FeatureResult
                    {
                        Success = false,
                        FeatureName = featureName,
                        ErrorMessage = string.Join("\n", result.Errors)
                    };
                }

                var output = result.Output.FirstOrDefault() as PSObject;
                return new FeatureResult
                {
                    Success = true,
                    FeatureName = featureName,
                    RestartRequired = Convert.ToBoolean(output?.Properties["RestartRequired"]?.Value ?? false)
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to disable feature: {Feature}", featureName);
                throw;
            }
        }

        public async Task<WindowsFeature?> GetFeatureStatusAsync(string featureName)
        {
            try
            {
                var features = await ListFeaturesAsync();
                return features.FirstOrDefault(f => f.FeatureName.Equals(featureName, StringComparison.OrdinalIgnoreCase));
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get feature status: {Feature}", featureName);
                return null;
            }
        }

        private FeatureState ParseFeatureState(string state)
        {
            return state.ToLowerInvariant() switch
            {
                "enabled" => FeatureState.Enabled,
                "disabled" => FeatureState.Disabled,
                "enablepending" => FeatureState.EnablePending,
                "disablepending" => FeatureState.DisablePending,
                _ => FeatureState.Disabled
            };
        }
    }
}
