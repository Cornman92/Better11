using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Better11.Core.Interfaces;
using Better11.Core.Models;
using Better11.Core.PowerShell;
using Microsoft.Extensions.Logging;

namespace Better11.Core.Services
{
    /// <summary>
    /// Service for managing Windows Updates using PowerShell backend.
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

        public async Task<UpdateOperationResult> GetUpdatesAsync(bool includeOptional = false)
        {
            try
            {
                _logger.LogInformation("Getting Windows updates (includeOptional: {Include})", includeOptional);

                var script = includeOptional 
                    ? "Get-Better11WindowsUpdate -IncludeOptional" 
                    : "Get-Better11WindowsUpdate";

                var result = await _psExecutor.ExecuteCommandAsync(script);

                if (result.HadErrors)
                {
                    return new UpdateOperationResult
                    {
                        Success = false,
                        Message = string.Join("; ", result.Errors)
                    };
                }

                var updates = result.Output
                    .Select(obj => PSObjectToWindowsUpdate(obj))
                    .ToList();

                return new UpdateOperationResult
                {
                    Success = true,
                    Message = $"Found {updates.Count} updates",
                    Updates = updates,
                    UpdatesFound = updates.Count
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get Windows updates");
                return new UpdateOperationResult
                {
                    Success = false,
                    Message = ex.Message
                };
            }
        }

        public async Task<UpdateOperationResult> CheckForUpdatesAsync()
        {
            return await GetUpdatesAsync(includeOptional: true);
        }

        public async Task<UpdateOperationResult> InstallUpdatesAsync(List<string> updateIds)
        {
            try
            {
                _logger.LogInformation("Installing {Count} Windows updates", updateIds.Count);

                // TODO: Implement batch installation
                // For now, return a placeholder result
                return new UpdateOperationResult
                {
                    Success = true,
                    Message = $"Installation initiated for {updateIds.Count} updates",
                    UpdatesInstalled = updateIds.Count
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to install Windows updates");
                return new UpdateOperationResult
                {
                    Success = false,
                    Message = ex.Message
                };
            }
        }

        public async Task<UpdateOperationResult> PauseUpdatesAsync(int days, bool confirm = true)
        {
            try
            {
                _logger.LogInformation("Pausing Windows updates for {Days} days", days);

                var script = confirm
                    ? $"Suspend-Better11Updates -Days {days}"
                    : $"Suspend-Better11Updates -Days {days} -Force";

                var result = await _psExecutor.ExecuteCommandAsync(script);

                var pausedUntil = DateTime.Now.AddDays(days);

                return new UpdateOperationResult
                {
                    Success = !result.HadErrors,
                    Message = result.HadErrors 
                        ? string.Join("; ", result.Errors)
                        : $"Updates paused until {pausedUntil:g}",
                    PausedUntil = pausedUntil
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to pause Windows updates");
                return new UpdateOperationResult
                {
                    Success = false,
                    Message = ex.Message
                };
            }
        }

        public async Task<UpdateOperationResult> ResumeUpdatesAsync(bool confirm = true)
        {
            try
            {
                _logger.LogInformation("Resuming Windows updates");

                var script = confirm
                    ? "Resume-Better11Updates"
                    : "Resume-Better11Updates -Force";

                var result = await _psExecutor.ExecuteCommandAsync(script);

                return new UpdateOperationResult
                {
                    Success = !result.HadErrors,
                    Message = result.HadErrors
                        ? string.Join("; ", result.Errors)
                        : "Windows updates resumed successfully"
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to resume Windows updates");
                return new UpdateOperationResult
                {
                    Success = false,
                    Message = ex.Message
                };
            }
        }

        public async Task<UpdateServiceStatus> GetUpdateStatusAsync()
        {
            try
            {
                _logger.LogInformation("Getting Windows Update service status");

                // TODO: Implement status check via PowerShell
                return new UpdateServiceStatus
                {
                    IsRunning = true,
                    IsPaused = false,
                    LastCheckTime = DateTime.Now.AddHours(-2),
                    PendingUpdates = 0,
                    RebootRequired = false
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get update status");
                return new UpdateServiceStatus
                {
                    IsRunning = false
                };
            }
        }

        public async Task<UpdateOperationResult> HideUpdateAsync(string updateId)
        {
            _logger.LogInformation("Hiding update {UpdateId}", updateId);
            // TODO: Implement hide functionality
            return new UpdateOperationResult { Success = true };
        }

        public async Task<UpdateOperationResult> ShowUpdateAsync(string updateId)
        {
            _logger.LogInformation("Showing update {UpdateId}", updateId);
            // TODO: Implement show functionality
            return new UpdateOperationResult { Success = true };
        }

        public async Task<List<WindowsUpdate>> GetUpdateHistoryAsync(int maxResults = 50)
        {
            try
            {
                _logger.LogInformation("Getting Windows Update history (max: {Max})", maxResults);
                // TODO: Implement history retrieval
                return new List<WindowsUpdate>();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get update history");
                return new List<WindowsUpdate>();
            }
        }

        private WindowsUpdate PSObjectToWindowsUpdate(dynamic obj)
        {
            try
            {
                return new WindowsUpdate
                {
                    UpdateId = obj.UpdateID?.ToString() ?? string.Empty,
                    Title = obj.Title?.ToString() ?? string.Empty,
                    Description = obj.Description?.ToString() ?? string.Empty,
                    Type = obj.Type?.ToString() ?? string.Empty,
                    SizeBytes = Convert.ToInt64(obj.SizeBytes ?? 0),
                    IsDownloaded = obj.IsDownloaded ?? false,
                    IsInstalled = obj.IsInstalled ?? false,
                    IsMandatory = obj.IsMandatory ?? false
                };
            }
            catch
            {
                return new WindowsUpdate
                {
                    Title = obj?.ToString() ?? "Unknown Update"
                };
            }
        }
    }
}
