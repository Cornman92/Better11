using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Better11.Core.Interfaces;
using Better11.Core.Models;
using Better11.Core.PowerShell;
using Microsoft.Extensions.Logging;

namespace Better11.Core.Services
{
    /// <summary>
    /// Service for scheduled tasks management.
    /// </summary>
    public class TasksService : ITasksService
    {
        private readonly PowerShellExecutor _psExecutor;
        private readonly ILogger<TasksService> _logger;

        public TasksService(PowerShellExecutor psExecutor, ILogger<TasksService> logger)
        {
            _psExecutor = psExecutor;
            _logger = logger;
        }

        /// <inheritdoc/>
        public async Task<List<ScheduledTaskInfo>> GetScheduledTasksAsync(string? pathFilter = null, TaskState? stateFilter = null)
        {
            try
            {
                _logger.LogInformation("Getting scheduled tasks");

                var parameters = new Dictionary<string, object>();
                if (!string.IsNullOrEmpty(pathFilter))
                {
                    parameters["Path"] = pathFilter;
                }
                if (stateFilter.HasValue)
                {
                    parameters["State"] = stateFilter.Value.ToString();
                }
                else
                {
                    parameters["State"] = "All";
                }

                var result = await _psExecutor.ExecuteCommandAsync("Get-Better11ScheduledTasks", parameters);
                var tasks = new List<ScheduledTaskInfo>();

                if (result.Success)
                {
                    foreach (var item in result.Output)
                    {
                        dynamic task = item;
                        tasks.Add(new ScheduledTaskInfo
                        {
                            Name = task.Name?.ToString() ?? "",
                            Path = task.Path?.ToString() ?? "",
                            State = ParseTaskState(task.State?.ToString()),
                            Description = task.Description?.ToString(),
                            Author = task.Author?.ToString(),
                            LastRun = task.LastRun,
                            NextRun = task.NextRun,
                            LastResult = task.LastResult
                        });
                    }
                }

                return tasks;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get scheduled tasks");
                return new List<ScheduledTaskInfo>();
            }
        }

        /// <inheritdoc/>
        public async Task<bool> EnableScheduledTaskAsync(string taskName, string taskPath = "\\")
        {
            try
            {
                _logger.LogInformation("Enabling task: {Path}{Name}", taskPath, taskName);

                var result = await _psExecutor.ExecuteCommandAsync(
                    "Enable-Better11ScheduledTask",
                    new() { { "Name", taskName }, { "Path", taskPath } });

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to enable task");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> DisableScheduledTaskAsync(string taskName, string taskPath = "\\")
        {
            try
            {
                _logger.LogInformation("Disabling task: {Path}{Name}", taskPath, taskName);

                var result = await _psExecutor.ExecuteCommandAsync(
                    "Disable-Better11ScheduledTask",
                    new() { { "Name", taskName }, { "Path", taskPath } });

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to disable task");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<List<TelemetryTaskInfo>> GetTelemetryTasksAsync()
        {
            try
            {
                _logger.LogInformation("Getting telemetry tasks");

                var result = await _psExecutor.ExecuteCommandAsync("Get-Better11TelemetryTasks");
                var tasks = new List<TelemetryTaskInfo>();

                if (result.Success)
                {
                    foreach (var item in result.Output)
                    {
                        dynamic task = item;
                        tasks.Add(new TelemetryTaskInfo
                        {
                            Name = task.Name?.ToString() ?? "",
                            Path = task.Path?.ToString() ?? "",
                            State = task.State?.ToString() ?? "",
                            Exists = task.Exists ?? false,
                            Description = task.Description?.ToString()
                        });
                    }
                }

                return tasks;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get telemetry tasks");
                return new List<TelemetryTaskInfo>();
            }
        }

        /// <inheritdoc/>
        public async Task<bool> DisableTelemetryTasksAsync()
        {
            try
            {
                _logger.LogInformation("Disabling all telemetry tasks");

                var result = await _psExecutor.ExecuteCommandAsync("Disable-Better11TelemetryTasks");

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to disable telemetry tasks");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> CreateScheduledTaskAsync(
            string name,
            string execute,
            TaskTriggerType triggerType,
            string? arguments = null,
            string? time = "03:00",
            string? path = "\\Better11\\")
        {
            try
            {
                _logger.LogInformation("Creating scheduled task: {Name}", name);

                var parameters = new Dictionary<string, object>
                {
                    { "Name", name },
                    { "Execute", execute },
                    { "TriggerType", triggerType.ToString() }
                };

                if (!string.IsNullOrEmpty(arguments))
                {
                    parameters["Arguments"] = arguments;
                }
                if (!string.IsNullOrEmpty(time))
                {
                    parameters["Time"] = time;
                }
                if (!string.IsNullOrEmpty(path))
                {
                    parameters["Path"] = path;
                }

                var result = await _psExecutor.ExecuteCommandAsync("New-Better11ScheduledTask", parameters);

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to create scheduled task");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> RemoveScheduledTaskAsync(string taskName, string taskPath = "\\Better11\\")
        {
            try
            {
                _logger.LogInformation("Removing task: {Path}{Name}", taskPath, taskName);

                var result = await _psExecutor.ExecuteCommandAsync(
                    "Remove-Better11ScheduledTask",
                    new() { { "Name", taskName }, { "Path", taskPath } });

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to remove task");
                return false;
            }
        }

        private static TaskState ParseTaskState(string? state)
        {
            return state?.ToLower() switch
            {
                "disabled" => TaskState.Disabled,
                "queued" => TaskState.Queued,
                "ready" => TaskState.Ready,
                "running" => TaskState.Running,
                _ => TaskState.Unknown
            };
        }
    }
}
