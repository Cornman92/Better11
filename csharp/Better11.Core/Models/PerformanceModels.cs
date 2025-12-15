using System;

namespace Better11.Core.Models
{
    /// <summary>
    /// Performance optimization settings.
    /// </summary>
    public class PerformanceSettings
    {
        public string VisualEffects { get; set; } = string.Empty;
        public string MenuShowDelay { get; set; } = string.Empty;
        public string MouseHoverTime { get; set; } = string.Empty;
        public string PagingFileManaged { get; set; } = string.Empty;
        public int Win32PrioritySeparation { get; set; }
        public bool FastStartupEnabled { get; set; }
    }

    /// <summary>
    /// Visual effects preset levels.
    /// </summary>
    public enum VisualEffectsPreset
    {
        BestPerformance,
        BestAppearance,
        Balanced
    }

    /// <summary>
    /// Processor scheduling priority options.
    /// </summary>
    public enum ProcessorPriority
    {
        Programs,
        BackgroundServices
    }

    /// <summary>
    /// Performance optimization preset levels.
    /// </summary>
    public enum PerformancePreset
    {
        Maximum,
        Balanced,
        Default
    }

    /// <summary>
    /// Virtual memory settings.
    /// </summary>
    public class VirtualMemorySettings
    {
        public bool SystemManaged { get; set; }
        public string Drive { get; set; } = "C";
        public int InitialSizeMB { get; set; }
        public int MaximumSizeMB { get; set; }
    }
}
