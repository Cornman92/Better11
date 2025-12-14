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
    public class StartupService : IStartupService
    {
        private readonly PowerShellExecutor _psExecutor;
        private readonly ILogger<StartupService> _logger;

        public StartupService(PowerShellExecutor psExecutor, ILogger<StartupService> logger)
        {
            _psExecutor = psExecutor;
            _logger = logger;
        }

        public async Task<List<StartupItem>> ListStartupItemsAsync()
        {
            try
            {
                var result = await _psExecutor.ExecuteCommandAsync("Get-Better11StartupItems");

                var items = new List<StartupItem>();
                foreach (var item in result.Output)
                {
                    var psObj = item as PSObject;
                    if (psObj == null) continue;

                    items.Add(new StartupItem
                    {
                        Name = psObj.Properties["Name"]?.Value?.ToString() ?? string.Empty,
                        Command = psObj.Properties["Command"]?.Value?.ToString() ?? string.Empty,
                        Location = ParseLocation(psObj.Properties["Location"]?.Value?.ToString() ?? "Registry"),
                        Enabled = Convert.ToBoolean(psObj.Properties["Enabled"]?.Value ?? false)
                    });
                }

                return items;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to list startup items");
                throw;
            }
        }

        public async Task<bool> DisableStartupItemAsync(string itemName, StartupLocation location)
        {
            try
            {
                var parameters = new Dictionary<string, object>
                {
                    { "ItemName", itemName },
                    { "Location", location.ToString() }
                };

                var result = await _psExecutor.ExecuteCommandAsync("Disable-Better11StartupItem", parameters);
                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to disable startup item: {Item}", itemName);
                return false;
            }
        }

        public async Task<bool> EnableStartupItemAsync(string itemName, StartupLocation location)
        {
            try
            {
                var parameters = new Dictionary<string, object>
                {
                    { "ItemName", itemName },
                    { "Location", location.ToString() }
                };

                var result = await _psExecutor.ExecuteCommandAsync("Enable-Better11StartupItem", parameters);
                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to enable startup item: {Item}", itemName);
                return false;
            }
        }

        public async Task<bool> RemoveStartupItemAsync(string itemName, StartupLocation location)
        {
            try
            {
                var parameters = new Dictionary<string, object>
                {
                    { "ItemName", itemName },
                    { "Location", location.ToString() }
                };

                var result = await _psExecutor.ExecuteCommandAsync("Remove-Better11StartupItem", parameters);
                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to remove startup item: {Item}", itemName);
                return false;
            }
        }

        public async Task<bool> AddStartupItemAsync(StartupItem item)
        {
            try
            {
                var parameters = new Dictionary<string, object>
                {
                    { "Name", item.Name },
                    { "Command", item.Command },
                    { "Location", item.Location.ToString() }
                };

                var result = await _psExecutor.ExecuteCommandAsync("Add-Better11StartupItem", parameters);
                return result.Success;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to add startup item: {Item}", item.Name);
                return false;
            }
        }

        private StartupLocation ParseLocation(string location)
        {
            return location.ToLowerInvariant() switch
            {
                "registry" => StartupLocation.Registry,
                "startupfolder" => StartupLocation.StartupFolder,
                "taskscheduler" => StartupLocation.TaskScheduler,
                _ => StartupLocation.Registry
            };
        }
    }
}
