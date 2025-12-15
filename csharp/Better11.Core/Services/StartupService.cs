using System;
using System.Collections.Generic;
using System.Linq;
using System.Management.Automation;
using System.Threading.Tasks;
using Better11.Core.Interfaces;
using Better11.Core.Models;
using Better11.Core.PowerShell;
using Microsoft.Extensions.Logging;

namespace Better11.Core.Services
{
    /// <summary>
    /// Service for managing startup programs.
    /// </summary>
    public class StartupService : IStartupService
    {
        private readonly PowerShellExecutor _psExecutor;
        private readonly ILogger<StartupService> _logger;

        public StartupService(PowerShellExecutor psExecutor, ILogger<StartupService> logger)
        {
            _psExecutor = psExecutor;
            _logger = logger;
        }

        /// <inheritdoc/>
        public async Task<List<StartupItem>> ListStartupItemsAsync()
        {
            try
            {
                _logger.LogInformation("Listing startup items");

                var items = new List<StartupItem>();

                // Get registry startup items from HKCU
                var hkcuResult = await _psExecutor.ExecuteCommandAsync(@"
                    Get-ItemProperty -Path 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run' -ErrorAction SilentlyContinue |
                    ForEach-Object {
                        $_.PSObject.Properties | Where-Object { $_.Name -notmatch '^PS' } | ForEach-Object {
                            [PSCustomObject]@{
                                Name = $_.Name
                                Command = $_.Value
                                Location = 'HKCU'
                            }
                        }
                    }
                ");

                if (hkcuResult.Success)
                {
                    items.AddRange(ParseStartupItems(hkcuResult.Output, StartupLocation.RegistryCurrentUser));
                }

                // Get registry startup items from HKLM
                var hklmResult = await _psExecutor.ExecuteCommandAsync(@"
                    Get-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run' -ErrorAction SilentlyContinue |
                    ForEach-Object {
                        $_.PSObject.Properties | Where-Object { $_.Name -notmatch '^PS' } | ForEach-Object {
                            [PSCustomObject]@{
                                Name = $_.Name
                                Command = $_.Value
                                Location = 'HKLM'
                            }
                        }
                    }
                ");

                if (hklmResult.Success)
                {
                    items.AddRange(ParseStartupItems(hklmResult.Output, StartupLocation.RegistryLocalMachine));
                }

                // Get startup folder items
                var startupFolderResult = await _psExecutor.ExecuteCommandAsync(@"
                    $startupPath = [Environment]::GetFolderPath('Startup')
                    Get-ChildItem -Path $startupPath -ErrorAction SilentlyContinue | ForEach-Object {
                        [PSCustomObject]@{
                            Name = $_.BaseName
                            Command = $_.FullName
                            Location = 'StartupFolder'
                        }
                    }
                ");

                if (startupFolderResult.Success)
                {
                    items.AddRange(ParseStartupItems(startupFolderResult.Output, StartupLocation.StartupFolder));
                }

                _logger.LogInformation("Found {Count} startup item(s)", items.Count);
                return items;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to list startup items");
                throw;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> EnableStartupItemAsync(string name)
        {
            try
            {
                _logger.LogInformation("Enabling startup item: {Name}", name);

                // This would require implementing a disable/enable mechanism
                // For now, we log a warning
                _logger.LogWarning("Enable startup item not fully implemented");
                return false;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to enable startup item");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> DisableStartupItemAsync(string name)
        {
            try
            {
                _logger.LogInformation("Disabling startup item: {Name}", name);

                // Remove from registry (HKCU first)
                var result = await _psExecutor.ExecuteCommandAsync($@"
                    $removed = $false
                    $hkcuPath = 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run'
                    if (Get-ItemProperty -Path $hkcuPath -Name '{name}' -ErrorAction SilentlyContinue) {{
                        Remove-ItemProperty -Path $hkcuPath -Name '{name}' -Force
                        $removed = $true
                    }}
                    $removed
                ");

                return result.Success && result.Output.Any(o => o?.ToString()?.ToLower() == "true");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to disable startup item");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> AddStartupItemAsync(StartupItem item)
        {
            try
            {
                _logger.LogInformation("Adding startup item: {Name}", item.Name);

                var registryPath = item.Location switch
                {
                    StartupLocation.RegistryCurrentUser => "HKCU:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run",
                    StartupLocation.RegistryLocalMachine => "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run",
                    _ => throw new NotSupportedException($"Location {item.Location} not supported for adding items")
                };

                var result = await _psExecutor.ExecuteCommandAsync($@"
                    Set-ItemProperty -Path '{registryPath}' -Name '{item.Name}' -Value '{item.Command}'
                ");

                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to add startup item");
                return false;
            }
        }

        /// <inheritdoc/>
        public async Task<bool> RemoveStartupItemAsync(string name)
        {
            try
            {
                _logger.LogInformation("Removing startup item: {Name}", name);

                var result = await _psExecutor.ExecuteCommandAsync($@"
                    $removed = $false
                    $paths = @(
                        'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run',
                        'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run'
                    )
                    foreach ($path in $paths) {{
                        if (Get-ItemProperty -Path $path -Name '{name}' -ErrorAction SilentlyContinue) {{
                            Remove-ItemProperty -Path $path -Name '{name}' -Force -ErrorAction SilentlyContinue
                            $removed = $true
                        }}
                    }}
                    $removed
                ");

                return result.Success && result.Output.Any(o => o?.ToString()?.ToLower() == "true");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to remove startup item");
                return false;
            }
        }

        private List<StartupItem> ParseStartupItems(List<object> output, StartupLocation location)
        {
            var items = new List<StartupItem>();

            foreach (var item in output)
            {
                if (item is PSObject psObj)
                {
                    items.Add(new StartupItem
                    {
                        Name = psObj.Properties["Name"]?.Value?.ToString() ?? string.Empty,
                        Command = psObj.Properties["Command"]?.Value?.ToString() ?? string.Empty,
                        Location = location,
                        Enabled = true
                    });
                }
            }

            return items;
        }
    }
}
