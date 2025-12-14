using System.Collections.Generic;
using System.Threading.Tasks;
using Better11.Core.Models;

namespace Better11.Core.Interfaces
{
    /// <summary>
    /// Service for managing application installation and updates.
    /// </summary>
    public interface IAppManagerService
    {
        /// <summary>
        /// Lists all available applications from the catalog.
        /// </summary>
        Task<List<AppMetadata>> ListAvailableAppsAsync();

        /// <summary>
        /// Lists installed applications.
        /// </summary>
        Task<List<AppMetadata>> ListInstalledAppsAsync();

        /// <summary>
        /// Gets the status of a specific application.
        /// </summary>
        Task<AppStatus?> GetAppStatusAsync(string appId);

        /// <summary>
        /// Installs an application and its dependencies.
        /// </summary>
        Task<InstallResult> InstallAppAsync(string appId, bool force = false, bool skipDependencies = false);

        /// <summary>
        /// Uninstalls an application.
        /// </summary>
        Task<UninstallResult> UninstallAppAsync(string appId, bool force = false);

        /// <summary>
        /// Updates an application to the latest version.
        /// </summary>
        Task<InstallResult> UpdateAppAsync(string appId);

        /// <summary>
        /// Downloads an application installer without installing.
        /// </summary>
        Task<DownloadResult> DownloadAppAsync(string appId);
    }
}
