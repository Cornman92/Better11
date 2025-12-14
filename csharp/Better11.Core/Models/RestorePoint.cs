using System;

namespace Better11.Core.Models
{
    /// <summary>
    /// Represents a system restore point.
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
        public long? SizeBytes { get; set; }
        public string? ErrorMessage { get; set; }
    }
}
