using System.Collections.Generic;

namespace Better11.Core.Models
{
    /// <summary>
    /// Represents a performance optimization preset.
    /// </summary>
    public class PerformancePreset
    {
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public List<RegistryTweak> RegistryTweaks { get; set; } = new();
        public List<ServiceAction> ServiceActions { get; set; } = new();
    }

    /// <summary>
    /// Result of applying a bloatware removal operation.
    /// </summary>
    public class RemovalResult
    {
        public bool Success { get; set; }
        public int PackagesRemoved { get; set; }
        public int PackagesFailed { get; set; }
        public string? ErrorMessage { get; set; }
    }

    /// <summary>
    /// Result of applying a performance preset.
    /// </summary>
    public class PresetResult
    {
        public bool Success { get; set; }
        public string PresetName { get; set; } = string.Empty;
        public int TweaksApplied { get; set; }
        public string? ErrorMessage { get; set; }
    }
}
