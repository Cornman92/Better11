using System;

namespace Better11.Core.Models
{
    /// <summary>
    /// Scheduled task information.
    /// </summary>
    public class ScheduledTaskInfo
    {
        public string Name { get; set; } = string.Empty;
        public string Path { get; set; } = string.Empty;
        public TaskState State { get; set; }
        public string? Description { get; set; }
        public string? Author { get; set; }
        public DateTime? LastRun { get; set; }
        public DateTime? NextRun { get; set; }
        public int? LastResult { get; set; }
    }

    /// <summary>
    /// Scheduled task state.
    /// </summary>
    public enum TaskState
    {
        Unknown,
        Disabled,
        Queued,
        Ready,
        Running
    }

    /// <summary>
    /// Task trigger type.
    /// </summary>
    public enum TaskTriggerType
    {
        Daily,
        Weekly,
        AtStartup,
        AtLogon
    }

    /// <summary>
    /// Telemetry task status.
    /// </summary>
    public class TelemetryTaskInfo
    {
        public string Name { get; set; } = string.Empty;
        public string Path { get; set; } = string.Empty;
        public string State { get; set; } = string.Empty;
        public bool Exists { get; set; }
        public string? Description { get; set; }
    }
}
