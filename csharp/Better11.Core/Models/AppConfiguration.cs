using System;
using System.Collections.Generic;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace Better11.Core.Models
{
    /// <summary>
    /// Represents an exportable/importable app configuration.
    /// Can be used to backup installed apps or share configurations.
    /// </summary>
    public class AppConfiguration
    {
        /// <summary>
        /// Configuration format version for compatibility.
        /// </summary>
        [JsonPropertyName("version")]
        public string Version { get; set; } = "1.0";

        /// <summary>
        /// Display name for this configuration.
        /// </summary>
        [JsonPropertyName("name")]
        public string Name { get; set; } = string.Empty;

        /// <summary>
        /// Optional description of this configuration.
        /// </summary>
        [JsonPropertyName("description")]
        public string? Description { get; set; }

        /// <summary>
        /// When this configuration was created.
        /// </summary>
        [JsonPropertyName("createdAt")]
        public DateTime CreatedAt { get; set; } = DateTime.Now;

        /// <summary>
        /// Machine name where this was exported from.
        /// </summary>
        [JsonPropertyName("exportedFrom")]
        public string? ExportedFrom { get; set; }

        /// <summary>
        /// List of application IDs to install.
        /// </summary>
        [JsonPropertyName("applications")]
        public List<string> Applications { get; set; } = new();

        /// <summary>
        /// Optional metadata for custom properties.
        /// </summary>
        [JsonPropertyName("metadata")]
        public Dictionary<string, string> Metadata { get; set; } = new();

        /// <summary>
        /// Serializes the configuration to JSON.
        /// </summary>
        public string ToJson()
        {
            var options = new JsonSerializerOptions
            {
                WriteIndented = true,
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase
            };
            return JsonSerializer.Serialize(this, options);
        }

        /// <summary>
        /// Deserializes configuration from JSON.
        /// </summary>
        public static AppConfiguration FromJson(string json)
        {
            var options = new JsonSerializerOptions
            {
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
                PropertyNameCaseInsensitive = true
            };

            var config = JsonSerializer.Deserialize<AppConfiguration>(json, options);
            if (config == null)
            {
                throw new InvalidOperationException("Failed to deserialize app configuration");
            }

            return config;
        }

        /// <summary>
        /// Saves configuration to a file.
        /// </summary>
        public void SaveToFile(string path)
        {
            var json = ToJson();
            File.WriteAllText(path, json);
        }

        /// <summary>
        /// Loads configuration from a file.
        /// </summary>
        public static AppConfiguration LoadFromFile(string path)
        {
            if (!File.Exists(path))
            {
                throw new FileNotFoundException($"Configuration file not found: {path}");
            }

            var json = File.ReadAllText(path);
            return FromJson(json);
        }

        /// <summary>
        /// Validates the configuration.
        /// </summary>
        public List<string> Validate()
        {
            var errors = new List<string>();

            if (string.IsNullOrWhiteSpace(Name))
            {
                errors.Add("Configuration name is required");
            }

            if (Applications == null || Applications.Count == 0)
            {
                errors.Add("Configuration must contain at least one application");
            }

            if (Applications != null)
            {
                var duplicates = Applications
                    .GroupBy(a => a)
                    .Where(g => g.Count() > 1)
                    .Select(g => g.Key)
                    .ToList();

                if (duplicates.Any())
                {
                    errors.Add($"Duplicate applications found: {string.Join(", ", duplicates)}");
                }

                var invalidIds = Applications.Where(string.IsNullOrWhiteSpace).ToList();
                if (invalidIds.Any())
                {
                    errors.Add("Configuration contains empty application IDs");
                }
            }

            return errors;
        }

        /// <summary>
        /// Creates a configuration from currently installed apps.
        /// </summary>
        public static AppConfiguration FromInstalledApps(
            List<AppStatus> installedApps,
            string name,
            string? description = null)
        {
            return new AppConfiguration
            {
                Name = name,
                Description = description,
                CreatedAt = DateTime.Now,
                ExportedFrom = Environment.MachineName,
                Applications = installedApps
                    .Where(a => a.Installed)
                    .Select(a => a.AppId)
                    .OrderBy(a => a)
                    .ToList()
            };
        }
    }
}
