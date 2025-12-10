using System;

namespace Better11.Core.Models
{
    /// <summary>
    /// Represents disk/volume information.
    /// </summary>
    public class DiskInfo
    {
        public string DriveLetter { get; set; } = string.Empty;
        public string Label { get; set; } = string.Empty;
        public string FileSystem { get; set; } = string.Empty;
        public DriveType DriveType { get; set; }
        public long TotalBytes { get; set; }
        public long UsedBytes { get; set; }
        public long FreeBytes { get; set; }

        /// <summary>
        /// Total space in GB.
        /// </summary>
        public double TotalGB => TotalBytes / (1024.0 * 1024.0 * 1024.0);

        /// <summary>
        /// Used space in GB.
        /// </summary>
        public double UsedGB => UsedBytes / (1024.0 * 1024.0 * 1024.0);

        /// <summary>
        /// Free space in GB.
        /// </summary>
        public double FreeGB => FreeBytes / (1024.0 * 1024.0 * 1024.0);

        /// <summary>
        /// Usage percentage.
        /// </summary>
        public double UsagePercent => TotalBytes > 0 ? (UsedBytes / (double)TotalBytes) * 100.0 : 0.0;
    }

    /// <summary>
    /// Type of disk drive.
    /// </summary>
    public enum DriveType
    {
        HDD,
        SSD,
        Removable,
        Network,
        Unknown
    }
}
