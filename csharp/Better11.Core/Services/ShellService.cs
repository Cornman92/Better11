using System;
using System.Threading.Tasks;
using Better11.Core.Interfaces;
using Better11.Core.Models;
using Better11.Core.PowerShell;
using Microsoft.Extensions.Logging;

namespace Better11.Core.Services
{
    /// <summary>
    /// Service for Windows shell and taskbar customization.
    /// </summary>
    public class ShellService : IShellService
    {
        private readonly PowerShellExecutor _psExecutor;
        private readonly ILogger<ShellService> _logger;

        public ShellService(PowerShellExecutor psExecutor, ILogger<ShellService> logger)
        {
            _psExecutor = psExecutor;
            _logger = logger;
        }

        /// <inheritdoc/>
        public async Task<ShellSettings> GetShellSettingsAsync()
        {
            try
            {
                _logger.LogInformation("Getting shell settings");

                var result = await _psExecutor.ExecuteCommandAsync("Get-Better11TaskbarSettings");

                if (result.Success && result.Output.Count > 0)
                {
                    dynamic settings = result.Output[0];
                    return new ShellSettings
                    {
                        TaskbarAlignment = (TaskbarAlignment)(settings.TaskbarAlignment ?? 1),
                        SearchMode = (SearchMode)(settings.SearchMode ?? 1),
                        TaskViewVisible = settings.TaskViewVisible ?? true,
                        WidgetsVisible = settings.WidgetsVisible ?? true,
                        CopilotVisible = settings.CopilotVisible ?? true,
                        ClassicContextMenu = settings.ClassicContextMenu ?? false
                    };
                }

                return new ShellSettings();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to get shell settings");
                throw;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> SetTaskbarAlignmentAsync(TaskbarAlignment alignment)
        {
            try
            {
                _logger.LogInformation("Setting taskbar alignment to {Alignment}", alignment);

                var result = await _psExecutor.ExecuteCommandAsync(
                    "Set-Better11TaskbarAlignment",
                    new() { { "Alignment", alignment.ToString() } });

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to set taskbar alignment");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> SetSearchModeAsync(SearchMode mode)
        {
            try
            {
                _logger.LogInformation("Setting search mode to {Mode}", mode);

                var result = await _psExecutor.ExecuteCommandAsync(
                    "Set-Better11SearchMode",
                    new() { { "Mode", mode.ToString() } });

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to set search mode");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> SetTaskViewVisibleAsync(bool visible)
        {
            try
            {
                _logger.LogInformation("{Action} Task View button", visible ? "Showing" : "Hiding");

                var result = await _psExecutor.ExecuteCommandAsync(
                    "Set-Better11TaskViewVisible",
                    new() { { "Visible", visible } });

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to set Task View visibility");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> SetWidgetsVisibleAsync(bool visible)
        {
            try
            {
                _logger.LogInformation("{Action} Widgets button", visible ? "Showing" : "Hiding");

                var result = await _psExecutor.ExecuteCommandAsync(
                    "Set-Better11WidgetsVisible",
                    new() { { "Visible", visible } });

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to set Widgets visibility");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> SetCopilotVisibleAsync(bool visible)
        {
            try
            {
                _logger.LogInformation("{Action} Copilot button", visible ? "Showing" : "Hiding");

                var result = await _psExecutor.ExecuteCommandAsync(
                    "Set-Better11CopilotVisible",
                    new() { { "Visible", visible } });

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to set Copilot visibility");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> SetClassicContextMenuAsync(bool enabled)
        {
            try
            {
                _logger.LogInformation("{Action} classic context menu", enabled ? "Enabling" : "Disabling");

                var command = enabled ? "Enable-Better11ClassicContextMenu" : "Disable-Better11ClassicContextMenu";
                var result = await _psExecutor.ExecuteCommandAsync(command);

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to set classic context menu");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> ApplyShellPresetAsync(ShellPreset preset)
        {
            try
            {
                _logger.LogInformation("Applying shell preset: {Preset}", preset);

                var result = await _psExecutor.ExecuteCommandAsync(
                    "Set-Better11ShellPreset",
                    new() { { "Preset", preset.ToString() } });

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to apply shell preset");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> RestartExplorerAsync()
        {
            try
            {
                _logger.LogInformation("Restarting Windows Explorer");

                var result = await _psExecutor.ExecuteCommandAsync("Restart-Better11Explorer");

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to restart Explorer");
                return false;
            }
        }
    }
}
