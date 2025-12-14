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
    /// Service for managing application installation and updates.
    /// </summary>
    public class AppManagerService : IAppManagerService
    {
        private readonly PowerShellExecutor _psExecutor;
        private readonly ILogger<AppManagerService> _logger;

        public AppManagerService(PowerShellExecutor psExecutor, ILogger<AppManagerService> logger)
        {
            _psExecutor = psExecutor;
            _logger = logger;
        }

        public async Task<List<AppMetadata>> ListAvailableAppsAsync()
        {
            try
            {
                _logger.LogInformation("Fetching available applications");

                var result = await _psExecutor.ExecuteCommandAsync("Get-Better11Apps");

                if (!result.Success)
                {
                    throw new InvalidOperationException(
                        $"Failed to get applications: {string.Join(", ", result.Errors)}");
                }

                var apps = new List<AppMetadata>();

                foreach (var item in result.Output)
                {
                    var psObj = item as PSObject;
                    if (psObj == null) continue;

                    apps.Add(new AppMetadata
                    {
                        AppId = psObj.Properties["AppId"]?.Value?.ToString() ?? string.Empty,
                        Name = psObj.Properties["Name"]?.Value?.ToString() ?? string.Empty,
                        Version = psObj.Properties["Version"]?.Value?.ToString() ?? string.Empty,
                        InstallerType = ParseInstallerType(
                            psObj.Properties["InstallerType"]?.Value?.ToString() ?? "exe"),
                        Description = psObj.Properties["Description"]?.Value?.ToString(),
                        Dependencies = ParseStringList(psObj.Properties["Dependencies"]?.Value),
                        IsInstalled = Convert.ToBoolean(psObj.Properties["Installed"]?.Value ?? false)
                    });
                }

                _logger.LogInformation("Retrieved {Count} applications", apps.Count);
                return apps;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to list available applications");
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

        public async Task<InstallResult> InstallAppAsync(string appId, bool force = false, bool skipDependencies = false)
        {
            try
            {
                _logger.LogInformation("Installing application: {AppId}", appId);

                var parameters = new Dictionary<string, object>
                {
                    { "AppId", appId },
                    { "Force", force },
                    { "SkipDependencies", skipDependencies }
                };

                var result = await _psExecutor.ExecuteCommandAsync("Install-Better11App", parameters);

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
                    Status = output?.Properties["Status"]?.Value?.ToString() ?? "Unknown"
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to install application: {AppId}", appId);
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
    }
}
