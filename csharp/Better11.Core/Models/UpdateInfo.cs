using System;

namespace Better11.Core.Models
{
    /// <summary>
    /// Represents a Windows update.
    /// </summary>
    public class UpdateInfo
    {
        public string UpdateId { get; set; } = string.Empty;
        public string Title { get; set; } = string.Empty;
        public string? Description { get; set; }
        public long SizeBytes { get; set; }
        public UpdateState State { get; set; }
        public bool IsDownloaded { get; set; }
        public bool IsMandatory { get; set; }
        public DateTime? LastDeploymentChangeTime { get; set; }
    }

    public enum UpdateState
    {
        NotStarted,
        Downloading,
        Downloaded,
        Installing,
        Installed,
        Failed
    }

    /// <summary>
    /// Result of an update operation.
    /// </summary>
    public class UpdateResult
    {
        public bool Success { get; set; }
        public int UpdatesInstalled { get; set; }
        public bool RestartRequired { get; set; }
        public string? ErrorMessage { get; set; }
    }

    /// <summary>
    /// Windows Update policy configuration.
    /// </summary>
    public class UpdatePolicy
    {
        public bool AutomaticUpdates { get; set; }
        public int DeferFeatureUpdatesDays { get; set; }
        public int DeferQualityUpdatesDays { get; set; }
        public bool PauseUpdates { get; set; }
        public DateTime? PauseUntil { get; set; }
    }
}
