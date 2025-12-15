using System.Collections.Generic;
using System.Threading.Tasks;
using Better11.Core.Models;

namespace Better11.Core.Interfaces
{
    /// <summary>
    /// Service for managing Windows updates.
    /// </summary>
    public interface IUpdateService
    {
        /// <summary>
        /// Lists available Windows updates.
        /// </summary>
        Task<List<UpdateInfo>> ListUpdatesAsync();

        /// <summary>
        /// Installs Windows updates.
        /// </summary>
        Task<UpdateResult> InstallUpdatesAsync(List<string> updateIds, bool force = false);

        /// <summary>
        /// Pauses Windows updates.
        /// </summary>
        Task<bool> PauseUpdatesAsync(int days);

        /// <summary>
        /// Resumes Windows updates.
        /// </summary>
        Task<bool> ResumeUpdatesAsync();

        /// <summary>
        /// Gets the current update policy.
        /// </summary>
        Task<UpdatePolicy> GetUpdatePolicyAsync();

        /// <summary>
        /// Sets the update policy.
        /// </summary>
        Task<bool> SetUpdatePolicyAsync(UpdatePolicy policy);
    }
}
