namespace Better11.Core.Models
{
    /// <summary>
    /// Represents a startup program.
    /// </summary>
    public class StartupItem
    {
        public string Name { get; set; } = string.Empty;
        public string Command { get; set; } = string.Empty;
        public StartupLocation Location { get; set; }
        public bool Enabled { get; set; }
        public string? Publisher { get; set; }
    }

    public enum StartupLocation
    {
        Registry,
        StartupFolder,
        TaskScheduler
    }
}
