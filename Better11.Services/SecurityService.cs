using Better11.Core.Interfaces;
using Better11.Core.Models;
using Microsoft.Extensions.Logging;
using System.Security.Cryptography;
using System.Security.Principal;
using System.Text;

namespace Better11.Services;

/// <summary>
/// Implementation of security service.
/// </summary>
public class SecurityService : ISecurityService
{
    private readonly ILogger<SecurityService> _logger;

    /// <summary>
    /// Initializes a new instance of the <see cref="SecurityService"/> class.
    /// </summary>
    /// <param name="logger">The logger instance.</param>
    public SecurityService(ILogger<SecurityService> logger)
    {
        _logger = logger;
    }

    /// <inheritdoc/>
    public bool IsAdministrator()
    {
        try
        {
            using var identity = WindowsIdentity.GetCurrent();
            var principal = new WindowsPrincipal(identity);
            var isAdmin = principal.IsInRole(WindowsBuiltInRole.Administrator);

            _logger.LogDebug("Is administrator: {IsAdmin}", isAdmin);
            return isAdmin;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error checking administrator status");
            return false;
        }
    }

    /// <inheritdoc/>
    public async Task<Result> RequestElevationAsync()
    {
        try
        {
            _logger.LogInformation("Requesting elevation");

            if (IsAdministrator())
            {
                _logger.LogInformation("Already running as administrator");
                return Result.Success();
            }

            // Restart the application with elevation
            var processInfo = new System.Diagnostics.ProcessStartInfo
            {
                FileName = Environment.ProcessPath ?? System.Diagnostics.Process.GetCurrentProcess().MainModule?.FileName,
                UseShellExecute = true,
                Verb = "runas"
            };

            System.Diagnostics.Process.Start(processInfo);

            // Exit current non-elevated process
            await Task.Run(() => Environment.Exit(0));

            return Result.Success();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error requesting elevation");
            return Result.Failure($"Failed to request elevation: {ex.Message}");
        }
    }

    /// <inheritdoc/>
    public string EncryptString(string plainText)
    {
        try
        {
            _logger.LogDebug("Encrypting string");

            var plainBytes = Encoding.UTF8.GetBytes(plainText);
            var encryptedBytes = ProtectedData.Protect(
                plainBytes,
                null,
                DataProtectionScope.CurrentUser);

            var result = Convert.ToBase64String(encryptedBytes);
            _logger.LogDebug("String encrypted successfully");

            return result;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error encrypting string");
            throw;
        }
    }

    /// <inheritdoc/>
    public string DecryptString(string cipherText)
    {
        try
        {
            _logger.LogDebug("Decrypting string");

            var cipherBytes = Convert.FromBase64String(cipherText);
            var decryptedBytes = ProtectedData.Unprotect(
                cipherBytes,
                null,
                DataProtectionScope.CurrentUser);

            var result = Encoding.UTF8.GetString(decryptedBytes);
            _logger.LogDebug("String decrypted successfully");

            return result;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error decrypting string");
            throw;
        }
    }

    /// <inheritdoc/>
    public async Task<Result<bool>> ValidateFileIntegrityAsync(string filePath, string expectedHash)
    {
        try
        {
            _logger.LogInformation("Validating file integrity: {FilePath}", filePath);

            var computeResult = await ComputeFileHashAsync(filePath);

            if (!computeResult.IsSuccess)
            {
                return Result<bool>.Failure(computeResult.Error!);
            }

            var actualHash = computeResult.Value!;
            var isValid = string.Equals(actualHash, expectedHash, StringComparison.OrdinalIgnoreCase);

            _logger.LogInformation("File integrity validation result: {IsValid}", isValid);

            return Result<bool>.Success(isValid);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error validating file integrity: {FilePath}", filePath);
            return Result<bool>.Failure($"Failed to validate file integrity: {ex.Message}");
        }
    }

    /// <inheritdoc/>
    public async Task<Result<string>> ComputeFileHashAsync(string filePath)
    {
        try
        {
            _logger.LogDebug("Computing file hash: {FilePath}", filePath);

            if (!File.Exists(filePath))
            {
                return Result<string>.Failure($"File not found: {filePath}");
            }

            using var sha256 = SHA256.Create();
            using var stream = File.OpenRead(filePath);

            var hashBytes = await sha256.ComputeHashAsync(stream);
            var hash = BitConverter.ToString(hashBytes).Replace("-", "").ToLowerInvariant();

            _logger.LogDebug("File hash computed: {Hash}", hash);

            return Result<string>.Success(hash);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error computing file hash: {FilePath}", filePath);
            return Result<string>.Failure($"Failed to compute file hash: {ex.Message}");
        }
    }
}
