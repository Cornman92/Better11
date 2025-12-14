namespace Better11.Core.Models
{
    /// <summary>
    /// Represents a privacy configuration setting.
    /// </summary>
    public class PrivacySetting
    {
        public string Name { get; set; } = string.Empty;
        public string Category { get; set; } = string.Empty;
        public string? Description { get; set; }
        public bool Enabled { get; set; }
        public PrivacyLevel? Level { get; set; }
    }

    public enum TelemetryLevel
    {
        Security = 0,
        Basic = 1,
        Enhanced = 2,
        Full = 3
    }

    public enum PrivacyLevel
    {
        High,
        Medium,
        Low
    }

    /// <summary>
    /// Result of applying privacy settings.
    /// </summary>
    public class PrivacyResult
    {
        public bool Success { get; set; }
        public int SettingsApplied { get; set; }
        public string? ErrorMessage { get; set; }
    }
}
