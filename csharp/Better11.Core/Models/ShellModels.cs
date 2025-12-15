using System;

namespace Better11.Core.Models
{
    /// <summary>
    /// Shell and taskbar settings.
    /// </summary>
    public class ShellSettings
    {
        public TaskbarAlignment TaskbarAlignment { get; set; }
        public SearchMode SearchMode { get; set; }
        public bool TaskViewVisible { get; set; }
        public bool WidgetsVisible { get; set; }
        public bool CopilotVisible { get; set; }
        public bool ClassicContextMenu { get; set; }
    }

    /// <summary>
    /// Taskbar alignment options.
    /// </summary>
    public enum TaskbarAlignment
    {
        Left = 0,
        Center = 1
    }

    /// <summary>
    /// Taskbar search box display modes.
    /// </summary>
    public enum SearchMode
    {
        Hidden = 0,
        IconOnly = 1,
        SearchBox = 2,
        IconAndLabel = 3
    }

    /// <summary>
    /// Shell customization preset.
    /// </summary>
    public enum ShellPreset
    {
        Windows10Style,
        Minimal,
        Default
    }
}
