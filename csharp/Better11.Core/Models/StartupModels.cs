using System;
using System.Text.Json.Serialization;

namespace Better11.Core.Models
{
    /// <summary>
    /// Location where startup items can be registered.
    /// </summary>
    public enum StartupLocation
    {
        RegistryCurrentUser,
        RegistryLocalMachine,
        StartupFolder,
        TaskScheduler
    }

    /// <summary>
    /// Represents a startup program.
    /// </summary>
    public class StartupItem
    {
        public string Name { get; set; } = string.Empty;
        public string Command { get; set; } = string.Empty;
        public StartupLocation Location { get; set; }
        public bool Enabled { get; set; } = true;
        public string? Publisher { get; set; }
        public string? Description { get; set; }
        public string? RegistryKey { get; set; }
        public string? FilePath { get; set; }
    }
}
