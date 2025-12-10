using System;
using System.Collections.Generic;
using System.IO;
using System.Threading.Tasks;
using Better11.Core.Models;

namespace Better11.Core.Interfaces
{
    /// <summary>
    /// Interface for power management operations.
    /// </summary>
    public interface IPowerService
    {
        /// <summary>
        /// Lists all available power plans.
        /// </summary>
        /// <returns>List of power plans.</returns>
        Task<List<PowerPlan>> ListPowerPlansAsync();

        /// <summary>
        /// Gets the currently active power plan.
        /// </summary>
        /// <returns>Active power plan, or null if not found.</returns>
        Task<PowerPlan?> GetActivePlanAsync();

        /// <summary>
        /// Sets the active power plan.
        /// </summary>
        /// <param name="planGuid">GUID of the plan to activate.</param>
        /// <returns>True if successful.</returns>
        Task<bool> SetActivePlanAsync(string planGuid);

        /// <summary>
        /// Sets the active power plan by name.
        /// </summary>
        /// <param name="planName">Name of the plan to activate.</param>
        /// <returns>True if successful.</returns>
        Task<bool> SetActivePlanByNameAsync(string planName);

        /// <summary>
        /// Enables hibernation.
        /// </summary>
        /// <returns>True if successful.</returns>
        Task<bool> EnableHibernationAsync();

        /// <summary>
        /// Disables hibernation.
        /// </summary>
        /// <returns>True if successful.</returns>
        Task<bool> DisableHibernationAsync();

        /// <summary>
        /// Generates a battery health report.
        /// </summary>
        /// <param name="outputPath">Optional output path for the report.</param>
        /// <returns>Path to the generated report, or null if failed.</returns>
        Task<string?> GenerateBatteryReportAsync(string? outputPath = null);
    }
}
