using System;
using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace Better11.Core.Models
{
    /// <summary>
    /// Represents metadata for an application in the Better11 catalog.
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
        public string InstallerType { get; set; } = "exe";

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

        [JsonPropertyName("description")]
        public string? Description { get; set; }

        /// <summary>
        /// Checks if the specified hostname is in the vetted domains list.
        /// </summary>
        public bool DomainIsVetted(string hostname)
        {
            var normalizedHost = hostname.ToLowerInvariant();
            return VettedDomains.Exists(d =>
                d.Equals(normalizedHost, StringComparison.OrdinalIgnoreCase));
        }

        /// <summary>
        /// Checks if this application requires signature verification.
        /// </summary>
        public bool RequiresSignatureVerification()
        {
            return !string.IsNullOrEmpty(Signature) && !string.IsNullOrEmpty(SignatureKey);
        }
    }

    /// <summary>
    /// Installer type enumeration.
    /// </summary>
    public enum InstallerTypeEnum
    {
        MSI,
        EXE,
        APPX
    }
}
