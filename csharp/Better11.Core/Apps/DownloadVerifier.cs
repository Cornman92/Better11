using System.Security.Cryptography;
using System.Text;
using Better11.Core.Apps.Models;

namespace Better11.Core.Apps;

/// <summary>
/// Performs integrity and signature validation for downloaded installers.
/// </summary>
public class DownloadVerifier
{
    public async Task<string> VerifyHashAsync(string filePath, string expectedSha256)
    {
        using var sha256 = SHA256.Create();
        await using var fileStream = File.OpenRead(filePath);
        var hashBytes = sha256.ComputeHash(fileStream);
        var actual = Convert.ToHexString(hashBytes).ToLowerInvariant();

        if (actual != expectedSha256.ToLowerInvariant())
        {
            throw new VerificationException(
                $"Hash mismatch for {Path.GetFileName(filePath)}: expected {expectedSha256}, got {actual}");
        }

        return actual;
    }

    public async Task VerifySignatureAsync(string filePath, string signatureB64, string keyB64)
    {
        var key = Convert.FromBase64String(keyB64);
        var provided = Convert.FromBase64String(signatureB64);

        using var sha256 = SHA256.Create();
        await using var fileStream = File.OpenRead(filePath);
        var hashBytes = sha256.ComputeHash(fileStream);

        using var hmac = new HMACSHA256(key);
        var expected = hmac.ComputeHash(hashBytes);

        if (!CryptographicOperations.FixedTimeEquals(expected, provided))
        {
            throw new VerificationException("Signature validation failed");
        }
    }

    public async Task VerifyAsync(AppMetadata metadata, string filePath)
    {
        await VerifyHashAsync(filePath, metadata.Sha256);
        if (metadata.RequiresSignatureVerification())
        {
            try
            {
                await VerifySignatureAsync(filePath, metadata.Signature!, metadata.SignatureKey!);
            }
            catch (Exception ex)
            {
                throw new VerificationException($"Signature check failed for {metadata.AppId}", ex);
            }
        }
    }
}

/// <summary>
/// Exception thrown when verification fails.
/// </summary>
public class VerificationException : Exception
{
    public VerificationException(string message) : base(message) { }
    public VerificationException(string message, Exception innerException) : base(message, innerException) { }
}
