using Better11.Core.Interfaces;
using Better11.Core.Models;
using Microsoft.Extensions.Logging;

namespace Better11.Services;

/// <summary>
/// Implementation of file system operations service.
/// </summary>
public class FileSystemService : IFileSystemService
{
    private readonly ILogger<FileSystemService> _logger;

    /// <summary>
    /// Initializes a new instance of the <see cref="FileSystemService"/> class.
    /// </summary>
    /// <param name="logger">The logger instance.</param>
    public FileSystemService(ILogger<FileSystemService> logger)
    {
        _logger = logger;
    }

    /// <inheritdoc/>
    public bool FileExists(string path)
    {
        return File.Exists(path);
    }

    /// <inheritdoc/>
    public bool DirectoryExists(string path)
    {
        return Directory.Exists(path);
    }

    /// <inheritdoc/>
    public async Task<Result> CopyFileAsync(string sourcePath, string destinationPath, bool overwrite = false)
    {
        try
        {
            _logger.LogInformation("Copying file from {Source} to {Destination}", sourcePath, destinationPath);

            if (!File.Exists(sourcePath))
            {
                return Result.Failure($"Source file not found: {sourcePath}");
            }

            // Ensure destination directory exists
            var destinationDir = Path.GetDirectoryName(destinationPath);
            if (!string.IsNullOrEmpty(destinationDir) && !Directory.Exists(destinationDir))
            {
                Directory.CreateDirectory(destinationDir);
            }

            await Task.Run(() => File.Copy(sourcePath, destinationPath, overwrite));

            _logger.LogInformation("File copied successfully");
            return Result.Success();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error copying file from {Source} to {Destination}", sourcePath, destinationPath);
            return Result.Failure($"Failed to copy file: {ex.Message}");
        }
    }

    /// <inheritdoc/>
    public async Task<Result> MoveFileAsync(string sourcePath, string destinationPath, bool overwrite = false)
    {
        try
        {
            _logger.LogInformation("Moving file from {Source} to {Destination}", sourcePath, destinationPath);

            if (!File.Exists(sourcePath))
            {
                return Result.Failure($"Source file not found: {sourcePath}");
            }

            // Ensure destination directory exists
            var destinationDir = Path.GetDirectoryName(destinationPath);
            if (!string.IsNullOrEmpty(destinationDir) && !Directory.Exists(destinationDir))
            {
                Directory.CreateDirectory(destinationDir);
            }

            await Task.Run(() => File.Move(sourcePath, destinationPath, overwrite));

            _logger.LogInformation("File moved successfully");
            return Result.Success();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error moving file from {Source} to {Destination}", sourcePath, destinationPath);
            return Result.Failure($"Failed to move file: {ex.Message}");
        }
    }

    /// <inheritdoc/>
    public async Task<Result> DeleteFileAsync(string path)
    {
        try
        {
            _logger.LogInformation("Deleting file: {Path}", path);

            if (!File.Exists(path))
            {
                return Result.Failure($"File not found: {path}");
            }

            await Task.Run(() => File.Delete(path));

            _logger.LogInformation("File deleted successfully");
            return Result.Success();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error deleting file: {Path}", path);
            return Result.Failure($"Failed to delete file: {ex.Message}");
        }
    }

    /// <inheritdoc/>
    public async Task<Result<string>> ReadFileAsync(string path)
    {
        try
        {
            _logger.LogDebug("Reading file: {Path}", path);

            if (!File.Exists(path))
            {
                return Result<string>.Failure($"File not found: {path}");
            }

            var content = await File.ReadAllTextAsync(path);

            _logger.LogDebug("File read successfully, {Length} characters", content.Length);
            return Result<string>.Success(content);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error reading file: {Path}", path);
            return Result<string>.Failure($"Failed to read file: {ex.Message}");
        }
    }

    /// <inheritdoc/>
    public async Task<Result> WriteFileAsync(string path, string content)
    {
        try
        {
            _logger.LogInformation("Writing to file: {Path}", path);

            // Ensure directory exists
            var directory = Path.GetDirectoryName(path);
            if (!string.IsNullOrEmpty(directory) && !Directory.Exists(directory))
            {
                Directory.CreateDirectory(directory);
            }

            await File.WriteAllTextAsync(path, content);

            _logger.LogInformation("File written successfully, {Length} characters", content.Length);
            return Result.Success();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error writing to file: {Path}", path);
            return Result.Failure($"Failed to write file: {ex.Message}");
        }
    }

    /// <inheritdoc/>
    public async Task<Result<IEnumerable<string>>> GetFilesAsync(string path, string searchPattern = "*", bool recursive = false)
    {
        try
        {
            _logger.LogDebug("Getting files from {Path} with pattern {Pattern}", path, searchPattern);

            if (!Directory.Exists(path))
            {
                return Result<IEnumerable<string>>.Failure($"Directory not found: {path}");
            }

            var searchOption = recursive ? SearchOption.AllDirectories : SearchOption.TopDirectoryOnly;
            var files = await Task.Run(() => Directory.GetFiles(path, searchPattern, searchOption));

            _logger.LogDebug("Found {Count} files", files.Length);
            return Result<IEnumerable<string>>.Success(files);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting files from {Path}", path);
            return Result<IEnumerable<string>>.Failure($"Failed to get files: {ex.Message}");
        }
    }

    /// <inheritdoc/>
    public async Task<Result> CreateDirectoryAsync(string path)
    {
        try
        {
            _logger.LogInformation("Creating directory: {Path}", path);

            await Task.Run(() => Directory.CreateDirectory(path));

            _logger.LogInformation("Directory created successfully");
            return Result.Success();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error creating directory: {Path}", path);
            return Result.Failure($"Failed to create directory: {ex.Message}");
        }
    }

    /// <inheritdoc/>
    public async Task<Result<long>> GetFileSizeAsync(string path)
    {
        try
        {
            _logger.LogDebug("Getting file size: {Path}", path);

            if (!File.Exists(path))
            {
                return Result<long>.Failure($"File not found: {path}");
            }

            var size = await Task.Run(() => new FileInfo(path).Length);

            _logger.LogDebug("File size: {Size} bytes", size);
            return Result<long>.Success(size);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting file size: {Path}", path);
            return Result<long>.Failure($"Failed to get file size: {ex.Message}");
        }
    }
}
