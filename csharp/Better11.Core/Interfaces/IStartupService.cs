using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Better11.Core.Models;

namespace Better11.Core.Interfaces
{
    /// <summary>
    /// Interface for startup program management.
    /// </summary>
    public interface IStartupService
    {
        /// <summary>
        /// Lists all startup items.
        /// </summary>
        /// <returns>List of startup items.</returns>
        Task<List<StartupItem>> ListStartupItemsAsync();

        /// <summary>
        /// Enables a startup item.
        /// </summary>
        /// <param name="name">Name of the startup item.</param>
        /// <returns>True if successful.</returns>
        Task<bool> EnableStartupItemAsync(string name);

        /// <summary>
        /// Disables a startup item.
        /// </summary>
        /// <param name="name">Name of the startup item.</param>
        /// <returns>True if successful.</returns>
        Task<bool> DisableStartupItemAsync(string name);

        /// <summary>
        /// Adds a new startup item.
        /// </summary>
        /// <param name="item">Startup item to add.</param>
        /// <returns>True if successful.</returns>
        Task<bool> AddStartupItemAsync(StartupItem item);

        /// <summary>
        /// Removes a startup item.
        /// </summary>
        /// <param name="name">Name of the startup item.</param>
        /// <returns>True if successful.</returns>
        Task<bool> RemoveStartupItemAsync(string name);
    }
}
