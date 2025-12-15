namespace Better11.Core.Interfaces;

/// <summary>
/// Service for managing application configuration and settings.
/// </summary>
public interface IConfigurationService
{
    /// <summary>
    /// Gets a configuration value.
    /// </summary>
    /// <typeparam name="T">The type of the value.</typeparam>
    /// <param name="key">The configuration key.</param>
    /// <param name="defaultValue">The default value if key not found.</param>
    /// <returns>The configuration value.</returns>
    T GetValue<T>(string key, T defaultValue = default!);

    /// <summary>
    /// Sets a configuration value.
    /// </summary>
    /// <typeparam name="T">The type of the value.</typeparam>
    /// <param name="key">The configuration key.</param>
    /// <param name="value">The value to set.</param>
    void SetValue<T>(string key, T value);

    /// <summary>
    /// Checks if a configuration key exists.
    /// </summary>
    /// <param name="key">The configuration key.</param>
    /// <returns>True if the key exists; otherwise, false.</returns>
    bool HasKey(string key);

    /// <summary>
    /// Saves the configuration to persistent storage.
    /// </summary>
    Task SaveAsync();

    /// <summary>
    /// Reloads the configuration from persistent storage.
    /// </summary>
    Task ReloadAsync();
}
