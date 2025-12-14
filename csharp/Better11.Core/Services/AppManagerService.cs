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
                        AppId = psObj.Properties["AppId"]?.Value?.ToString() ?? string.Empty,
                        Name = psObj.Properties["Name"]?.Value?.ToString() ?? string.Empty,
                        Version = psObj.Properties["Version"]?.Value?.ToString() ?? string.Empty,
                        InstallerType = ParseInstallerType(
                            psObj.Properties["InstallerType"]?.Value?.ToString() ?? "exe"),
                        Description = psObj.Properties["Description"]?.Value?.ToString(),
                        Dependencies = ParseStringList(psObj.Properties["Dependencies"]?.Value)
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
                    "Get-Better11AppStatus", 
                    parameters);
                
                var statuses = new List<AppStatus>();
                
                foreach (var item in result.Output)
                {
                    var psObj = item as PSObject;
                    if (psObj == null) continue;
                    
                    statuses.Add(new AppStatus
                    {
                        AppId = psObj.Properties["AppId"]?.Value?.ToString() ?? string.Empty,
                        Version = psObj.Properties["Version"]?.Value?.ToString() ?? string.Empty,
                        Installed = Convert.ToBoolean(psObj.Properties["Installed"]?.Value ?? false),
                        InstallerPath = psObj.Properties["InstallerPath"]?.Value?.ToString() ?? string.Empty
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
