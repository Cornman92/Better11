namespace Better11.Core.Models
{
    /// <summary>
    /// Represents a Windows optional feature.
    /// </summary>
    public class WindowsFeature
    {
        public string FeatureName { get; set; } = string.Empty;
        public string DisplayName { get; set; } = string.Empty;
        public string? Description { get; set; }
        public FeatureState State { get; set; }
        public bool RestartRequired { get; set; }
    }

    public enum FeatureState
    {
        Enabled,
        Disabled,
        EnablePending,
        DisablePending
    }

    /// <summary>
    /// Result of a Windows feature operation.
    /// </summary>
    public class FeatureResult
    {
        public bool Success { get; set; }
        public string FeatureName { get; set; } = string.Empty;
        public bool RestartRequired { get; set; }
        public string? ErrorMessage { get; set; }
    }
}
