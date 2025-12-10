using System;
using System.Collections.Generic;

namespace Better11.Core.Models
{
    /// <summary>
    /// Represents a Windows Update item.
    /// </summary>
    public class WindowsUpdate
    {
        public string UpdateId { get; set; } = string.Empty;
        public string Title { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public string Type { get; set; } = string.Empty;
        public long SizeBytes { get; set; }
        public double SizeMB => Math.Round(SizeBytes / 1024.0 / 1024.0, 2);
        public bool IsDownloaded { get; set; }
        public bool IsInstalled { get; set; }
        public bool IsMandatory { get; set; }
        public DateTime? ReleaseDate { get; set; }
        public List<string> KBArticleIds { get; set; } = new();
        public List<string> Categories { get; set; } = new();
    }

    /// <summary>
    /// Result of a Windows Update operation.
    /// </summary>
    public class UpdateOperationResult
    {
        public bool Success { get; set; }
        public string Message { get; set; } = string.Empty;
        public List<WindowsUpdate> Updates { get; set; } = new();
        public DateTime? PausedUntil { get; set; }
        public int UpdatesFound { get; set; }
        public int UpdatesInstalled { get; set; }
        public int UpdatesFailed { get; set; }
    }

    /// <summary>
    /// Windows Update service status.
    /// </summary>
    public class UpdateServiceStatus
    {
        public bool IsRunning { get; set; }
        public bool IsPaused { get; set; }
        public DateTime? PausedUntil { get; set; }
        public DateTime? LastCheckTime { get; set; }
        public DateTime? LastSuccessTime { get; set; }
        public int PendingUpdates { get; set; }
        public bool RebootRequired { get; set; }
    }
}
