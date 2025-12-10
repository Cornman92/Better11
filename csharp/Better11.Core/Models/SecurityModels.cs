using System;

namespace Better11.Core.Models
{
    /// <summary>
    /// Signature verification status.
    /// </summary>
    public enum SignatureStatus
    {
        Valid,
        Invalid,
        Unsigned,
        Revoked,
        Expired,
        Untrusted,
        Unknown
    }

    /// <summary>
    /// Certificate information.
    /// </summary>
    public class CertificateInfo
    {
        public string Subject { get; set; } = string.Empty;
        public string Issuer { get; set; } = string.Empty;
        public string SerialNumber { get; set; } = string.Empty;
        public string Thumbprint { get; set; } = string.Empty;
        public DateTime ValidFrom { get; set; }
        public DateTime ValidTo { get; set; }
        public bool IsExpired => DateTime.Now > ValidTo;
        public string? FriendlyName { get; set; }
    }

    /// <summary>
    /// Code signature information.
    /// </summary>
    public class SignatureInfo
    {
        public SignatureStatus Status { get; set; }
        public CertificateInfo? Certificate { get; set; }
        public DateTime? Timestamp { get; set; }
        public string? HashAlgorithm { get; set; }
        public string? StatusMessage { get; set; }
        public bool IsTrusted => Status == SignatureStatus.Valid;
        public bool IsSigned => Status != SignatureStatus.Unsigned;
    }

    /// <summary>
    /// File hash verification result.
    /// </summary>
    public class HashVerificationResult
    {
        public string FilePath { get; set; } = string.Empty;
        public string Algorithm { get; set; } = string.Empty;
        public string ComputedHash { get; set; } = string.Empty;
        public string ExpectedHash { get; set; } = string.Empty;
        public bool IsMatch { get; set; }
        public long FileSize { get; set; }
    }
}
