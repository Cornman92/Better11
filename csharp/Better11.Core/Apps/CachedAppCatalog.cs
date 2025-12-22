using System;
using System.Collections.Generic;
using Better11.Core.Apps.Models;

namespace Better11.Core.Apps
{
    /// <summary>
    /// Cached wrapper around AppCatalog for improved performance.
    /// Caches catalog data in memory and tracks file modification time.
    /// </summary>
    public class CachedAppCatalog
    {
        private readonly string _catalogPath;
        private AppCatalog? _cachedCatalog;
        private DateTime _lastModified;
        private readonly object _lock = new object();
        private readonly TimeSpan _cacheExpiration;

        /// <summary>
        /// Creates a new cached catalog instance.
        /// </summary>
        /// <param name="catalogPath">Path to the catalog JSON file.</param>
        /// <param name="cacheExpiration">Optional cache expiration time. Default is 5 minutes.</param>
        public CachedAppCatalog(string catalogPath, TimeSpan? cacheExpiration = null)
        {
            _catalogPath = catalogPath ?? throw new ArgumentNullException(nameof(catalogPath));
            _cacheExpiration = cacheExpiration ?? TimeSpan.FromMinutes(5);
            _lastModified = DateTime.MinValue;
        }

        /// <summary>
        /// Gets the catalog, using cache if valid or reloading if necessary.
        /// </summary>
        /// <returns>The app catalog.</returns>
        public AppCatalog GetCatalog()
        {
            lock (_lock)
            {
                if (ShouldReload())
                {
                    ReloadCatalog();
                }

                return _cachedCatalog!;
            }
        }

        /// <summary>
        /// Forces a reload of the catalog from disk.
        /// </summary>
        public void Invalidate()
        {
            lock (_lock)
            {
                _cachedCatalog = null;
                _lastModified = DateTime.MinValue;
            }
        }

        /// <summary>
        /// Gets an application from the catalog.
        /// </summary>
        /// <param name="appId">Application ID.</param>
        /// <returns>Application metadata.</returns>
        public AppMetadata Get(string appId)
        {
            return GetCatalog().Get(appId);
        }

        /// <summary>
        /// Lists all applications in the catalog.
        /// </summary>
        /// <returns>List of all applications.</returns>
        public List<AppMetadata> ListAll()
        {
            return GetCatalog().ListAll();
        }

        /// <summary>
        /// Checks if the catalog should be reloaded.
        /// </summary>
        private bool ShouldReload()
        {
            // No cache exists
            if (_cachedCatalog == null)
            {
                return true;
            }

            // Cache has expired
            if (DateTime.Now - _lastModified > _cacheExpiration)
            {
                return true;
            }

            // File has been modified
            if (File.Exists(_catalogPath))
            {
                var fileModified = File.GetLastWriteTimeUtc(_catalogPath);
                if (fileModified > _lastModified)
                {
                    return true;
                }
            }

            return false;
        }

        /// <summary>
        /// Reloads the catalog from disk.
        /// </summary>
        private void ReloadCatalog()
        {
            _cachedCatalog = AppCatalog.FromFile(_catalogPath);
            _lastModified = File.Exists(_catalogPath)
                ? File.GetLastWriteTimeUtc(_catalogPath)
                : DateTime.UtcNow;
        }

        /// <summary>
        /// Gets cache statistics for monitoring.
        /// </summary>
        public CacheStatistics GetStatistics()
        {
            lock (_lock)
            {
                return new CacheStatistics
                {
                    IsCached = _cachedCatalog != null,
                    LastReload = _lastModified,
                    ItemCount = _cachedCatalog?.ListAll().Count ?? 0,
                    CacheAge = DateTime.Now - _lastModified
                };
            }
        }
    }

    /// <summary>
    /// Statistics about the catalog cache.
    /// </summary>
    public class CacheStatistics
    {
        /// <summary>
        /// Whether the catalog is currently cached.
        /// </summary>
        public bool IsCached { get; init; }

        /// <summary>
        /// When the catalog was last reloaded.
        /// </summary>
        public DateTime LastReload { get; init; }

        /// <summary>
        /// Number of items in the cached catalog.
        /// </summary>
        public int ItemCount { get; init; }

        /// <summary>
        /// Age of the current cache.
        /// </summary>
        public TimeSpan CacheAge { get; init; }
    }
}
