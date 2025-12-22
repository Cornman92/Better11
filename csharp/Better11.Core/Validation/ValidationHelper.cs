using System;
using System.Text.RegularExpressions;

namespace Better11.Core.Validation
{
    /// <summary>
    /// Provides validation helpers for user input and parameters.
    /// </summary>
    public static class ValidationHelper
    {
        private static readonly Regex AppIdRegex = new Regex(@"^[a-zA-Z0-9_-]+$", RegexOptions.Compiled);
        private static readonly int MaxAppIdLength = 100;
        private static readonly int MaxPathLength = 260; // Windows MAX_PATH

        /// <summary>
        /// Validates an application ID.
        /// </summary>
        /// <param name="appId">The application ID to validate.</param>
        /// <param name="paramName">The parameter name for error messages.</param>
        /// <exception cref="ArgumentNullException">Thrown when appId is null or empty.</exception>
        /// <exception cref="ArgumentException">Thrown when appId is invalid.</exception>
        public static void ValidateAppId(string? appId, string paramName = "appId")
        {
            if (string.IsNullOrWhiteSpace(appId))
            {
                throw new ArgumentNullException(paramName, "Application ID cannot be null or empty");
            }

            if (appId.Length > MaxAppIdLength)
            {
                throw new ArgumentException(
                    $"Application ID cannot exceed {MaxAppIdLength} characters",
                    paramName);
            }

            if (!AppIdRegex.IsMatch(appId))
            {
                throw new ArgumentException(
                    "Application ID can only contain letters, numbers, hyphens, and underscores",
                    paramName);
            }
        }

        /// <summary>
        /// Validates a file path.
        /// </summary>
        /// <param name="path">The path to validate.</param>
        /// <param name="paramName">The parameter name for error messages.</param>
        /// <param name="mustExist">If true, validates that the path exists.</param>
        /// <exception cref="ArgumentNullException">Thrown when path is null or empty.</exception>
        /// <exception cref="ArgumentException">Thrown when path is invalid.</exception>
        public static void ValidatePath(string? path, string paramName = "path", bool mustExist = false)
        {
            if (string.IsNullOrWhiteSpace(path))
            {
                throw new ArgumentNullException(paramName, "Path cannot be null or empty");
            }

            if (path.Length > MaxPathLength)
            {
                throw new ArgumentException(
                    $"Path cannot exceed {MaxPathLength} characters",
                    paramName);
            }

            // Check for invalid path characters
            var invalidChars = Path.GetInvalidPathChars();
            if (path.IndexOfAny(invalidChars) >= 0)
            {
                throw new ArgumentException("Path contains invalid characters", paramName);
            }

            if (mustExist && !File.Exists(path) && !Directory.Exists(path))
            {
                throw new ArgumentException($"Path does not exist: {path}", paramName);
            }
        }

        /// <summary>
        /// Validates a URI string.
        /// </summary>
        /// <param name="uriString">The URI string to validate.</param>
        /// <param name="paramName">The parameter name for error messages.</param>
        /// <param name="allowedSchemes">Optional array of allowed URI schemes (e.g., "http", "https", "file").</param>
        /// <returns>The validated URI.</returns>
        /// <exception cref="ArgumentNullException">Thrown when uriString is null or empty.</exception>
        /// <exception cref="ArgumentException">Thrown when URI is invalid or uses disallowed scheme.</exception>
        public static Uri ValidateUri(string? uriString, string paramName = "uri", string[]? allowedSchemes = null)
        {
            if (string.IsNullOrWhiteSpace(uriString))
            {
                throw new ArgumentNullException(paramName, "URI cannot be null or empty");
            }

            if (!Uri.TryCreate(uriString, UriKind.RelativeOrAbsolute, out var uri))
            {
                throw new ArgumentException($"Invalid URI format: {uriString}", paramName);
            }

            if (allowedSchemes != null && allowedSchemes.Length > 0 && uri.IsAbsoluteUri)
            {
                var scheme = uri.Scheme.ToLowerInvariant();
                var isAllowed = false;
                foreach (var allowedScheme in allowedSchemes)
                {
                    if (scheme == allowedScheme.ToLowerInvariant())
                    {
                        isAllowed = true;
                        break;
                    }
                }

                if (!isAllowed)
                {
                    throw new ArgumentException(
                        $"URI scheme '{scheme}' is not allowed. Allowed schemes: {string.Join(", ", allowedSchemes)}",
                        paramName);
                }
            }

            return uri;
        }

        /// <summary>
        /// Validates a version string.
        /// </summary>
        /// <param name="versionString">The version string to validate.</param>
        /// <param name="paramName">The parameter name for error messages.</param>
        /// <returns>The validated Version object.</returns>
        /// <exception cref="ArgumentNullException">Thrown when versionString is null or empty.</exception>
        /// <exception cref="ArgumentException">Thrown when version format is invalid.</exception>
        public static Version ValidateVersion(string? versionString, string paramName = "version")
        {
            if (string.IsNullOrWhiteSpace(versionString))
            {
                throw new ArgumentNullException(paramName, "Version cannot be null or empty");
            }

            if (!Version.TryParse(versionString, out var version))
            {
                throw new ArgumentException($"Invalid version format: {versionString}", paramName);
            }

            return version;
        }

        /// <summary>
        /// Validates that a string does not contain potentially dangerous characters or patterns.
        /// </summary>
        /// <param name="input">The input string to validate.</param>
        /// <param name="paramName">The parameter name for error messages.</param>
        /// <exception cref="ArgumentException">Thrown when input contains dangerous characters.</exception>
        public static void ValidateNoCommandInjection(string? input, string paramName = "input")
        {
            if (string.IsNullOrEmpty(input))
            {
                return; // Null/empty is safe, handle with other validation if needed
            }

            // Check for command injection patterns
            var dangerousPatterns = new[] { "|", "&", ";", "$", "`", "\n", "\r", "<", ">" };
            foreach (var pattern in dangerousPatterns)
            {
                if (input.Contains(pattern))
                {
                    throw new ArgumentException(
                        $"Input contains potentially dangerous character or pattern: {pattern}",
                        paramName);
                }
            }
        }

        /// <summary>
        /// Validates that a number is within a specified range.
        /// </summary>
        /// <param name="value">The value to validate.</param>
        /// <param name="min">The minimum allowed value (inclusive).</param>
        /// <param name="max">The maximum allowed value (inclusive).</param>
        /// <param name="paramName">The parameter name for error messages.</param>
        /// <exception cref="ArgumentOutOfRangeException">Thrown when value is outside the allowed range.</exception>
        public static void ValidateRange(int value, int min, int max, string paramName = "value")
        {
            if (value < min || value > max)
            {
                throw new ArgumentOutOfRangeException(
                    paramName,
                    value,
                    $"Value must be between {min} and {max}");
            }
        }
    }
}
