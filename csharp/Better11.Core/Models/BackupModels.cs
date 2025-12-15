using System;
using System.Collections.Generic;

namespace Better11.Core.Models
{
    /// <summary>
    /// Represents a Windows system restore point.
    /// </summary>
    public class RestorePoint
    {
        public int SequenceNumber { get; set; }
        public string Description { get; set; } = string.Empty;
        public DateTime CreationTime { get; set; }
        public string RestorePointType { get; set; } = string.Empty;
    }

    /// <summary>
    /// Result of a backup operation.
    /// </summary>
    public class BackupResult
    {
        public bool Success { get; set; }
        public string? BackupPath { get; set; }
        public string? Message { get; set; }
        public DateTime Timestamp { get; set; } = DateTime.UtcNow;
        public List<string> FilesBackedUp { get; set; } = new();
    }

    /// <summary>
    /// Settings export configuration.
    /// </summary>
    public class SettingsExport
    {
        public DateTime ExportDate { get; set; } = DateTime.UtcNow;
        public string Version { get; set; } = "1.0";
        public Dictionary<string, object> Settings { get; set; } = new();
    }
}
