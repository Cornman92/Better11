using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Better11.Core.Models;

namespace Better11.Core.Interfaces
{
    /// <summary>
    /// Interface for application management operations.
    /// </summary>
    public interface IAppService
    {
        /// <summary>
        /// Lists all available applications from the catalog.
        /// </summary>
        /// <returns>List of available applications.</returns>
        Task<List<AppMetadata>> ListAvailableAsync();

        /// <summary>
        /// Gets a specific application from the catalog.
        /// </summary>
        /// <param name="appId">Application identifier.</param>
        /// <returns>Application metadata, or null if not found.</returns>
        Task<AppMetadata?> GetAppAsync(string appId);

        /// <summary>
        /// Downloads an application installer.
        /// </summary>
        /// <param name="appId">Application identifier.</param>
        /// <returns>Path to the downloaded installer.</returns>
        Task<string> DownloadAsync(string appId);

        /// <summary>
        /// Installs an application.
        /// </summary>
        /// <param name="appId">Application identifier.</param>
        /// <returns>Tuple of installation status and result.</returns>
        Task<(AppStatus Status, InstallerResult Result)> InstallAsync(string appId);

        /// <summary>
        /// Uninstalls an application.
        /// </summary>
        /// <param name="appId">Application identifier.</param>
        /// <returns>Uninstallation result.</returns>
        Task<InstallerResult> UninstallAsync(string appId);

        /// <summary>
        /// Gets the status of installed applications.
        /// </summary>
        /// <param name="appId">Optional specific application ID.</param>
        /// <returns>List of application statuses.</returns>
        Task<List<AppStatus>> GetStatusAsync(string? appId = null);

        /// <summary>
        /// Verifies an installer file against the catalog.
        /// </summary>
        /// <param name="appId">Application identifier.</param>
        /// <param name="installerPath">Path to installer file.</param>
        /// <returns>True if verification passes.</returns>
        Task<bool> VerifyInstallerAsync(string appId, string installerPath);
    }
}
