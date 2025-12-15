using System.Collections.Generic;
using System.Threading.Tasks;
using Better11.Core.Models;

namespace Better11.Core.Interfaces
{
    public interface IAppManager
    {
        Task<List<AppMetadata>> ListAvailableAppsAsync();
        
        Task<InstallResult> InstallAppAsync(
            string appId, 
            bool force = false, 
            bool skipDependencies = false);
            
        Task<UninstallResult> UninstallAppAsync(string appId, bool force = false);
        
        Task<List<AppStatus>> GetAppStatusAsync(string? appId = null);
    }
}
