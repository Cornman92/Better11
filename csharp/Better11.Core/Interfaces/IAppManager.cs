using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Better11.Core.Apps.Models;
using Better11.Core.Models;

namespace Better11.Core.Interfaces
{
    public interface IAppManager
    {
        Task<List<AppMetadata>> ListAvailableAppsAsync();

        Task<InstallResult> InstallAppAsync(
            string appId,
            bool force = false,
            bool skipDependencies = false,
            IProgress<OperationProgress>? progress = null,
            CancellationToken cancellationToken = default);

        Task<UninstallResult> UninstallAppAsync(string appId, bool force = false);

        Task<List<AppStatus>> GetAppStatusAsync(string? appId = null);

        Task<InstallPlanSummary> GetInstallPlanAsync(string appId);

        Task<BatchOperationResult> BatchInstallAsync(
            IEnumerable<string> appIds,
            IProgress<OperationProgress>? progress = null,
            CancellationToken cancellationToken = default,
            bool continueOnError = true);

        Task<BatchOperationResult> BatchUninstallAsync(
            IEnumerable<string> appIds,
            bool continueOnError = true);
    }
}
