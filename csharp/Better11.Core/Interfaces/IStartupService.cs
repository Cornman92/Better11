using System.Collections.Generic;
using System.Threading.Tasks;
using Better11.Core.Models;

namespace Better11.Core.Interfaces
{
    /// <summary>
    /// Service for managing startup programs.
    /// </summary>
    public interface IStartupService
    {
        /// <summary>
        /// Lists all startup items.
        /// </summary>
        Task<List<StartupItem>> ListStartupItemsAsync();

        /// <summary>
        /// Disables a startup item.
        /// </summary>
        Task<bool> DisableStartupItemAsync(string itemName, StartupLocation location);

        /// <summary>
        /// Enables a startup item.
        /// </summary>
        Task<bool> EnableStartupItemAsync(string itemName, StartupLocation location);

        /// <summary>
        /// Removes a startup item completely.
        /// </summary>
        Task<bool> RemoveStartupItemAsync(string itemName, StartupLocation location);

        /// <summary>
        /// Adds a new startup item.
        /// </summary>
        Task<bool> AddStartupItemAsync(StartupItem item);
    }
}
