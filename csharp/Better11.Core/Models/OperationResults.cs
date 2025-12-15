namespace Better11.Core.Models
{
    public class InstallResult
    {
        public bool Success { get; set; }
        public string AppId { get; set; } = string.Empty;
        public string Version { get; set; } = string.Empty;
        public string Status { get; set; } = string.Empty;
        public string? ErrorMessage { get; set; }
    }
    
    public class UninstallResult
    {
        public bool Success { get; set; }
        public string AppId { get; set; } = string.Empty;
        public string? ErrorMessage { get; set; }
    }
}
