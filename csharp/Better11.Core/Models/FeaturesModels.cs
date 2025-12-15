using System;

namespace Better11.Core.Models
{
    /// <summary>
    /// Windows optional feature information.
    /// </summary>
    public class OptionalFeature
    {
        public string Name { get; set; } = string.Empty;
        public FeatureState State { get; set; }
        public bool RestartRequired { get; set; }
        public string? Description { get; set; }
    }

    /// <summary>
    /// Optional feature state.
    /// </summary>
    public enum FeatureState
    {
        Enabled,
        Disabled,
        EnablePending,
        DisablePending
    }

    /// <summary>
    /// Windows capability information.
    /// </summary>
    public class WindowsCapability
    {
        public string Name { get; set; } = string.Empty;
        public CapabilityState State { get; set; }
        public string DisplayName { get; set; } = string.Empty;
    }

    /// <summary>
    /// Capability state.
    /// </summary>
    public enum CapabilityState
    {
        Installed,
        NotPresent,
        Staged
    }
}
