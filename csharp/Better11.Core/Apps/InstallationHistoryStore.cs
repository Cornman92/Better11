using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Text.Json.Serialization;
using Better11.Core.Models;

namespace Better11.Core.Apps
{
    /// <summary>
    /// Persists and retrieves installation history events.
    /// </summary>
    public class InstallationHistoryStore
    {
        private readonly string _historyFile;
        private readonly object _lock = new object();
        private readonly JsonSerializerOptions _jsonOptions;

        public InstallationHistoryStore(string historyFile)
        {
            _historyFile = historyFile;
            _jsonOptions = new JsonSerializerOptions
            {
                WriteIndented = true,
                Converters = { new JsonStringEnumConverter() }
            };

            var directory = Path.GetDirectoryName(_historyFile);
            if (!string.IsNullOrEmpty(directory))
            {
                Directory.CreateDirectory(directory);
            }
        }

        /// <summary>
        /// Records a new installation history entry.
        /// </summary>
        public void RecordEvent(InstallationHistoryEntry entry)
        {
            lock (_lock)
            {
                var history = LoadHistory();
                history.Add(entry);

                // Keep only last 1000 entries to prevent unbounded growth
                if (history.Count > 1000)
                {
                    history = history
                        .OrderByDescending(e => e.Timestamp)
                        .Take(1000)
                        .ToList();
                }

                SaveHistory(history);
            }
        }

        /// <summary>
        /// Queries installation history with optional filters.
        /// </summary>
        public List<InstallationHistoryEntry> Query(InstallationHistoryFilter? filter = null)
        {
            lock (_lock)
            {
                var history = LoadHistory();
                var query = history.AsEnumerable();

                if (filter != null)
                {
                    if (!string.IsNullOrEmpty(filter.AppId))
                    {
                        query = query.Where(e => e.AppId.Equals(filter.AppId, StringComparison.OrdinalIgnoreCase));
                    }

                    if (filter.EventType.HasValue)
                    {
                        query = query.Where(e => e.EventType == filter.EventType.Value);
                    }

                    if (filter.StartDate.HasValue)
                    {
                        query = query.Where(e => e.Timestamp >= filter.StartDate.Value);
                    }

                    if (filter.EndDate.HasValue)
                    {
                        query = query.Where(e => e.Timestamp <= filter.EndDate.Value);
                    }

                    if (filter.SuccessOnly.HasValue)
                    {
                        query = query.Where(e => e.Success == filter.SuccessOnly.Value);
                    }
                }

                var results = query.OrderByDescending(e => e.Timestamp).ToList();

                if (filter?.Limit.HasValue == true && filter.Limit.Value > 0)
                {
                    results = results.Take(filter.Limit.Value).ToList();
                }

                return results;
            }
        }

        /// <summary>
        /// Gets a summary of installation history for a specific app.
        /// </summary>
        public InstallationHistorySummary? GetSummary(string appId)
        {
            lock (_lock)
            {
                var history = LoadHistory()
                    .Where(e => e.AppId.Equals(appId, StringComparison.OrdinalIgnoreCase))
                    .OrderByDescending(e => e.Timestamp)
                    .ToList();

                if (!history.Any())
                {
                    return null;
                }

                var installs = history.Where(e => e.EventType == InstallationEventType.Install);
                var uninstalls = history.Where(e => e.EventType == InstallationEventType.Uninstall);
                var updates = history.Where(e => e.EventType == InstallationEventType.Update);

                return new InstallationHistorySummary
                {
                    AppId = appId,
                    FirstInstalled = installs.Any() ? installs.OrderBy(e => e.Timestamp).First().Timestamp : null,
                    LastInstalled = installs.Any() ? installs.First().Timestamp : null,
                    LastUninstalled = uninstalls.Any() ? uninstalls.First().Timestamp : null,
                    LastUpdated = updates.Any() ? updates.First().Timestamp : null,
                    TotalInstallations = installs.Count(),
                    TotalUninstallations = uninstalls.Count(),
                    FailedOperations = history.Count(e => !e.Success),
                    RecentEvents = history.Take(10).ToList()
                };
            }
        }

        /// <summary>
        /// Gets all apps that have history entries.
        /// </summary>
        public List<string> GetTrackedApps()
        {
            lock (_lock)
            {
                var history = LoadHistory();
                return history
                    .Select(e => e.AppId)
                    .Distinct(StringComparer.OrdinalIgnoreCase)
                    .OrderBy(id => id)
                    .ToList();
            }
        }

        /// <summary>
        /// Clears history older than the specified date.
        /// </summary>
        public int ClearOldHistory(DateTime olderThan)
        {
            lock (_lock)
            {
                var history = LoadHistory();
                var initialCount = history.Count;

                history = history
                    .Where(e => e.Timestamp >= olderThan)
                    .ToList();

                SaveHistory(history);
                return initialCount - history.Count;
            }
        }

        /// <summary>
        /// Clears all history for a specific app.
        /// </summary>
        public int ClearAppHistory(string appId)
        {
            lock (_lock)
            {
                var history = LoadHistory();
                var initialCount = history.Count;

                history = history
                    .Where(e => !e.AppId.Equals(appId, StringComparison.OrdinalIgnoreCase))
                    .ToList();

                SaveHistory(history);
                return initialCount - history.Count;
            }
        }

        private List<InstallationHistoryEntry> LoadHistory()
        {
            if (!File.Exists(_historyFile))
            {
                return new List<InstallationHistoryEntry>();
            }

            try
            {
                var json = File.ReadAllText(_historyFile);
                return JsonSerializer.Deserialize<List<InstallationHistoryEntry>>(json, _jsonOptions)
                    ?? new List<InstallationHistoryEntry>();
            }
            catch (JsonException)
            {
                // If history file is corrupted, start fresh
                return new List<InstallationHistoryEntry>();
            }
        }

        private void SaveHistory(List<InstallationHistoryEntry> history)
        {
            var json = JsonSerializer.Serialize(history, _jsonOptions);
            File.WriteAllText(_historyFile, json);
        }
    }
}
