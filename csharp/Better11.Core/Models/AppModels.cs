using System;
using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace Better11.Core.Models
{
    /// <summary>
    /// Type of installer package.
    /// </summary>
    [JsonConverter(typeof(JsonStringEnumConverter))]
    public enum InstallerType
    {
        [JsonPropertyName("msi")]
        MSI,
        [JsonPropertyName("exe")]
        EXE,
        [JsonPropertyName("appx")]
        APPX
    }

    /// <summary>
    /// Metadata for a vetted application in the catalog.
    /// </summary>
    public class AppMetadata
    {
        [JsonPropertyName("app_id")]
        public string AppId { get; set; } = string.Empty;

        [JsonPropertyName("name")]
        public string Name { get; set; } = string.Empty;

        [JsonPropertyName("version")]
        public string Version { get; set; } = string.Empty;

        [JsonPropertyName("uri")]
        public string Uri { get; set; } = string.Empty;

        [JsonPropertyName("sha256")]
        public string Sha256 { get; set; } = string.Empty;

        [JsonPropertyName("installer_type")]
        public string InstallerTypeString { get; set; } = "exe";

        [JsonIgnore]
        public InstallerType InstallerType => InstallerTypeString.ToLowerInvariant() switch
        {
            "msi" => InstallerType.MSI,
            "exe" => InstallerType.EXE,
            "appx" => InstallerType.APPX,
            _ => InstallerType.EXE
        };

        [JsonPropertyName("vetted_domains")]
        public List<string> VettedDomains { get; set; } = new();

        [JsonPropertyName("signature")]
        public string? Signature { get; set; }

        [JsonPropertyName("signature_key")]
        public string? SignatureKey { get; set; }

        [JsonPropertyName("dependencies")]
        public List<string> Dependencies { get; set; } = new();

        [JsonPropertyName("silent_args")]
        public List<string> SilentArgs { get; set; } = new();

        [JsonPropertyName("uninstall_command")]
        public string? UninstallCommand { get; set; }

        /// <summary>
        /// Checks if a domain is in the vetted domains list.
        /// </summary>
        public bool IsDomainVetted(string hostname)
        {
            var normalized = hostname.ToLowerInvariant();
            return VettedDomains.Exists(d => d.ToLowerInvariant() == normalized);
        }

        /// <summary>
        /// Whether signature verification is required.
        /// </summary>
        public bool RequiresSignatureVerification => !string.IsNullOrEmpty(Signature) && !string.IsNullOrEmpty(SignatureKey);
    }

    /// <summary>
    /// Status of an installed application.
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

        [JsonPropertyName("install_date")]
        public DateTime? InstallDate { get; set; }
    }

    /// <summary>
    /// Result of an installer execution.
    /// </summary>
    public class InstallerResult
    {
        public List<string> Command { get; set; } = new();
        public int ExitCode { get; set; }
        public string StandardOutput { get; set; } = string.Empty;
        public string StandardError { get; set; } = string.Empty;
        public bool Success => ExitCode == 0;
    }

    /// <summary>
    /// Application catalog containing vetted applications.
    /// </summary>
    public class AppCatalog
    {
        [JsonPropertyName("applications")]
        public List<AppMetadata> Applications { get; set; } = new();
    }
}
