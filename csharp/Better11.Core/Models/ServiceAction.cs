namespace Better11.Core.Models
{
    /// <summary>
    /// Represents a Windows service management action.
    /// </summary>
    public class ServiceAction
    {
        public string ServiceName { get; set; } = string.Empty;
        public ServiceActionType ActionType { get; set; }
        public ServiceStartMode? StartMode { get; set; }
    }

    public enum ServiceActionType
    {
        Start,
        Stop,
        Restart,
        Enable,
        Disable,
        SetStartupType
    }

    public enum ServiceStartMode
    {
        Automatic,
        Manual,
        Disabled
    }

    /// <summary>
    /// Result of a service operation.
    /// </summary>
    public class ServiceResult
    {
        public bool Success { get; set; }
        public string ServiceName { get; set; } = string.Empty;
        public string? ErrorMessage { get; set; }
    }
}
