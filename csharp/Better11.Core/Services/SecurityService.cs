using System;
using System.Collections.Generic;
using System.Linq;
using System.Management.Automation;
using System.Threading.Tasks;
using Better11.Core.Interfaces;
using Better11.Core.Models;
using Better11.Core.PowerShell;
using Microsoft.Extensions.Logging;

namespace Better11.Core.Services
{
    /// <summary>
    /// Service for security and verification operations.
    /// Communicates with PowerShell backend to perform operations.
    /// </summary>
    public class SecurityService : ISecurityService
    {
        private readonly PowerShellExecutor _psExecutor;
        private readonly ILogger<SecurityService> _logger;

        public SecurityService(
            PowerShellExecutor psExecutor,
            ILogger<SecurityService> logger)
        {
            _psExecutor = psExecutor;
            _logger = logger;
        }

        /// <summary>
        /// Verifies the code signature of a file.
        /// </summary>
        public async Task<SignatureInfo> VerifyCodeSignatureAsync(string filePath, bool checkRevocation = false)
        {
            try
            {
                _logger.LogInformation("Verifying code signature for: {FilePath}", filePath);

                var parameters = new Dictionary<string, object>
                {
                    { "FilePath", filePath },
                    { "CheckRevocation", checkRevocation }
                };

                var result = await _psExecutor.ExecuteCommandAsync(
                    "Test-Better11CodeSignature",
                    parameters);

                if (!result.Success)
                {
                    throw new InvalidOperationException(
                        $"Signature verification failed: {string.Join(", ", result.Errors)}");
                }

                var output = result.Output.FirstOrDefault() as PSObject;

                var statusStr = GetPropertyValue<string>(output, "Status");
                var status = Enum.TryParse<SignatureStatus>(statusStr, out var parsedStatus)
                    ? parsedStatus
                    : SignatureStatus.Unknown;

                CertificateInfo? certInfo = null;
                var cert = output?.Properties["Certificate"]?.Value as PSObject;
                if (cert != null)
                {
                    certInfo = new CertificateInfo
                    {
                        Subject = GetPropertyValue<string>(cert, "Subject") ?? string.Empty,
                        Issuer = GetPropertyValue<string>(cert, "Issuer") ?? string.Empty,
                        SerialNumber = GetPropertyValue<string>(cert, "SerialNumber") ?? string.Empty,
                        Thumbprint = GetPropertyValue<string>(cert, "Thumbprint") ?? string.Empty,
                        ValidFrom = GetPropertyValue<DateTime>(cert, "ValidFrom"),
                        ValidTo = GetPropertyValue<DateTime>(cert, "ValidTo"),
                        FriendlyName = GetPropertyValue<string>(cert, "FriendlyName")
                    };
                }

                return new SignatureInfo
                {
                    Status = status,
                    Certificate = certInfo,
                    HashAlgorithm = GetPropertyValue<string>(output, "HashAlgorithm"),
                    StatusMessage = GetPropertyValue<string>(output, "StatusMessage")
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to verify code signature");
                throw;
            }
        }

        /// <summary>
        /// Verifies the hash of a file.
        /// </summary>
        public async Task<HashVerificationResult> VerifyFileHashAsync(
            string filePath,
            string expectedHash,
            string algorithm = "SHA256")
        {
            try
            {
                _logger.LogInformation("Verifying {Algorithm} hash for: {FilePath}", algorithm, filePath);

                var parameters = new Dictionary<string, object>
                {
                    { "FilePath", filePath },
                    { "ExpectedHash", expectedHash },
                    { "Algorithm", algorithm }
                };

                var result = await _psExecutor.ExecuteCommandAsync(
                    "Verify-Better11FileHash",
                    parameters);

                if (!result.Success)
                {
                    throw new InvalidOperationException(
                        $"Hash verification failed: {string.Join(", ", result.Errors)}");
                }

                var output = result.Output.FirstOrDefault() as PSObject;

                return new HashVerificationResult
                {
                    FilePath = GetPropertyValue<string>(output, "FilePath") ?? string.Empty,
                    Algorithm = GetPropertyValue<string>(output, "Algorithm") ?? algorithm,
                    ComputedHash = GetPropertyValue<string>(output, "ComputedHash") ?? string.Empty,
                    ExpectedHash = GetPropertyValue<string>(output, "ExpectedHash") ?? expectedHash,
                    IsMatch = GetPropertyValue<bool>(output, "IsMatch"),
                    FileSize = GetPropertyValue<long>(output, "FileSize")
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to verify file hash");
                throw;
            }
        }

        /// <summary>
        /// Creates a system restore point.
        /// </summary>
        public async Task<bool> CreateRestorePointAsync(string description)
        {
            try
            {
                _logger.LogInformation("Creating restore point: {Description}", description);

                var parameters = new Dictionary<string, object>
                {
                    { "Description", description }
                };

                var result = await _psExecutor.ExecuteCommandAsync(
                    "New-Better11RestorePoint",
                    parameters);

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to create restore point");
                throw;
            }
        }

        /// <summary>
        /// Backs up a registry key.
        /// </summary>
        public async Task<string> BackupRegistryKeyAsync(string keyPath, string? destination = null)
        {
            try
            {
                _logger.LogInformation("Backing up registry key: {KeyPath}", keyPath);

                var parameters = new Dictionary<string, object>
                {
                    { "KeyPath", keyPath }
                };

                if (!string.IsNullOrEmpty(destination))
                {
                    parameters["Destination"] = destination;
                }

                var result = await _psExecutor.ExecuteCommandAsync(
                    "Backup-Better11Registry",
                    parameters);

                if (!result.Success)
                {
                    throw new InvalidOperationException(
                        $"Registry backup failed: {string.Join(", ", result.Errors)}");
                }

                var output = result.Output.FirstOrDefault() as PSObject;
                return GetPropertyValue<string>(output, "FullName") ?? string.Empty;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to backup registry key");
                throw;
            }
        }

        private T? GetPropertyValue<T>(PSObject? psObject, string propertyName)
        {
            if (psObject == null) return default;

            var property = psObject.Properties[propertyName];
            if (property == null) return default;

            try
            {
                if (typeof(T) == typeof(DateTime))
                {
                    var value = property.Value;
                    if (value is DateTime dt) return (T)(object)dt;
                    if (value is string str && DateTime.TryParse(str, out var parsed))
                        return (T)(object)parsed;
                    return default;
                }
                return (T?)Convert.ChangeType(property.Value, typeof(T));
            }
            catch
            {
                return default;
            }
        }
    }
}
