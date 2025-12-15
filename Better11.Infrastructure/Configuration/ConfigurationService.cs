using Better11.Core.Interfaces;
using Microsoft.Extensions.Logging;
using System.Text.Json;

namespace Better11.Infrastructure.Configuration;

/// <summary>
/// Implementation of configuration service using JSON file storage.
/// </summary>
public class ConfigurationService : IConfigurationService
{
    private readonly ILogger<ConfigurationService> _logger;
    private readonly string _configFilePath;
    private Dictionary<string, object> _configuration;
    private readonly SemaphoreSlim _semaphore = new(1, 1);

    /// <summary>
    /// Initializes a new instance of the <see cref="ConfigurationService"/> class.
    /// </summary>
    /// <param name="logger">The logger instance.</param>
    /// <param name="configFilePath">Optional custom configuration file path.</param>
    public ConfigurationService(ILogger<ConfigurationService> logger, string? configFilePath = null)
    {
        _logger = logger;
        _configFilePath = configFilePath ?? Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
            "Better11",
            "Settings",
            "user-settings.json");

        _configuration = new Dictionary<string, object>();

        // Ensure directory exists
        var directory = Path.GetDirectoryName(_configFilePath);
        if (!string.IsNullOrEmpty(directory))
        {
            Directory.CreateDirectory(directory);
        }

        // Load configuration
        Task.Run(async () => await ReloadAsync()).Wait();
    }

    /// <inheritdoc/>
    public T GetValue<T>(string key, T defaultValue = default!)
    {
        _semaphore.Wait();
        try
        {
            if (!_configuration.TryGetValue(key, out var value))
            {
                _logger.LogDebug("Configuration key not found: {Key}, using default value", key);
                return defaultValue;
            }

            if (value is JsonElement jsonElement)
            {
                try
                {
                    return jsonElement.Deserialize<T>() ?? defaultValue;
                }
                catch (JsonException ex)
                {
                    _logger.LogWarning(ex, "Failed to deserialize configuration value for key: {Key}", key);
                    return defaultValue;
                }
            }

            if (value is T typedValue)
            {
                return typedValue;
            }

            try
            {
                return (T)Convert.ChangeType(value, typeof(T));
            }
            catch (Exception ex)
            {
                _logger.LogWarning(ex, "Failed to convert configuration value for key: {Key}", key);
                return defaultValue;
            }
        }
        finally
        {
            _semaphore.Release();
        }
    }

    /// <inheritdoc/>
    public void SetValue<T>(string key, T value)
    {
        _semaphore.Wait();
        try
        {
            _logger.LogDebug("Setting configuration value: {Key}", key);
            _configuration[key] = value!;
        }
        finally
        {
            _semaphore.Release();
        }
    }

    /// <inheritdoc/>
    public bool HasKey(string key)
    {
        _semaphore.Wait();
        try
        {
            return _configuration.ContainsKey(key);
        }
        finally
        {
            _semaphore.Release();
        }
    }

    /// <inheritdoc/>
    public async Task SaveAsync()
    {
        await _semaphore.WaitAsync();
        try
        {
            _logger.LogInformation("Saving configuration to {FilePath}", _configFilePath);

            var json = JsonSerializer.Serialize(_configuration, new JsonSerializerOptions
            {
                WriteIndented = true
            });

            await File.WriteAllTextAsync(_configFilePath, json);

            _logger.LogInformation("Configuration saved successfully");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error saving configuration");
            throw;
        }
        finally
        {
            _semaphore.Release();
        }
    }

    /// <inheritdoc/>
    public async Task ReloadAsync()
    {
        await _semaphore.WaitAsync();
        try
        {
            _logger.LogDebug("Reloading configuration from {FilePath}", _configFilePath);

            if (!File.Exists(_configFilePath))
            {
                _logger.LogInformation("Configuration file not found, creating new");
                _configuration = new Dictionary<string, object>();
                return;
            }

            var json = await File.ReadAllTextAsync(_configFilePath);
            _configuration = JsonSerializer.Deserialize<Dictionary<string, object>>(json)
                ?? new Dictionary<string, object>();

            _logger.LogInformation("Configuration reloaded successfully, {Count} keys", _configuration.Count);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error reloading configuration");
            _configuration = new Dictionary<string, object>();
        }
        finally
        {
            _semaphore.Release();
        }
    }
}
