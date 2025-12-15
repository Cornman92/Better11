using Better11.Core.Interfaces;
using Better11.Services;
using Microsoft.Extensions.Logging;
using Moq;
using Xunit;

namespace Better11.UnitTests.Services;

/// <summary>
/// Unit tests for <see cref="SecurityService"/>.
/// </summary>
public class SecurityServiceTests : IDisposable
{
    private readonly Mock<ILogger<SecurityService>> _mockLogger;
    private readonly ISecurityService _service;
    private readonly string _testDirectory;

    public SecurityServiceTests()
    {
        _mockLogger = new Mock<ILogger<SecurityService>>();
        _service = new SecurityService(_mockLogger.Object);

        _testDirectory = Path.Combine(Path.GetTempPath(), $"Better11_SecTests_{Guid.NewGuid()}");
        Directory.CreateDirectory(_testDirectory);
    }

    public void Dispose()
    {
        if (Directory.Exists(_testDirectory))
        {
            Directory.Delete(_testDirectory, recursive: true);
        }
    }

    [Fact]
    public void IsAdministrator_ReturnsBoolean()
    {
        // Act
        var result = _service.IsAdministrator();

        // Assert
        Assert.IsType<bool>(result);
    }

    [Fact]
    public void EncryptString_ValidInput_ReturnsEncryptedString()
    {
        // Arrange
        var plainText = "my secret password";

        // Act
        var encrypted = _service.EncryptString(plainText);

        // Assert
        Assert.NotNull(encrypted);
        Assert.NotEmpty(encrypted);
        Assert.NotEqual(plainText, encrypted);
    }

    [Fact]
    public void EncryptDecrypt_RoundTrip_Success()
    {
        // Arrange
        var plainText = "my secret password";

        // Act
        var encrypted = _service.EncryptString(plainText);
        var decrypted = _service.DecryptString(encrypted);

        // Assert
        Assert.Equal(plainText, decrypted);
    }

    [Fact]
    public void EncryptString_DifferentInputs_ProduceDifferentOutputs()
    {
        // Arrange
        var plainText1 = "password1";
        var plainText2 = "password2";

        // Act
        var encrypted1 = _service.EncryptString(plainText1);
        var encrypted2 = _service.EncryptString(plainText2);

        // Assert
        Assert.NotEqual(encrypted1, encrypted2);
    }

    [Fact]
    public async Task ComputeFileHashAsync_ValidFile_ReturnsHash()
    {
        // Arrange
        var testFile = Path.Combine(_testDirectory, "hash_test.txt");
        var content = "test content for hashing";
        File.WriteAllText(testFile, content);

        // Act
        var result = await _service.ComputeFileHashAsync(testFile);

        // Assert
        Assert.True(result.IsSuccess);
        Assert.NotNull(result.Value);
        Assert.NotEmpty(result.Value);
        Assert.Equal(64, result.Value.Length); // SHA256 produces 64 hex characters
    }

    [Fact]
    public async Task ComputeFileHashAsync_SameContent_SameHash()
    {
        // Arrange
        var file1 = Path.Combine(_testDirectory, "hash1.txt");
        var file2 = Path.Combine(_testDirectory, "hash2.txt");
        var content = "identical content";
        File.WriteAllText(file1, content);
        File.WriteAllText(file2, content);

        // Act
        var hash1 = await _service.ComputeFileHashAsync(file1);
        var hash2 = await _service.ComputeFileHashAsync(file2);

        // Assert
        Assert.True(hash1.IsSuccess);
        Assert.True(hash2.IsSuccess);
        Assert.Equal(hash1.Value, hash2.Value);
    }

    [Fact]
    public async Task ComputeFileHashAsync_DifferentContent_DifferentHash()
    {
        // Arrange
        var file1 = Path.Combine(_testDirectory, "diff1.txt");
        var file2 = Path.Combine(_testDirectory, "diff2.txt");
        File.WriteAllText(file1, "content 1");
        File.WriteAllText(file2, "content 2");

        // Act
        var hash1 = await _service.ComputeFileHashAsync(file1);
        var hash2 = await _service.ComputeFileHashAsync(file2);

        // Assert
        Assert.True(hash1.IsSuccess);
        Assert.True(hash2.IsSuccess);
        Assert.NotEqual(hash1.Value, hash2.Value);
    }

    [Fact]
    public async Task ComputeFileHashAsync_NonExistingFile_Failure()
    {
        // Arrange
        var nonExistentFile = Path.Combine(_testDirectory, "nonexistent.txt");

        // Act
        var result = await _service.ComputeFileHashAsync(nonExistentFile);

        // Assert
        Assert.True(result.IsFailure);
        Assert.NotNull(result.Error);
    }

    [Fact]
    public async Task ValidateFileIntegrityAsync_MatchingHash_ReturnsTrue()
    {
        // Arrange
        var testFile = Path.Combine(_testDirectory, "integrity.txt");
        var content = "test content";
        File.WriteAllText(testFile, content);

        var hashResult = await _service.ComputeFileHashAsync(testFile);
        var expectedHash = hashResult.Value!;

        // Act
        var result = await _service.ValidateFileIntegrityAsync(testFile, expectedHash);

        // Assert
        Assert.True(result.IsSuccess);
        Assert.True(result.Value);
    }

    [Fact]
    public async Task ValidateFileIntegrityAsync_DifferentHash_ReturnsFalse()
    {
        // Arrange
        var testFile = Path.Combine(_testDirectory, "tampered.txt");
        File.WriteAllText(testFile, "original content");

        var originalHashResult = await _service.ComputeFileHashAsync(testFile);
        var originalHash = originalHashResult.Value!;

        // Modify the file
        File.WriteAllText(testFile, "tampered content");

        // Act
        var result = await _service.ValidateFileIntegrityAsync(testFile, originalHash);

        // Assert
        Assert.True(result.IsSuccess);
        Assert.False(result.Value);
    }

    [Fact]
    public void DecryptString_EmptyString_ReturnsEmpty()
    {
        // Arrange
        var encrypted = _service.EncryptString(string.Empty);

        // Act
        var decrypted = _service.DecryptString(encrypted);

        // Assert
        Assert.Equal(string.Empty, decrypted);
    }
}
