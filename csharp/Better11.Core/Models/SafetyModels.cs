using System;

namespace Better11.Core.Models
{
    /// <summary>
    /// System restore point information.
    /// </summary>
    public class RestorePoint
    {
        public int SequenceNumber { get; set; }
        public string Description { get; set; } = string.Empty;
        public DateTime CreationTime { get; set; }
        public RestorePointType Type { get; set; }
    }

    /// <summary>
    /// Restore point type.
    /// </summary>
    public enum RestorePointType
    {
        ApplicationInstall = 0,
        ApplicationUninstall = 1,
        DeviceDriverInstall = 10,
        ModifySettings = 12,
        CancelledOperation = 13
    }

    /// <summary>
    /// Registry backup result.
    /// </summary>
    public class RegistryBackupResult
    {
        public bool Success { get; set; }
        public string Path { get; set; } = string.Empty;
        public string RegistryKey { get; set; } = string.Empty;
        public DateTime Timestamp { get; set; }
        public string? Error { get; set; }
    }

    /// <summary>
    /// Operation result with safety information.
    /// </summary>
    public class SafetyOperationResult
    {
        public bool Success { get; set; }
        public string Operation { get; set; } = string.Empty;
        public bool BackupCreated { get; set; }
        public string? BackupPath { get; set; }
        public string? Error { get; set; }
    }
}
