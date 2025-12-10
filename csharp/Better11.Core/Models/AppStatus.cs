using System;
using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace Better11.Core.Models
{
    /// <summary>
    /// Represents the installation status of an application.
    /// </summary>
    public class AppStatus
    {
        [JsonPropertyName("app_id")]
        public string AppId { get; set; } = string.Empty;

        [JsonPropertyName("version")]
        public string Version { get; set; } = string.Empty;

        [JsonPropertyName("installer_path")]
        public string InstallerPath { get; set; } = string.Empty;

        [JsonPropertyName("installed")]
        public bool Installed { get; set; }

        [JsonPropertyName("dependencies_installed")]
        public List<string> DependenciesInstalled { get; set; } = new();

        [JsonPropertyName("installed_date")]
        public DateTime? InstalledDate { get; set; }
    }

    /// <summary>
    /// Result of an installation operation.
    /// </summary>
    public class InstallResult
    {
        public bool Success { get; set; }
        public string AppId { get; set; } = string.Empty;
        public string Version { get; set; } = string.Empty;
        public string Status { get; set; } = string.Empty;
        public string? ErrorMessage { get; set; }
        public int? ExitCode { get; set; }
    }

    /// <summary>
    /// Result of an uninstall operation.
    /// </summary>
    public class UninstallResult
    {
        public bool Success { get; set; }
        public string AppId { get; set; } = string.Empty;
        public string? ErrorMessage { get; set; }
        public int? ExitCode { get; set; }
    }
}
