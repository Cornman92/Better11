using Better11.Core.Interfaces;
using Better11.Core.Models;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Microsoft.Extensions.Logging;
using System.Collections.ObjectModel;

namespace Better11.App.ViewModels;

/// <summary>
/// ViewModel for file operations feature.
/// </summary>
public partial class FileOperationsViewModel : ViewModelBase
{
    private readonly ILogger<FileOperationsViewModel> _logger;
    private readonly IFileSystemService _fileSystemService;
    private readonly ISecurityService _securityService;
    private readonly IDialogService _dialogService;

    private string _sourcePath = string.Empty;
    private string _destinationPath = string.Empty;
    private string _searchPattern = "*.*";
    private bool _recursive;
    private string _operationLog = string.Empty;
    private ObservableCollection<FileOperationItem> _fileList = new();
    private int _progressValue;
    private int _progressMaximum = 100;
    private string _progressText = string.Empty;

    /// <summary>
    /// Initializes a new instance of the <see cref="FileOperationsViewModel"/> class.
    /// </summary>
    public FileOperationsViewModel(
        ILogger<FileOperationsViewModel> logger,
        IFileSystemService fileSystemService,
        ISecurityService securityService,
        IDialogService dialogService)
    {
        _logger = logger;
        _fileSystemService = fileSystemService;
        _securityService = securityService;
        _dialogService = dialogService;

        Title = "File Operations";
    }

    /// <summary>
    /// Gets or sets the source path.
    /// </summary>
    public string SourcePath
    {
        get => _sourcePath;
        set => SetProperty(ref _sourcePath, value);
    }

    /// <summary>
    /// Gets or sets the destination path.
    /// </summary>
    public string DestinationPath
    {
        get => _destinationPath;
        set => SetProperty(ref _destinationPath, value);
    }

    /// <summary>
    /// Gets or sets the search pattern.
    /// </summary>
    public string SearchPattern
    {
        get => _searchPattern;
        set => SetProperty(ref _searchPattern, value);
    }

    /// <summary>
    /// Gets or sets whether to search recursively.
    /// </summary>
    public bool Recursive
    {
        get => _recursive;
        set => SetProperty(ref _recursive, value);
    }

    /// <summary>
    /// Gets or sets the operation log.
    /// </summary>
    public string OperationLog
    {
        get => _operationLog;
        set => SetProperty(ref _operationLog, value);
    }

    /// <summary>
    /// Gets or sets the file list.
    /// </summary>
    public ObservableCollection<FileOperationItem> FileList
    {
        get => _fileList;
        set => SetProperty(ref _fileList, value);
    }

    /// <summary>
    /// Gets or sets the progress value.
    /// </summary>
    public int ProgressValue
    {
        get => _progressValue;
        set => SetProperty(ref _progressValue, value);
    }

    /// <summary>
    /// Gets or sets the progress maximum.
    /// </summary>
    public int ProgressMaximum
    {
        get => _progressMaximum;
        set => SetProperty(ref _progressMaximum, value);
    }

    /// <summary>
    /// Gets or sets the progress text.
    /// </summary>
    public string ProgressText
    {
        get => _progressText;
        set => SetProperty(ref _progressText, value);
    }

