namespace Better11.Core.Apps.Models;

/// <summary>
/// Status of a digital signature.
/// </summary>
public enum SignatureStatus
{
    Valid,
    Invalid,
    Unsigned,
    Revoked,
    Expired,
    Untrusted
}

/// <summary>
/// Certificate information extracted from signed file.
/// </summary>
public class CertificateInfo
{
    public required string Subject { get; init; }
    public required string Issuer { get; init; }
    public required string SerialNumber { get; init; }
    public required string Thumbprint { get; init; }
    public required DateTime ValidFrom { get; init; }
    public required DateTime ValidTo { get; init; }

    public bool IsExpired()
    {
        return DateTime.Now > ValidTo;
    }
}

/// <summary>
/// Complete signature information for a file.
/// </summary>
public class SignatureInfo
{
    public required SignatureStatus Status { get; init; }
    public CertificateInfo? Certificate { get; init; }
    public DateTime? Timestamp { get; init; }
    public string? HashAlgorithm { get; init; }
    public string? ErrorMessage { get; init; }

    public bool IsTrusted()
    {
        return Status == SignatureStatus.Valid;
    }
}
