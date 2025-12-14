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
    public class UpdateService : IUpdateService
    {
        private readonly PowerShellExecutor _psExecutor;
        private readonly ILogger<UpdateService> _logger;

        public UpdateService(PowerShellExecutor psExecutor, ILogger<UpdateService> logger)
        {
            _psExecutor = psExecutor;
            _logger = logger;
        }

        public async Task<List<UpdateInfo>> ListUpdatesAsync()
        {
            try
            {
                var result = await _psExecutor.ExecuteCommandAsync("Get-Better11WindowsUpdate");

                var updates = new List<UpdateInfo>();
                foreach (var item in result.Output)
                {
                    var psObj = item as PSObject;
                    if (psObj == null) continue;

                    updates.Add(new UpdateInfo
                    {
                        UpdateId = psObj.Properties["UpdateId"]?.Value?.ToString() ?? string.Empty,
                        Title = psObj.Properties["Title"]?.Value?.ToString() ?? string.Empty,
                        SizeBytes = Convert.ToInt64(psObj.Properties["SizeBytes"]?.Value ?? 0L),
                        IsMandatory = Convert.ToBoolean(psObj.Properties["IsMandatory"]?.Value ?? false)
                    });
                }

                return updates;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to list updates");
                throw;
            }
        }

        public async Task<UpdateResult> InstallUpdatesAsync(List<string> updateIds, bool force = false)
        {
            try
            {
                var parameters = new Dictionary<string, object>
                {
                    { "UpdateIds", updateIds },
                    { "Force", force }
                };

                var result = await _psExecutor.ExecuteCommandAsync("Install-Better11WindowsUpdate", parameters);

                if (!result.Success)
                {
                    return new UpdateResult
                    {
                        Success = false,
                        ErrorMessage = string.Join("\n", result.Errors)
                    };
                }

                var output = result.Output.FirstOrDefault() as PSObject;
                return new UpdateResult
                {
                    Success = true,
                    UpdatesInstalled = Convert.ToInt32(output?.Properties["UpdatesInstalled"]?.Value ?? 0),
                    RestartRequired = Convert.ToBoolean(output?.Properties["RestartRequired"]?.Value ?? false)
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to install updates");
                throw;
            }
        }

        public async Task<bool> PauseUpdatesAsync(int days)
        {
            try
            {
                var parameters = new Dictionary<string, object> { { "Days", days } };
                var result = await _psExecutor.ExecuteCommandAsync("Suspend-Better11WindowsUpdate", parameters);
                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to pause updates");
                return false;
            }
        }

        public async Task<bool> ResumeUpdatesAsync()
        {
            try
            {
                var result = await _psExecutor.ExecuteCommandAsync("Resume-Better11WindowsUpdate");
                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to resume updates");
                return false;
            }
        }

        public async Task<UpdatePolicy> GetUpdatePolicyAsync()
        {
            try
            {
                var result = await _psExecutor.ExecuteCommandAsync("Get-Better11UpdatePolicy");

                if (result.Success && result.Output.Count > 0)
                {
                    var psObj = result.Output[0] as PSObject;
                    return new UpdatePolicy
                    {
                        AutomaticUpdates = Convert.ToBoolean(psObj?.Properties["AutomaticUpdates"]?.Value ?? true),
                        DeferFeatureUpdatesDays = Convert.ToInt32(psObj?.Properties["DeferFeatureUpdatesDays"]?.Value ?? 0),
                        DeferQualityUpdatesDays = Convert.ToInt32(psObj?.Properties["DeferQualityUpdatesDays"]?.Value ?? 0),
                        PauseUpdates = Convert.ToBoolean(psObj?.Properties["PauseUpdates"]?.Value ?? false)
                    };
                }

                return new UpdatePolicy { AutomaticUpdates = true };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get update policy");
                throw;
            }
        }

        public async Task<bool> SetUpdatePolicyAsync(UpdatePolicy policy)
        {
            try
            {
                var parameters = new Dictionary<string, object>
                {
                    { "AutomaticUpdates", policy.AutomaticUpdates },
                    { "DeferFeatureUpdatesDays", policy.DeferFeatureUpdatesDays },
                    { "DeferQualityUpdatesDays", policy.DeferQualityUpdatesDays }
                };

                var result = await _psExecutor.ExecuteCommandAsync("Set-Better11UpdatePolicy", parameters);
                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to set update policy");
                return false;
            }
        }
    }
}
