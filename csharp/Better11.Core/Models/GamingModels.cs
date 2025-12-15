using System;

namespace Better11.Core.Models
{
    /// <summary>
    /// Gaming optimization settings.
    /// </summary>
    public class GamingSettings
    {
        public bool GameModeEnabled { get; set; }
        public bool GameBarEnabled { get; set; }
        public bool GPUSchedulingEnabled { get; set; }
        public bool MouseAccelerationEnabled { get; set; }
        public bool NagleAlgorithmEnabled { get; set; }
        public string CurrentPowerPlan { get; set; } = string.Empty;
    }

    /// <summary>
    /// Gaming optimization preset levels.
    /// </summary>
    public enum GamingPreset
    {
        Maximum,
        Balanced,
        Default
    }
}
