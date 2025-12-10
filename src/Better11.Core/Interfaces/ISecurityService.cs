using Better11.Core.Models;

namespace Better11.Core.Interfaces;

/// <summary>
/// Service for security-related operations.
/// </summary>
public interface ISecurityService
{
    /// <summary>
    /// Checks if the current process is running with administrator privileges.
    /// </summary>
    /// <returns>True if running as administrator; otherwise, false.</returns>
    bool IsAdministrator();

    /// <summary>
    /// Requests UAC elevation for the current process.
    /// </summary>
    /// <returns>Result indicating success or failure.</returns>
    Task<Result> RequestElevationAsync();

    /// <summary>
    /// Encrypts a string using DPAPI.
    /// </summary>
    /// <param name="plainText">The text to encrypt.</param>
    /// <returns>The encrypted text in Base64 format.</returns>
    string EncryptString(string plainText);

    /// <summary>
    /// Decrypts a string using DPAPI.
    /// </summary>
    /// <param name="cipherText">The encrypted text in Base64 format.</param>
    /// <returns>The decrypted plain text.</returns>
    string DecryptString(string cipherText);

    /// <summary>
    /// Validates the integrity of a file using SHA256 hash.
    /// </summary>
    /// <param name="filePath">The path to the file.</param>
    /// <param name="expectedHash">The expected SHA256 hash.</param>
    /// <returns>Result indicating if the file is valid.</returns>
    Task<Result<bool>> ValidateFileIntegrityAsync(string filePath, string expectedHash);

    /// <summary>
    /// Computes the SHA256 hash of a file.
    /// </summary>
    /// <param name="filePath">The path to the file.</param>
    /// <returns>Result containing the hash in hexadecimal format.</returns>
    Task<Result<string>> ComputeFileHashAsync(string filePath);
}
