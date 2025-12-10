using Better11.Core.Interfaces;
using Better11.Infrastructure.Configuration;
using Microsoft.Extensions.Logging;
using Moq;
using Xunit;

namespace Better11.UnitTests.Infrastructure;

/// <summary>
/// Unit tests for <see cref="ConfigurationService"/>.
/// </summary>
public class ConfigurationServiceTests : IDisposable
{
    private readonly Mock<ILogger<ConfigurationService>> _mockLogger;
    private readonly string _testConfigPath;
    private readonly IConfigurationService _service;

    public ConfigurationServiceTests()
    {
        _mockLogger = new Mock<ILogger<ConfigurationService>>();
        _testConfigPath = Path.Combine(Path.GetTempPath(), $"test_config_{Guid.NewGuid()}.json");
        _service = new ConfigurationService(_mockLogger.Object, _testConfigPath);
    }

    public void Dispose()
    {
        if (File.Exists(_testConfigPath))
        {
            File.Delete(_testConfigPath);
        }
    }

    [Fact]
    public void GetValue_NonExistingKey_ReturnsDefaultValue()
    {
        // Arrange
        var key = "nonexistent.key";
        var defaultValue = "default";

        // Act
        var result = _service.GetValue(key, defaultValue);

        // Assert
        Assert.Equal(defaultValue, result);
    }

    [Fact]
    public void SetValue_GetValue_RoundTrip_Success()
    {
        // Arrange
        var key = "test.string";
        var value = "test value";

        // Act
        _service.SetValue(key, value);
        var result = _service.GetValue<string>(key);

        // Assert
        Assert.Equal(value, result);
    }

    [Fact]
    public void SetValue_GetValue_IntegerType_Success()
    {
        // Arrange
        var key = "test.int";
        var value = 42;

        // Act
        _service.SetValue(key, value);
        var result = _service.GetValue<int>(key);

        // Assert
        Assert.Equal(value, result);
    }

    [Fact]
    public void SetValue_GetValue_BooleanType_Success()
    {
        // Arrange
        var key = "test.bool";
        var value = true;

        // Act
        _service.SetValue(key, value);
        var result = _service.GetValue<bool>(key);

        // Assert
        Assert.Equal(value, result);
    }

    [Fact]
    public void HasKey_ExistingKey_ReturnsTrue()
    {
        // Arrange
        var key = "existing.key";
        _service.SetValue(key, "value");

        // Act
        var result = _service.HasKey(key);

        // Assert
        Assert.True(result);
    }

    [Fact]
    public void HasKey_NonExistingKey_ReturnsFalse()
    {
        // Arrange
        var key = "nonexistent.key";

        // Act
        var result = _service.HasKey(key);

        // Assert
        Assert.False(result);
    }

    [Fact]
    public async Task SaveAsync_ReloadAsync_PersistsData()
    {
        // Arrange
        var key1 = "test.key1";
        var value1 = "value1";
        var key2 = "test.key2";
        var value2 = 123;

        _service.SetValue(key1, value1);
        _service.SetValue(key2, value2);

        // Act
        await _service.SaveAsync();

        // Create a new service instance to load the saved data
        var newService = new ConfigurationService(_mockLogger.Object, _testConfigPath);
        await newService.ReloadAsync();

        var result1 = newService.GetValue<string>(key1);
        var result2 = newService.GetValue<int>(key2);

        // Assert
        Assert.Equal(value1, result1);
        Assert.Equal(value2, result2);
    }

    [Fact]
    public async Task ReloadAsync_NonExistingFile_CreatesEmptyConfig()
    {
        // Arrange
        var newConfigPath = Path.Combine(Path.GetTempPath(), $"new_config_{Guid.NewGuid()}.json");
        var newService = new ConfigurationService(_mockLogger.Object, newConfigPath);

        try
        {
            // Act
            await newService.ReloadAsync();

            // Assert
            Assert.False(newService.HasKey("any.key"));
        }
        finally
        {
            if (File.Exists(newConfigPath))
            {
                File.Delete(newConfigPath);
            }
        }
    }

    [Fact]
    public async Task SaveAsync_CreatesDirectory()
    {
        // Arrange
        var testDir = Path.Combine(Path.GetTempPath(), $"test_dir_{Guid.NewGuid()}");
        var configPath = Path.Combine(testDir, "subdir", "config.json");
        var service = new ConfigurationService(_mockLogger.Object, configPath);

        try
        {
            service.SetValue("test.key", "test.value");

            // Act
            await service.SaveAsync();

            // Assert
            Assert.True(File.Exists(configPath));
        }
        finally
        {
            if (Directory.Exists(testDir))
            {
                Directory.Delete(testDir, recursive: true);
            }
        }
    }

    [Fact]
    public void SetValue_OverwritesExistingValue()
    {
        // Arrange
        var key = "test.overwrite";
        var value1 = "first value";
        var value2 = "second value";

        // Act
        _service.SetValue(key, value1);
        var firstResult = _service.GetValue<string>(key);

        _service.SetValue(key, value2);
        var secondResult = _service.GetValue<string>(key);

        // Assert
        Assert.Equal(value1, firstResult);
        Assert.Equal(value2, secondResult);
    }

    [Fact]
    public void GetValue_WithComplexType_ReturnsDefaultOnFailure()
    {
        // Arrange
        var key = "test.invalid";
        _service.SetValue(key, "not a complex object");

        // Act
        var result = _service.GetValue<ComplexType>(key);

        // Assert
        Assert.Null(result);
    }

    private class ComplexType
    {
        public string Name { get; set; } = string.Empty;
        public int Value { get; set; }
    }
}
