using System;
using System.Collections.Generic;

namespace Better11.Core.Models
{
    /// <summary>
    /// Windows Update information.
    /// </summary>
    public class WindowsUpdate
    {
        public string Title { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public string KBNumber { get; set; } = string.Empty;
        public DateTime? Date { get; set; }
        public long SizeBytes { get; set; }
        public bool IsImportant { get; set; }
        public bool IsCritical { get; set; }
        public bool IsDriver { get; set; }
        public bool IsInstalled { get; set; }
        public bool IsHidden { get; set; }
    }

    /// <summary>
    /// Windows Update settings.
    /// </summary>
    public class UpdateSettings
    {
        public int ActiveHoursStart { get; set; }
        public int ActiveHoursEnd { get; set; }
        public bool AutomaticUpdatesEnabled { get; set; }
        public DateTime? PausedUntil { get; set; }
        public bool RestartPending { get; set; }
    }

    /// <summary>
    /// Update history entry.
    /// </summary>
    public class UpdateHistoryEntry
    {
        public string Title { get; set; } = string.Empty;
        public string KBNumber { get; set; } = string.Empty;
        public DateTime InstalledOn { get; set; }
        public string Result { get; set; } = string.Empty;
        public string Category { get; set; } = string.Empty;
    }
}
