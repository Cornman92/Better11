namespace Better11.Core.Apps.Models;

/// <summary>
/// Description of a vetted application installer.
/// </summary>
public class AppMetadata
{
    public required string AppId { get; init; }
    public required string Name { get; init; }
    public required string Version { get; init; }
    public required string Uri { get; init; }
    public required string Sha256 { get; init; }
    public required InstallerType InstallerType { get; init; }
    public List<string> VettedDomains { get; init; } = new();
    public string? Signature { get; init; }
    public string? SignatureKey { get; init; }
    public List<string> Dependencies { get; init; } = new();
    public List<string> SilentArgs { get; init; } = new();
    public string? UninstallCommand { get; init; }
    public List<string> Categories { get; init; } = new();
    public string? Description { get; init; }
    public bool IsInstalled { get; set; }

    public bool DomainIsVetted(string hostname)
    {
        var normalized = hostname.ToLowerInvariant();
        return VettedDomains.Any(d => normalized == d.ToLowerInvariant());
    }

    public bool RequiresSignatureVerification()
    {
        return !string.IsNullOrEmpty(Signature) && !string.IsNullOrEmpty(SignatureKey);
    }
}
