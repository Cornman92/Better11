using System;
using System.Collections.Generic;

namespace Better11.Core.Models
{
    /// <summary>
    /// Represents metadata for an application in the Better11 catalog.
    /// </summary>
    public class AppMetadata
    {
        public string AppId { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public string Version { get; set; } = string.Empty;
        public string Uri { get; set; } = string.Empty;
        public string Sha256 { get; set; } = string.Empty;
        public InstallerType InstallerType { get; set; }
        public List<string> VettedDomains { get; set; } = new();
        public string? Signature { get; set; }
        public string? SignatureKey { get; set; }
        public List<string> Dependencies { get; set; } = new();
        public List<string> SilentArgs { get; set; } = new();
        public string? UninstallCommand { get; set; }
        public string? Description { get; set; }
        
        public bool DomainIsVetted(string hostname)
        {
            var normalizedHost = hostname.ToLowerInvariant();
            return VettedDomains.Exists(d => 
                d.Equals(normalizedHost, StringComparison.OrdinalIgnoreCase));
        }
        
        public bool RequiresSignatureVerification()
        {
            return !string.IsNullOrEmpty(Signature) && !string.IsNullOrEmpty(SignatureKey);
        }
    }
    
    public enum InstallerType
    {
        MSI,
        EXE,
        APPX
    }
}
