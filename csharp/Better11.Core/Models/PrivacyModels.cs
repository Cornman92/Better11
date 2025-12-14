using System;

namespace Better11.Core.Models
{
    /// <summary>
    /// Windows telemetry level settings.
    /// </summary>
    public enum TelemetryLevel
    {
        /// <summary>
        /// Security data only (Enterprise editions only).
        /// </summary>
        Security = 0,

        /// <summary>
        /// Basic diagnostic data.
        /// </summary>
        Basic = 1,

        /// <summary>
        /// Enhanced diagnostic data.
        /// </summary>
        Enhanced = 2,

        /// <summary>
        /// Full diagnostic data.
        /// </summary>
        Full = 3
    }

    /// <summary>
    /// Privacy settings status.
    /// </summary>
    public class PrivacyStatus
    {
        public TelemetryLevel TelemetryLevel { get; set; }
        public bool CortanaEnabled { get; set; }
        public bool LocationEnabled { get; set; }
        public bool AdvertisingIdEnabled { get; set; }
        public bool ActivityHistoryEnabled { get; set; }
        public bool DiagnosticDataViewerEnabled { get; set; }
    }
}
