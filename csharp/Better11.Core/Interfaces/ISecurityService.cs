using System.Threading.Tasks;
using Better11.Core.Models;

namespace Better11.Core.Interfaces
{
    /// <summary>
    /// Interface for security and verification service.
    /// </summary>
    public interface ISecurityService
    {
        /// <summary>
        /// Verifies the code signature of a file.
        /// </summary>
        Task<SignatureInfo> VerifyCodeSignatureAsync(string filePath, bool checkRevocation = false);

        /// <summary>
        /// Verifies the hash of a file.
        /// </summary>
        Task<HashVerificationResult> VerifyFileHashAsync(string filePath, string expectedHash, string algorithm = "SHA256");

        /// <summary>
        /// Creates a system restore point.
        /// </summary>
        Task<bool> CreateRestorePointAsync(string description);

        /// <summary>
        /// Backs up a registry key.
        /// </summary>
        Task<string> BackupRegistryKeyAsync(string keyPath, string? destination = null);
    }
}
