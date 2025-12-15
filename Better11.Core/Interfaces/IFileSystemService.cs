using Better11.Core.Models;

namespace Better11.Core.Interfaces;

/// <summary>
/// Service for file system operations.
/// </summary>
public interface IFileSystemService
{
    /// <summary>
    /// Checks if a file exists at the specified path.
    /// </summary>
    /// <param name="path">The path to check.</param>
    /// <returns>True if the file exists; otherwise, false.</returns>
    bool FileExists(string path);

    /// <summary>
    /// Checks if a directory exists at the specified path.
    /// </summary>
    /// <param name="path">The path to check.</param>
    /// <returns>True if the directory exists; otherwise, false.</returns>
    bool DirectoryExists(string path);

    /// <summary>
    /// Copies a file to a new location.
    /// </summary>
    /// <param name="sourcePath">The source file path.</param>
    /// <param name="destinationPath">The destination file path.</param>
    /// <param name="overwrite">Whether to overwrite if destination exists.</param>
    /// <returns>Result indicating success or failure.</returns>
    Task<Result> CopyFileAsync(string sourcePath, string destinationPath, bool overwrite = false);

    /// <summary>
    /// Moves a file to a new location.
    /// </summary>
    /// <param name="sourcePath">The source file path.</param>
    /// <param name="destinationPath">The destination file path.</param>
    /// <param name="overwrite">Whether to overwrite if destination exists.</param>
    /// <returns>Result indicating success or failure.</returns>
    Task<Result> MoveFileAsync(string sourcePath, string destinationPath, bool overwrite = false);

    /// <summary>
    /// Deletes a file.
    /// </summary>
    /// <param name="path">The path of the file to delete.</param>
    /// <returns>Result indicating success or failure.</returns>
    Task<Result> DeleteFileAsync(string path);

    /// <summary>
    /// Reads all text from a file.
    /// </summary>
    /// <param name="path">The path of the file to read.</param>
    /// <returns>Result containing the file content or an error.</returns>
    Task<Result<string>> ReadFileAsync(string path);

    /// <summary>
    /// Writes text to a file.
    /// </summary>
    /// <param name="path">The path of the file to write.</param>
    /// <param name="content">The content to write.</param>
    /// <returns>Result indicating success or failure.</returns>
    Task<Result> WriteFileAsync(string path, string content);

    /// <summary>
    /// Gets all files in a directory.
    /// </summary>
    /// <param name="path">The directory path.</param>
    /// <param name="searchPattern">Optional search pattern.</param>
    /// <param name="recursive">Whether to search recursively.</param>
    /// <returns>Result containing list of file paths.</returns>
    Task<Result<IEnumerable<string>>> GetFilesAsync(string path, string searchPattern = "*", bool recursive = false);

    /// <summary>
    /// Creates a directory.
    /// </summary>
    /// <param name="path">The path of the directory to create.</param>
    /// <returns>Result indicating success or failure.</returns>
    Task<Result> CreateDirectoryAsync(string path);

    /// <summary>
    /// Gets the size of a file in bytes.
    /// </summary>
    /// <param name="path">The path of the file.</param>
    /// <returns>Result containing the file size.</returns>
    Task<Result<long>> GetFileSizeAsync(string path);
}
