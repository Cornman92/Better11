using System;
using System.Collections.Generic;
using System.Linq;
using System.Management.Automation;
using System.Threading.Tasks;
using Better11.Core.Apps;
using Better11.Core.Apps.Models;
using Better11.Core.Interfaces;
using Better11.Core.Models;
using Better11.Core.PowerShell;
using Microsoft.Extensions.Logging;

namespace Better11.Core.Services
{
    /// <summary>
    /// Service for managing application installation and updates.
    /// </summary>
    public class AppManagerService : IAppManager, IAppManagerService
    {
        private readonly PowerShellExecutor _psExecutor;
        private readonly ILogger<AppManagerService> _logger;
        private readonly string _catalogPath;
        private readonly string _downloadDir;
        private readonly string _stateFile;

        public AppManagerService(PowerShellExecutor psExecutor, ILogger<AppManagerService> logger)
        {
            _psExecutor = psExecutor;
            _logger = logger;

            // Initialize paths for AppManager
            var userProfile = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
            var better11Dir = Path.Combine(userProfile, ".better11");
            _catalogPath = Path.Combine(Directory.GetCurrentDirectory(), "catalog.json");
            _downloadDir = Path.Combine(better11Dir, "downloads");
            _stateFile = Path.Combine(better11Dir, "installed.json");
        }

        public async Task<List<AppMetadata>> ListAvailableAppsAsync(string? category = null)
        {
            try
            {
                _logger.LogInformation("Fetching available applications");

                // Use AppManager for category filtering support
                var manager = new AppManager(_catalogPath, _downloadDir, _stateFile, logger: _logger);
                return await Task.Run(() => manager.ListAvailable(category));
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to list available applications");
                throw;
            }
        }

        public async Task<List<string>> GetCategoriesAsync()
        {
            try
            {
                _logger.LogInformation("Fetching application categories");

                var manager = new AppManager(_catalogPath, _downloadDir, _stateFile, logger: _logger);
                return await Task.Run(() => manager.GetCategories());
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get categories");
                throw;
            }
        }

        public async Task<List<AppMetadata>> SearchAppsAsync(string query, string? category = null)
        {
            try
            {
                _logger.LogInformation("Searching applications with query: {Query}, category: {Category}", query, category ?? "all");

                var manager = new AppManager(_catalogPath, _downloadDir, _stateFile, logger: _logger);
                return await Task.Run(() => manager.SearchApps(query, category));
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to search applications");
                throw;
            }
        }

        public async Task<List<AppMetadata>> ListInstalledAppsAsync()
        {
            try
            {
                var apps = await ListAvailableAppsAsync();
                return apps.Where(a => a.IsInstalled).ToList();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to list installed applications");
                throw;
            }
        }