    /// <summary>
    /// Browse for source folder.
    /// </summary>
    [RelayCommand]
    private async Task BrowseSourceAsync()
    {
        try
        {
            var folder = await _dialogService.ShowFolderPickerAsync();
            if (!string.IsNullOrEmpty(folder))
            {
                SourcePath = folder;
                LogOperation($"Source path set to: {folder}");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error browsing for source folder");
            await _dialogService.ShowErrorAsync($"Error selecting folder: {ex.Message}");
        }
    }

    /// <summary>
    /// Browse for destination folder.
    /// </summary>
    [RelayCommand]
    private async Task BrowseDestinationAsync()
    {
        try
        {
            var folder = await _dialogService.ShowFolderPickerAsync();
            if (!string.IsNullOrEmpty(folder))
            {
                DestinationPath = folder;
                LogOperation($"Destination path set to: {folder}");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error browsing for destination folder");
            await _dialogService.ShowErrorAsync($"Error selecting folder: {ex.Message}");
        }
    }

    /// <summary>
    /// Scan files in source directory.
    /// </summary>
    [RelayCommand]
    private async Task ScanFilesAsync()
    {
        if (string.IsNullOrEmpty(SourcePath))
        {
            await _dialogService.ShowWarningAsync("Please select a source path first.");
            return;
        }

        IsBusy = true;
        try
        {
            LogOperation($"Scanning files in {SourcePath} with pattern {SearchPattern}");

            FileList.Clear();

            var result = await _fileSystemService.GetFilesAsync(SourcePath, SearchPattern, Recursive);

            if (result.IsSuccess)
            {
                foreach (var file in result.Value!)
                {
                    var sizeResult = await _fileSystemService.GetFileSizeAsync(file);
                    var size = sizeResult.IsSuccess ? sizeResult.Value : 0;

                    FileList.Add(new FileOperationItem
                    {
                        Path = file,
                        Name = Path.GetFileName(file),
                        Size = size,
                        SizeFormatted = FormatBytes(size),
                        Selected = true
                    });
                }

                LogOperation($"Found {FileList.Count} files");
            }
            else
            {
                LogOperation($"Error scanning files: {result.Error}");
                await _dialogService.ShowErrorAsync($"Error scanning files: {result.Error}");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error scanning files");
            LogOperation($"Exception: {ex.Message}");
            await _dialogService.ShowErrorAsync($"Error scanning files: {ex.Message}");
        }
        finally
        {
            IsBusy = false;
        }
    }

    /// <summary>
    /// Copy selected files.
    /// </summary>
    [RelayCommand]
    private async Task CopyFilesAsync()
    {
        if (string.IsNullOrEmpty(DestinationPath))
        {
            await _dialogService.ShowWarningAsync("Please select a destination path.");
            return;
        }

        var selectedFiles = FileList.Where(f => f.Selected).ToList();
        if (selectedFiles.Count == 0)
        {
            await _dialogService.ShowWarningAsync("No files selected.");
            return;
        }

        var confirmed = await _dialogService.ShowConfirmationAsync(
            $"Copy {selectedFiles.Count} file(s) to {DestinationPath}?",
            "Confirm Copy");

        if (!confirmed)
        {
            return;
        }

        IsBusy = true;
        try
        {
            LogOperation($"Copying {selectedFiles.Count} files to {DestinationPath}");

            ProgressMaximum = selectedFiles.Count;
            ProgressValue = 0;

            var successCount = 0;
            var failCount = 0;

            foreach (var file in selectedFiles)
            {
                ProgressValue++;
                ProgressText = $"Copying {file.Name}...";

                var destFile = Path.Combine(DestinationPath, file.Name);
                var result = await _fileSystemService.CopyFileAsync(file.Path, destFile, overwrite: true);

                if (result.IsSuccess)
                {
                    successCount++;
                    LogOperation($"✓ Copied: {file.Name}");
                }
                else
                {
                    failCount++;
                    LogOperation($"✗ Failed to copy {file.Name}: {result.Error}");
                }
            }

            ProgressText = string.Empty;
            LogOperation($"Copy complete: {successCount} succeeded, {failCount} failed");

            await _dialogService.ShowInfoAsync(
                $"Copy operation completed.\n{successCount} files copied successfully.\n{failCount} files failed.");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error copying files");
            LogOperation($"Exception: {ex.Message}");
            await _dialogService.ShowErrorAsync($"Error copying files: {ex.Message}");
        }
        finally
        {
            IsBusy = false;
            ProgressValue = 0;
            ProgressText = string.Empty;
        }
    }

    /// <summary>
    /// Move selected files.
    /// </summary>
    [RelayCommand]
    private async Task MoveFilesAsync()
    {
        if (string.IsNullOrEmpty(DestinationPath))
        {
            await _dialogService.ShowWarningAsync("Please select a destination path.");
            return;
        }

        var selectedFiles = FileList.Where(f => f.Selected).ToList();
        if (selectedFiles.Count == 0)
        {
            await _dialogService.ShowWarningAsync("No files selected.");
            return;
        }

        var confirmed = await _dialogService.ShowConfirmationAsync(
            $"Move {selectedFiles.Count} file(s) to {DestinationPath}?",
            "Confirm Move");

        if (!confirmed)
        {
            return;
        }

        IsBusy = true;
        try
        {
            LogOperation($"Moving {selectedFiles.Count} files to {DestinationPath}");

            ProgressMaximum = selectedFiles.Count;
            ProgressValue = 0;

            var successCount = 0;
            var failCount = 0;

            foreach (var file in selectedFiles)
            {
                ProgressValue++;
                ProgressText = $"Moving {file.Name}...";

                var destFile = Path.Combine(DestinationPath, file.Name);
                var result = await _fileSystemService.MoveFileAsync(file.Path, destFile, overwrite: true);

                if (result.IsSuccess)
                {
                    successCount++;
                    LogOperation($"✓ Moved: {file.Name}");
                }
                else
                {
                    failCount++;
                    LogOperation($"✗ Failed to move {file.Name}: {result.Error}");
                }
            }

            ProgressText = string.Empty;
            LogOperation($"Move complete: {successCount} succeeded, {failCount} failed");

            await _dialogService.ShowInfoAsync(
                $"Move operation completed.\n{successCount} files moved successfully.\n{failCount} files failed.");

            // Refresh the file list
            await ScanFilesAsync();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error moving files");
            LogOperation($"Exception: {ex.Message}");
            await _dialogService.ShowErrorAsync($"Error moving files: {ex.Message}");
        }
        finally
        {
            IsBusy = false;
            ProgressValue = 0;
            ProgressText = string.Empty;
        }
    }

    /// <summary>
    /// Delete selected files.
    /// </summary>
    [RelayCommand]
    private async Task DeleteFilesAsync()
    {
        var selectedFiles = FileList.Where(f => f.Selected).ToList();
        if (selectedFiles.Count == 0)
        {
            await _dialogService.ShowWarningAsync("No files selected.");
            return;
        }

        var confirmed = await _dialogService.ShowConfirmationAsync(
            $"Delete {selectedFiles.Count} file(s)? This cannot be undone.",
            "Confirm Delete");

        if (!confirmed)
        {
            return;
        }

        IsBusy = true;
        try
        {
            LogOperation($"Deleting {selectedFiles.Count} files");

            ProgressMaximum = selectedFiles.Count;
            ProgressValue = 0;

            var successCount = 0;
            var failCount = 0;

            foreach (var file in selectedFiles)
            {
                ProgressValue++;
                ProgressText = $"Deleting {file.Name}...";

                var result = await _fileSystemService.DeleteFileAsync(file.Path);

                if (result.IsSuccess)
                {
                    successCount++;
                    LogOperation($"✓ Deleted: {file.Name}");
                }
                else
                {
                    failCount++;
                    LogOperation($"✗ Failed to delete {file.Name}: {result.Error}");
                }
            }

            ProgressText = string.Empty;
            LogOperation($"Delete complete: {successCount} succeeded, {failCount} failed");

            await _dialogService.ShowInfoAsync(
                $"Delete operation completed.\n{successCount} files deleted successfully.\n{failCount} files failed.");

            // Refresh the file list
            await ScanFilesAsync();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error deleting files");
            LogOperation($"Exception: {ex.Message}");
            await _dialogService.ShowErrorAsync($"Error deleting files: {ex.Message}");
        }
        finally
        {
            IsBusy = false;
            ProgressValue = 0;
            ProgressText = string.Empty;
        }
    }

    /// <summary>
    /// Compute hashes for selected files.
    /// </summary>
    [RelayCommand]
    private async Task ComputeHashesAsync()
    {
        var selectedFiles = FileList.Where(f => f.Selected).ToList();
        if (selectedFiles.Count == 0)
        {
            await _dialogService.ShowWarningAsync("No files selected.");
            return;
        }

        IsBusy = true;
        try
        {
            LogOperation($"Computing hashes for {selectedFiles.Count} files");

            ProgressMaximum = selectedFiles.Count;
            ProgressValue = 0;

            foreach (var file in selectedFiles)
            {
                ProgressValue++;
                ProgressText = $"Hashing {file.Name}...";

                var result = await _securityService.ComputeFileHashAsync(file.Path);

                if (result.IsSuccess)
                {
                    file.Hash = result.Value!;
                    LogOperation($"✓ {file.Name}: {result.Value}");
                }
                else
                {
                    LogOperation($"✗ Failed to hash {file.Name}: {result.Error}");
                }
            }

            ProgressText = string.Empty;
            LogOperation("Hash computation complete");

            await _dialogService.ShowInfoAsync("Hash computation completed successfully.");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error computing hashes");
            LogOperation($"Exception: {ex.Message}");
            await _dialogService.ShowErrorAsync($"Error computing hashes: {ex.Message}");
        }
        finally
        {
            IsBusy = false;
            ProgressValue = 0;
            ProgressText = string.Empty;
        }
    }

    /// <summary>
    /// Select or deselect all files.
    /// </summary>
    [RelayCommand]
    private void SelectAll(bool select)
    {
        foreach (var file in FileList)
        {
            file.Selected = select;
        }
    }

    /// <summary>
    /// Clear the operation log.
    /// </summary>
    [RelayCommand]
    private void ClearLog()
    {
        OperationLog = string.Empty;
    }

    /// <summary>
    /// Format bytes to human-readable format.
    /// </summary>
    private string FormatBytes(long bytes)
    {
        string[] sizes = { "B", "KB", "MB", "GB", "TB" };
        double len = bytes;
        int order = 0;

        while (len >= 1024 && order < sizes.Length - 1)
        {
            order++;
            len /= 1024;
        }

        return $"{len:0.##} {sizes[order]}";
    }

    /// <summary>
    /// Log an operation.
    /// </summary>
    private void LogOperation(string message)
    {
        var timestamp = DateTime.Now.ToString("HH:mm:ss");
        var logEntry = $"[{timestamp}] {message}{Environment.NewLine}";

        OperationLog += logEntry;
        _logger.LogInformation(message);
    }

    /// <inheritdoc/>
    public override async Task InitializeAsync()
    {
        await base.InitializeAsync();
        LogOperation("File Operations initialized");
    }
}

/// <summary>
/// Represents a file operation item.
/// </summary>
public class FileOperationItem : ObservableObject
{
    private bool _selected;
    private string _hash = string.Empty;

    /// <summary>
    /// Gets or sets the file path.
    /// </summary>
    public string Path { get; set; } = string.Empty;

    /// <summary>
    /// Gets or sets the file name.
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// Gets or sets the file size.
    /// </summary>
    public long Size { get; set; }

    /// <summary>
    /// Gets or sets the formatted file size.
    /// </summary>
    public string SizeFormatted { get; set; } = string.Empty;

    /// <summary>
    /// Gets or sets whether the file is selected.
    /// </summary>
    public bool Selected
    {
        get => _selected;
        set => SetProperty(ref _selected, value);
    }

    /// <summary>
    /// Gets or sets the file hash.
    /// </summary>
    public string Hash
    {
        get => _hash;
        set => SetProperty(ref _hash, value);
    }
}
