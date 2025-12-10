using System.Collections.Generic;
using System.Threading.Tasks;
using Better11.Core.Models;

namespace Better11.Core.Interfaces
{
    /// <summary>
    /// Interface for application management service.
    /// </summary>
    public interface IAppManager
    {
        /// <summary>
        /// Lists all available applications from the catalog.
        /// </summary>
        Task<List<AppMetadata>> ListAvailableAppsAsync();

        /// <summary>
        /// Installs an application and its dependencies.
        /// </summary>
        Task<InstallResult> InstallAppAsync(string appId, bool force = false, bool skipDependencies = false);

        /// <summary>
        /// Uninstalls an application.
        /// </summary>
        Task<UninstallResult> UninstallAppAsync(string appId, bool force = false);

        /// <summary>
        /// Gets the installation status of applications.
        /// </summary>
        Task<List<AppStatus>> GetAppStatusAsync(string? appId = null);

        /// <summary>
        /// Checks for available updates for installed applications.
        /// </summary>
        Task<List<AppMetadata>> CheckForUpdatesAsync();
    }
}
