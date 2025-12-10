using System;
using System.Collections.Generic;

namespace Better11.Core.Models
{
    /// <summary>
    /// Result of a cleanup operation.
    /// </summary>
    public class CleanupResult
    {
        public List<string> LocationsCleaned { get; set; } = new();
        public int FilesRemoved { get; set; }
        public long SpaceFreedBytes { get; set; }

        /// <summary>
        /// Space freed in MB.
        /// </summary>
        public double SpaceFreedMB => SpaceFreedBytes / (1024.0 * 1024.0);

        /// <summary>
        /// Space freed in GB.
        /// </summary>
        public double SpaceFreedGB => SpaceFreedBytes / (1024.0 * 1024.0 * 1024.0);
    }
}
