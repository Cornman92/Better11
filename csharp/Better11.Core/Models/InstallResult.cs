namespace Better11.Core.Models
{
    /// <summary>
    /// Result of an application installation operation.
    /// </summary>
    public class InstallResult
    {
        public bool Success { get; set; }
        public string AppId { get; set; } = string.Empty;
        public string Version { get; set; } = string.Empty;
        public string Status { get; set; } = string.Empty;
        public string? ErrorMessage { get; set; }
        public int? ExitCode { get; set; }
    }

    /// <summary>
    /// Result of an application uninstallation operation.
    /// </summary>
    public class UninstallResult
    {
        public bool Success { get; set; }
        public string AppId { get; set; } = string.Empty;
        public string? ErrorMessage { get; set; }
    }

    /// <summary>
    /// Result of an application download operation.
    /// </summary>
    public class DownloadResult
    {
        public bool Success { get; set; }
        public string AppId { get; set; } = string.Empty;
        public string? FilePath { get; set; }
        public string? ErrorMessage { get; set; }
    }
}
