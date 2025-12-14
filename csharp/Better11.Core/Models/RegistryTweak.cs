namespace Better11.Core.Models
{
    /// <summary>
    /// Represents a registry modification.
    /// </summary>
    public class RegistryTweak
    {
        public string Hive { get; set; } = string.Empty;
        public string Path { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public object Value { get; set; } = null!;
        public RegistryValueType ValueType { get; set; }

        public string FullPath => $"{Hive}\\{Path}";
    }

    public enum RegistryValueType
    {
        String = 1,
        ExpandString = 2,
        Binary = 3,
        DWord = 4,
        MultiString = 7,
        QWord = 11
    }

    /// <summary>
    /// Result of applying registry tweaks.
    /// </summary>
    public class TweakResult
    {
        public int TotalTweaks { get; set; }
        public int AppliedSuccessfully { get; set; }
        public int Failed { get; set; }
        public string? ErrorMessage { get; set; }
    }
}
