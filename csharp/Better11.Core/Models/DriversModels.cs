using System;

namespace Better11.Core.Models
{
    /// <summary>
    /// Driver information.
    /// </summary>
    public class DriverInfo
    {
        public string DeviceName { get; set; } = string.Empty;
        public string DriverVersion { get; set; } = string.Empty;
        public DateTime? DriverDate { get; set; }
        public string Manufacturer { get; set; } = string.Empty;
        public string DeviceClass { get; set; } = string.Empty;
        public string DeviceID { get; set; } = string.Empty;
        public bool IsSigned { get; set; }
        public string? InfName { get; set; }
    }

    /// <summary>
    /// Driver issue information.
    /// </summary>
    public class DriverIssue
    {
        public string DeviceName { get; set; } = string.Empty;
        public string Status { get; set; } = string.Empty;
        public int ErrorCode { get; set; }
        public string? ErrorDescription { get; set; }
        public string DeviceID { get; set; } = string.Empty;
        public string? DeviceClass { get; set; }
    }

    /// <summary>
    /// Driver backup result.
    /// </summary>
    public class DriverBackupResult
    {
        public bool Success { get; set; }
        public string Path { get; set; } = string.Empty;
        public int DriversBackedUp { get; set; }
        public DateTime Timestamp { get; set; }
        public string? Error { get; set; }
    }
}
