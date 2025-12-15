using System.Threading.Tasks;
using Better11.Core.Models;

namespace Better11.Core.Interfaces
{
    /// <summary>
    /// Interface for Windows shell and taskbar customization.
    /// </summary>
    public interface IShellService
    {
        /// <summary>
        /// Gets current shell settings.
        /// </summary>
        Task<ShellSettings> GetShellSettingsAsync();

        /// <summary>
        /// Sets taskbar alignment.
        /// </summary>
        Task<bool> SetTaskbarAlignmentAsync(TaskbarAlignment alignment);

        /// <summary>
        /// Sets taskbar search mode.
        /// </summary>
        Task<bool> SetSearchModeAsync(SearchMode mode);

        /// <summary>
        /// Shows or hides the Task View button.
        /// </summary>
        Task<bool> SetTaskViewVisibleAsync(bool visible);

        /// <summary>
        /// Shows or hides the Widgets button.
        /// </summary>
        Task<bool> SetWidgetsVisibleAsync(bool visible);

        /// <summary>
        /// Shows or hides the Copilot button.
        /// </summary>
        Task<bool> SetCopilotVisibleAsync(bool visible);

        /// <summary>
        /// Enables or disables classic context menu.
        /// </summary>
        Task<bool> SetClassicContextMenuAsync(bool enabled);

        /// <summary>
        /// Applies a shell customization preset.
        /// </summary>
        Task<bool> ApplyShellPresetAsync(ShellPreset preset);

        /// <summary>
        /// Restarts Windows Explorer to apply changes.
        /// </summary>
        Task<bool> RestartExplorerAsync();
    }
}
