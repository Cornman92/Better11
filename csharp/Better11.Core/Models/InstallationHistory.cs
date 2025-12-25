using System;

namespace Better11.Core.Models
{
    /// <summary>
    /// Represents a historical event in the application installation lifecycle.
    /// </summary>
    public class InstallationHistoryEntry
    {
        public required string EntryId { get; init; }
        public required string AppId { get; init; }
        public required string AppName { get; init; }
        public required string Version { get; init; }
        public required InstallationEventType EventType { get; init; }
        public required DateTime Timestamp { get; init; }
        public bool Success { get; init; }
        public string? ErrorMessage { get; init; }
        public string? UserName { get; init; }
        public TimeSpan? Duration { get; init; }
        public Dictionary<string, string> Metadata { get; init; } = new();
    }

    /// <summary>
    /// Types of installation events tracked in history.
    /// </summary>
    public enum InstallationEventType
    {
        Install,
        Uninstall,
        Update,
        Download,
        Verify
    }

    /// <summary>
    /// Summary of installation history for an application.
    /// </summary>
    public class InstallationHistorySummary
    {
        public required string AppId { get; init; }
        public DateTime? FirstInstalled { get; init; }
        public DateTime? LastInstalled { get; init; }
        public DateTime? LastUninstalled { get; init; }
        public DateTime? LastUpdated { get; init; }
        public int TotalInstallations { get; init; }
        public int TotalUninstallations { get; init; }
        public int FailedOperations { get; init; }
        public List<InstallationHistoryEntry> RecentEvents { get; init; } = new();
    }

    /// <summary>
    /// Filter criteria for querying installation history.
    /// </summary>
    public class InstallationHistoryFilter
    {
        public string? AppId { get; set; }
        public InstallationEventType? EventType { get; set; }
        public DateTime? StartDate { get; set; }
        public DateTime? EndDate { get; set; }
        public bool? SuccessOnly { get; set; }
        public int? Limit { get; set; }
    }
}
