using System.Collections.Generic;
using System.Threading.Tasks;
using Better11.Core.Models;

namespace Better11.Core.Interfaces
{
    /// <summary>
    /// Interface for scheduled tasks management.
    /// </summary>
    public interface ITasksService
    {
        /// <summary>
        /// Gets scheduled tasks.
        /// </summary>
        Task<List<ScheduledTaskInfo>> GetScheduledTasksAsync(string? pathFilter = null, TaskState? stateFilter = null);

        /// <summary>
        /// Enables a scheduled task.
        /// </summary>
        Task<bool> EnableScheduledTaskAsync(string taskName, string taskPath = "\\");

        /// <summary>
        /// Disables a scheduled task.
        /// </summary>
        Task<bool> DisableScheduledTaskAsync(string taskName, string taskPath = "\\");

        /// <summary>
        /// Gets known telemetry tasks.
        /// </summary>
        Task<List<TelemetryTaskInfo>> GetTelemetryTasksAsync();

        /// <summary>
        /// Disables all known telemetry tasks.
        /// </summary>
        Task<bool> DisableTelemetryTasksAsync();

        /// <summary>
        /// Creates a new scheduled task.
        /// </summary>
        Task<bool> CreateScheduledTaskAsync(
            string name,
            string execute,
            TaskTriggerType triggerType,
            string? arguments = null,
            string? time = "03:00",
            string? path = "\\Better11\\");

        /// <summary>
        /// Removes a scheduled task.
        /// </summary>
        Task<bool> RemoveScheduledTaskAsync(string taskName, string taskPath = "\\Better11\\");
    }
}