        public async Task<AppStatus?> GetAppStatusAsync(string appId)
        {
            try
            {
                _logger.LogInformation("Getting status for app: {AppId}", appId);

                var parameters = new Dictionary<string, object>
                {
                    { "AppId", appId }
                };

                var result = await _psExecutor.ExecuteCommandAsync("Get-Better11AppStatus", parameters);

                if (!result.Success || result.Output.Count == 0)
                {
                    return null;
                }

                var psObj = result.Output[0] as PSObject;
                if (psObj == null) return null;

                return new AppStatus
                {
                    AppId = psObj.Properties["AppId"]?.Value?.ToString() ?? string.Empty,
                    Version = psObj.Properties["Version"]?.Value?.ToString() ?? string.Empty,
                    Installed = Convert.ToBoolean(psObj.Properties["Installed"]?.Value ?? false),
                    InstallerPath = psObj.Properties["InstallerPath"]?.Value?.ToString() ?? string.Empty
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get app status for {AppId}", appId);
                throw;
            }
        }

        public async Task<InstallResult> InstallAppAsync(
            string appId,
            bool force = false,
            bool skipDependencies = false,
            IProgress<OperationProgress>? progress = null,
            CancellationToken cancellationToken = default)
        {
            try
            {
                _logger.LogInformation("Installing application: {AppId}", appId);

                // Use AppManager directly for progress reporting support
                var manager = new AppManager(_catalogPath, _downloadDir, _stateFile, logger: _logger);
                var (status, installerResult) = await manager.InstallAsync(appId, progress, cancellationToken);

                return new InstallResult
                {
                    Success = installerResult.ReturnCode == 0,
                    AppId = appId,
                    Version = status.Version,
                    Status = installerResult.ReturnCode == 0 ? "Installed" : "Failed",
                    ErrorMessage = installerResult.ReturnCode != 0 ? installerResult.Stderr : null
                };
            }
            catch (OperationCanceledException)
            {
                _logger.LogWarning("Installation cancelled for: {AppId}", appId);
                progress?.Report(new OperationProgress
                {
                    AppId = appId,
                    Stage = OperationStage.Failed,
                    PercentComplete = 0,
                    Message = "Installation cancelled by user",
                    IsComplete = true,
                    ErrorMessage = "Operation cancelled"
                });
                return new InstallResult
                {
                    Success = false,
                    AppId = appId,
                    ErrorMessage = "Installation cancelled by user"
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to install application: {AppId}", appId);
                progress?.Report(new OperationProgress
                {
                    AppId = appId,
                    Stage = OperationStage.Failed,
                    PercentComplete = 0,
                    Message = $"Installation failed: {ex.Message}",
                    IsComplete = true,
                    ErrorMessage = ex.Message
                });
                return new InstallResult
                {
                    Success = false,
                    AppId = appId,
                    ErrorMessage = ex.Message
                };
            }
        }

        public async Task<UninstallResult> UninstallAppAsync(string appId, bool force = false)
        {
            try
            {
                _logger.LogInformation("Uninstalling application: {AppId}", appId);

                var parameters = new Dictionary<string, object>
                {
                    { "AppId", appId },
                    { "Force", force }
                };

                var result = await _psExecutor.ExecuteCommandAsync("Uninstall-Better11App", parameters);

                return new UninstallResult
                {
                    Success = result.Success,
                    AppId = appId,
                    ErrorMessage = result.Success ? null : string.Join("\n", result.Errors)
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to uninstall application: {AppId}", appId);
                return new UninstallResult
                {
                    Success = false,
                    AppId = appId,
                    ErrorMessage = ex.Message
                };
            }
        }

        public async Task<InstallResult> UpdateAppAsync(string appId)
        {
            try
            {
                _logger.LogInformation("Updating application: {AppId}", appId);

                var parameters = new Dictionary<string, object>
                {
                    { "AppId", appId }
                };

                var result = await _psExecutor.ExecuteCommandAsync("Update-Better11App", parameters);

                if (!result.Success)
                {
                    return new InstallResult
                    {
                        Success = false,
                        AppId = appId,
                        ErrorMessage = string.Join("\n", result.Errors)
                    };
                }

                var output = result.Output.FirstOrDefault() as PSObject;

                return new InstallResult
                {
                    Success = true,
                    AppId = appId,
                    Version = output?.Properties["Version"]?.Value?.ToString() ?? string.Empty,
                    Status = "Updated"
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to update application: {AppId}", appId);
                return new InstallResult
                {
                    Success = false,
                    AppId = appId,
                    ErrorMessage = ex.Message
                };
            }
        }

        public async Task<DownloadResult> DownloadAppAsync(string appId)
        {
            try
            {
                _logger.LogInformation("Downloading application: {AppId}", appId);

                var parameters = new Dictionary<string, object>
                {
                    { "AppId", appId }
                };

                var result = await _psExecutor.ExecuteCommandAsync("Get-Better11AppInstaller", parameters);

                if (!result.Success)
                {
                    return new DownloadResult
                    {
                        Success = false,
                        AppId = appId,
                        ErrorMessage = string.Join("\n", result.Errors)
                    };
                }

                var filePath = result.Output.FirstOrDefault()?.ToString();

                return new DownloadResult
                {
                    Success = true,
                    AppId = appId,
                    FilePath = filePath
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to download application: {AppId}", appId);
                return new DownloadResult
                {
                    Success = false,
                    AppId = appId,
                    ErrorMessage = ex.Message
                };
            }
        }

        private InstallerType ParseInstallerType(string type)
        {
            return type.ToLowerInvariant() switch
            {
                "msi" => InstallerType.MSI,
                "exe" => InstallerType.EXE,
                "appx" => InstallerType.APPX,
                _ => InstallerType.EXE
            };
        }

        private List<string> ParseStringList(object? value)
        {
            if (value == null) return new List<string>();

            if (value is IEnumerable<object> enumerable)
            {
                return enumerable.Select(o => o.ToString() ?? string.Empty).ToList();
            }

            return new List<string>();
        }

        public async Task<InstallPlanSummary> GetInstallPlanAsync(string appId)
        {
            try
            {
                _logger.LogInformation("Building install plan for: {AppId}", appId);

                var manager = new AppManager(_catalogPath, _downloadDir, _stateFile, logger: _logger);
                return await Task.Run(() => manager.BuildInstallPlan(appId));
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to build install plan for {AppId}", appId);
                throw;
            }
        }

        public async Task<BatchOperationResult> BatchInstallAsync(
            IEnumerable<string> appIds,
            IProgress<OperationProgress>? progress = null,
            CancellationToken cancellationToken = default,
            bool continueOnError = true)
        {
            try
            {
                _logger.LogInformation("Starting batch install for {Count} applications", appIds.Count());

                var manager = new AppManager(_catalogPath, _downloadDir, _stateFile, logger: _logger);
                return await manager.BatchInstallAsync(appIds, progress, cancellationToken, continueOnError);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Batch install operation failed");
                throw;
            }
        }

        public async Task<BatchOperationResult> BatchUninstallAsync(
            IEnumerable<string> appIds,
            bool continueOnError = true)
        {
            try
            {
                _logger.LogInformation("Starting batch uninstall for {Count} applications", appIds.Count());

                var manager = new AppManager(_catalogPath, _downloadDir, _stateFile, logger: _logger);
                return await Task.Run(() => manager.BatchUninstall(appIds, continueOnError));
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Batch uninstall operation failed");
                throw;
            }
        }
    }
}
