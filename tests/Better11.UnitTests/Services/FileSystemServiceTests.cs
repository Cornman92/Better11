using Better11.Core.Interfaces;
using Better11.Services;
using Microsoft.Extensions.Logging;
using Moq;
using Xunit;

namespace Better11.UnitTests.Services;

/// <summary>
/// Unit tests for <see cref="FileSystemService"/>.
/// </summary>
public class FileSystemServiceTests : IDisposable
{
    private readonly Mock<ILogger<FileSystemService>> _mockLogger;
    private readonly IFileSystemService _service;
    private readonly string _testDirectory;

    public FileSystemServiceTests()
    {
        _mockLogger = new Mock<ILogger<FileSystemService>>();
        _service = new FileSystemService(_mockLogger.Object);

        // Create a temporary test directory
        _testDirectory = Path.Combine(Path.GetTempPath(), $"Better11_Tests_{Guid.NewGuid()}");
        Directory.CreateDirectory(_testDirectory);
    }

    public void Dispose()
    {
        // Clean up test directory
        if (Directory.Exists(_testDirectory))
        {
            Directory.Delete(_testDirectory, recursive: true);
        }
    }

    [Fact]
    public void FileExists_ExistingFile_ReturnsTrue()
    {
        // Arrange
        var testFile = Path.Combine(_testDirectory, "test.txt");
        File.WriteAllText(testFile, "test content");

        // Act
        var result = _service.FileExists(testFile);

        // Assert
        Assert.True(result);
    }

    [Fact]
    public void FileExists_NonExistingFile_ReturnsFalse()
    {
        // Arrange
        var testFile = Path.Combine(_testDirectory, "nonexistent.txt");

        // Act
        var result = _service.FileExists(testFile);

        // Assert
        Assert.False(result);
    }

    [Fact]
    public void DirectoryExists_ExistingDirectory_ReturnsTrue()
    {
        // Act
        var result = _service.DirectoryExists(_testDirectory);

        // Assert
        Assert.True(result);
    }

    [Fact]
    public void DirectoryExists_NonExistingDirectory_ReturnsFalse()
    {
        // Arrange
        var nonExistentDir = Path.Combine(_testDirectory, "nonexistent");

        // Act
        var result = _service.DirectoryExists(nonExistentDir);

        // Assert
        Assert.False(result);
    }

    [Fact]
    public async Task CopyFileAsync_ValidFiles_Success()
    {
        // Arrange
        var sourceFile = Path.Combine(_testDirectory, "source.txt");
        var destFile = Path.Combine(_testDirectory, "dest.txt");
        var content = "test content";
        File.WriteAllText(sourceFile, content);

        // Act
        var result = await _service.CopyFileAsync(sourceFile, destFile);

        // Assert
        Assert.True(result.IsSuccess);
        Assert.True(File.Exists(destFile));
        Assert.Equal(content, File.ReadAllText(destFile));
    }

    [Fact]
    public async Task CopyFileAsync_NonExistingSource_Failure()
    {
        // Arrange
        var sourceFile = Path.Combine(_testDirectory, "nonexistent.txt");
        var destFile = Path.Combine(_testDirectory, "dest.txt");

        // Act
        var result = await _service.CopyFileAsync(sourceFile, destFile);

        // Assert
        Assert.True(result.IsFailure);
        Assert.Contains("not found", result.Error!, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public async Task CopyFileAsync_CreatesDestinationDirectory()
    {
        // Arrange
        var sourceFile = Path.Combine(_testDirectory, "source.txt");
        var destDir = Path.Combine(_testDirectory, "subdir");
        var destFile = Path.Combine(destDir, "dest.txt");
        File.WriteAllText(sourceFile, "test");

        // Act
        var result = await _service.CopyFileAsync(sourceFile, destFile);

        // Assert
        Assert.True(result.IsSuccess);
        Assert.True(Directory.Exists(destDir));
        Assert.True(File.Exists(destFile));
    }

    [Fact]
    public async Task WriteFileAsync_ValidPath_Success()
    {
        // Arrange
        var testFile = Path.Combine(_testDirectory, "write.txt");
        var content = "Hello, World!";

        // Act
        var result = await _service.WriteFileAsync(testFile, content);

        // Assert
        Assert.True(result.IsSuccess);
        Assert.True(File.Exists(testFile));
        Assert.Equal(content, File.ReadAllText(testFile));
    }

    [Fact]
    public async Task ReadFileAsync_ExistingFile_Success()
    {
        // Arrange
        var testFile = Path.Combine(_testDirectory, "read.txt");
        var content = "Test content";
        File.WriteAllText(testFile, content);

        // Act
        var result = await _service.ReadFileAsync(testFile);

        // Assert
        Assert.True(result.IsSuccess);
        Assert.Equal(content, result.Value);
    }

    [Fact]
    public async Task ReadFileAsync_NonExistingFile_Failure()
    {
        // Arrange
        var testFile = Path.Combine(_testDirectory, "nonexistent.txt");

        // Act
        var result = await _service.ReadFileAsync(testFile);

        // Assert
        Assert.True(result.IsFailure);
        Assert.NotNull(result.Error);
    }

    [Fact]
    public async Task DeleteFileAsync_ExistingFile_Success()
    {
        // Arrange
        var testFile = Path.Combine(_testDirectory, "delete.txt");
        File.WriteAllText(testFile, "to be deleted");

        // Act
        var result = await _service.DeleteFileAsync(testFile);

        // Assert
        Assert.True(result.IsSuccess);
        Assert.False(File.Exists(testFile));
    }

    [Fact]
    public async Task GetFilesAsync_ReturnsFiles()
    {
        // Arrange
        var file1 = Path.Combine(_testDirectory, "file1.txt");
        var file2 = Path.Combine(_testDirectory, "file2.txt");
        var file3 = Path.Combine(_testDirectory, "file3.doc");
        File.WriteAllText(file1, "content1");
        File.WriteAllText(file2, "content2");
        File.WriteAllText(file3, "content3");

        // Act
        var result = await _service.GetFilesAsync(_testDirectory, "*.txt");

        // Assert
        Assert.True(result.IsSuccess);
        Assert.Equal(2, result.Value!.Count());
    }

    [Fact]
    public async Task CreateDirectoryAsync_NewDirectory_Success()
    {
        // Arrange
        var newDir = Path.Combine(_testDirectory, "newdir");

        // Act
        var result = await _service.CreateDirectoryAsync(newDir);

        // Assert
        Assert.True(result.IsSuccess);
        Assert.True(Directory.Exists(newDir));
    }

    [Fact]
    public async Task GetFileSizeAsync_ExistingFile_ReturnsSize()
    {
        // Arrange
        var testFile = Path.Combine(_testDirectory, "size.txt");
        var content = "1234567890";
        File.WriteAllText(testFile, content);

        // Act
        var result = await _service.GetFileSizeAsync(testFile);

        // Assert
        Assert.True(result.IsSuccess);
        Assert.True(result.Value > 0);
    }

    [Fact]
    public async Task MoveFileAsync_ValidFiles_Success()
    {
        // Arrange
        var sourceFile = Path.Combine(_testDirectory, "move_source.txt");
        var destFile = Path.Combine(_testDirectory, "move_dest.txt");
        var content = "move me";
        File.WriteAllText(sourceFile, content);

        // Act
        var result = await _service.MoveFileAsync(sourceFile, destFile);

        // Assert
        Assert.True(result.IsSuccess);
        Assert.False(File.Exists(sourceFile));
        Assert.True(File.Exists(destFile));
        Assert.Equal(content, File.ReadAllText(destFile));
    }
}
