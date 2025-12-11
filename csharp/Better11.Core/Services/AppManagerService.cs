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
    /// Communicates with PowerShell backend to perform operations.
    /// </summary>
    public class AppManagerService : IAppManager
    {
        private readonly PowerShellExecutor _psExecutor;
        private readonly ILogger<AppManagerService> _logger;

        public AppManagerService(
            PowerShellExecutor psExecutor,
            ILogger<AppManagerService> logger)
        {
            _psExecutor = psExecutor;
            _logger = logger;
        }

        /// <summary>
        /// Lists all available applications from the catalog.
        /// </summary>
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
                        AppId = GetPropertyValue<string>(psObj, "AppId") ?? string.Empty,
                        Name = GetPropertyValue<string>(psObj, "Name") ?? string.Empty,
                        Version = GetPropertyValue<string>(psObj, "Version") ?? string.Empty,
                        InstallerType = GetPropertyValue<string>(psObj, "InstallerType") ?? "exe",
                        Description = GetPropertyValue<string>(psObj, "Description"),
                        Uri = GetPropertyValue<string>(psObj, "Uri") ?? string.Empty,
                        Sha256 = GetPropertyValue<string>(psObj, "Sha256") ?? string.Empty,
                        Dependencies = GetListProperty(psObj, "Dependencies"),
                        SilentArgs = GetListProperty(psObj, "SilentArgs"),
                        VettedDomains = GetListProperty(psObj, "VettedDomains")
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

        /// <summary>
        /// Installs an application and its dependencies.
        /// </summary>
        public async Task<InstallResult> InstallAppAsync(
            string appId,
            bool force = false,
            bool skipDependencies = false)
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

                var result = await _psExecutor.ExecuteCommandAsync(
                    "Install-Better11App",
                    parameters);

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
                    Success = GetPropertyValue<bool>(output, "Success"),
                    AppId = appId,
                    Version = GetPropertyValue<string>(output, "Version") ?? string.Empty,
                    Status = GetPropertyValue<string>(output, "Status") ?? "Unknown",
                    ExitCode = GetPropertyValue<int?>(output, "ExitCode")
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

        /// <summary>
        /// Uninstalls an application.
        /// </summary>
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

                var result = await _psExecutor.ExecuteCommandAsync(
                    "Uninstall-Better11App",
                    parameters);

                var output = result.Output.FirstOrDefault() as PSObject;

                return new UninstallResult
                {
                    Success = result.Success,
                    AppId = appId,
                    ErrorMessage = result.Success ? null : string.Join("\n", result.Errors),
                    ExitCode = GetPropertyValue<int?>(output, "ExitCode")
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

        /// <summary>
        /// Gets the installation status of all or specific applications.
        /// </summary>
        public async Task<List<AppStatus>> GetAppStatusAsync(string? appId = null)
        {
            try
            {
                var parameters = new Dictionary<string, object>();
                if (!string.IsNullOrEmpty(appId))
                {
                    parameters["AppId"] = appId;
                }

                var result = await _psExecutor.ExecuteCommandAsync(
                    "Get-Better11Apps",
                    new Dictionary<string, object> { { "Installed", true } });

                var statuses = new List<AppStatus>();

                foreach (var item in result.Output)
                {
                    var psObj = item as PSObject;
                    if (psObj == null) continue;

                    statuses.Add(new AppStatus
                    {
                        AppId = GetPropertyValue<string>(psObj, "AppId") ?? string.Empty,
                        Version = GetPropertyValue<string>(psObj, "InstalledVersion") ?? string.Empty,
                        Installed = GetPropertyValue<bool>(psObj, "Installed"),
                        InstallerPath = string.Empty
                    });
                }

                return statuses;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get application status");
                throw;
            }
        }

        /// <summary>
        /// Checks for available updates for installed applications.
        /// </summary>
        public async Task<List<AppMetadata>> CheckForUpdatesAsync()
        {
            try
            {
                // Get all apps and installed apps
                var allApps = await ListAvailableAppsAsync();
                var installedApps = await GetAppStatusAsync();

                // Find apps with updates
                var updates = new List<AppMetadata>();

                foreach (var installed in installedApps.Where(a => a.Installed))
                {
                    var catalogApp = allApps.FirstOrDefault(a => a.AppId == installed.AppId);
                    if (catalogApp != null && catalogApp.Version != installed.Version)
                    {
                        updates.Add(catalogApp);
                    }
                }

                return updates;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to check for updates");
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
                return (T?)Convert.ChangeType(property.Value, typeof(T));
            }
            catch
            {
                return default;
            }
        }

        private List<string> GetListProperty(PSObject? psObject, string propertyName)
        {
            if (psObject == null) return new List<string>();

            var property = psObject.Properties[propertyName];
            if (property?.Value == null) return new List<string>();

            if (property.Value is System.Collections.IEnumerable enumerable and not string)
            {
                return enumerable.Cast<object>().Select(o => o.ToString() ?? string.Empty).ToList();
            }

            return new List<string>();
        }
    }
}
