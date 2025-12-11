using System;

namespace Better11.Core.Models
{
    /// <summary>
    /// Represents a Windows power plan.
    /// </summary>
    public class PowerPlan
    {
        public string Guid { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public PowerPlanType Type { get; set; }
        public bool IsActive { get; set; }
    }

    /// <summary>
    /// Type of power plan.
    /// </summary>
    public enum PowerPlanType
    {
        Balanced,
        HighPerformance,
        PowerSaver,
        UltimatePerformance,
        Custom
    }
}
