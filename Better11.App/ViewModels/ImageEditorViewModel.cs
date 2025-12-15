using Better11.Core.Interfaces;
using Better11.Core.Models;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Microsoft.Extensions.Logging;

namespace Better11.App.ViewModels;

/// <summary>
/// ViewModel for the Image Editor feature.
/// </summary>
public partial class ImageEditorViewModel : ViewModelBase
{
    private readonly ILogger<ImageEditorViewModel> _logger;
    private readonly IFileSystemService _fileSystemService;
    private readonly IProcessService _processService;
    private readonly IPowerShellEngine _powerShellEngine;
    private readonly IDialogService _dialogService;

    private string _imagePath = string.Empty;
    private string _mountPath = string.Empty;
    private string _imageInfo = "No image loaded";
    private bool _isImageMounted;
    private bool _isImageLoaded;
    private string _selectedIndex = "1";
    private List<string> _availableIndexes = new();
    private string _operationLog = string.Empty;

    /// <summary>
    /// Initializes a new instance of the <see cref="ImageEditorViewModel"/> class.
    /// </summary>
    public ImageEditorViewModel(
        ILogger<ImageEditorViewModel> logger,
        IFileSystemService fileSystemService,
        IProcessService processService,
        IPowerShellEngine powerShellEngine,
        IDialogService dialogService)
    {
        _logger = logger;
        _fileSystemService = fileSystemService;
        _processService = processService;
        _powerShellEngine = powerShellEngine;
        _dialogService = dialogService;

        Title = "Image Editor";

        // Set default mount path
        _mountPath = Path.Combine(Path.GetTempPath(), "Better11_Mount");
    }

    /// <summary>
    /// Gets or sets the path to the Windows image file.
    /// </summary>
    public string ImagePath
    {
        get => _imagePath;
        set => SetProperty(ref _imagePath, value);
    }

    /// <summary>
    /// Gets or sets the mount path for the image.
    /// </summary>
    public string MountPath
    {
        get => _mountPath;
        set => SetProperty(ref _mountPath, value);
    }

    /// <summary>
    /// Gets or sets the image information.
    /// </summary>
    public string ImageInfo
    {
        get => _imageInfo;
        set => SetProperty(ref _imageInfo, value);
    }

    /// <summary>
    /// Gets or sets whether an image is currently mounted.
    /// </summary>
    public bool IsImageMounted
    {
        get => _isImageMounted;
        set
        {
            if (SetProperty(ref _isImageMounted, value))
            {
                OnPropertyChanged(nameof(CanMountImage));
                OnPropertyChanged(nameof(CanUnmountImage));
            }
        }
    }

    /// <summary>
    /// Gets or sets whether an image is loaded.
    /// </summary>
    public bool IsImageLoaded
    {
        get => _isImageLoaded;
        set
        {
            if (SetProperty(ref _isImageLoaded, value))
            {
                OnPropertyChanged(nameof(CanMountImage));
            }
        }
    }

    /// <summary>
    /// Gets or sets the selected image index.
    /// </summary>
    public string SelectedIndex
    {
        get => _selectedIndex;
        set => SetProperty(ref _selectedIndex, value);
    }

    /// <summary>
    /// Gets or sets the list of available image indexes.
    /// </summary>
    public List<string> AvailableIndexes
    {
        get => _availableIndexes;
        set => SetProperty(ref _availableIndexes, value);
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
    /// Gets whether an image can be mounted.
    /// </summary>
    public bool CanMountImage => IsImageLoaded && !IsImageMounted && !IsBusy;

    /// <summary>
    /// Gets whether an image can be unmounted.
    /// </summary>
    public bool CanUnmountImage => IsImageMounted && !IsBusy;

    /// <summary>
    /// Browse for a Windows image file.
    /// </summary>
    [RelayCommand]
    private async Task BrowseImageAsync()
    {
        try
        {
            var filePath = await _dialogService.ShowFilePickerAsync("*.wim", "*.iso", "*.esd");

            if (!string.IsNullOrEmpty(filePath))
            {
                ImagePath = filePath;
                await LoadImageInfoAsync();
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error browsing for image file");
            await _dialogService.ShowErrorAsync($"Error browsing for image: {ex.Message}");
        }
    }

    /// <summary>
    /// Load information about the selected image.
    /// </summary>
    [RelayCommand]
    private async Task LoadImageInfoAsync()
    {
        if (string.IsNullOrEmpty(ImagePath))
        {
            await _dialogService.ShowWarningAsync("Please select an image file first.");
            return;
        }

        IsBusy = true;
        try
        {
            LogOperation($"Loading image information from: {ImagePath}");

            // Use DISM to get image info
            var script = $@"
                $imagePath = '{ImagePath.Replace("'", "''")}'
                Get-WindowsImage -ImagePath $imagePath | ForEach-Object {{
                    ""Index: $($_.ImageIndex) - Name: $($_.ImageName) - Size: $([math]::Round($_.ImageSize / 1GB, 2)) GB""
                }}
            ";

            var result = await _powerShellEngine.ExecuteScriptAsync(script);

            if (result.IsSuccess && result.Value!.Success)
            {
                var indexes = new List<string>();
                var infoLines = new List<string>();

                foreach (var output in result.Value.Output)
                {
                    var line = output.ToString() ?? string.Empty;
                    infoLines.Add(line);

                    // Extract index numbers
                    if (line.StartsWith("Index:"))
                    {
                        var indexStr = line.Substring(7, line.IndexOf(" - ") - 7).Trim();
                        indexes.Add(indexStr);
                    }
                }

                AvailableIndexes = indexes;
                if (indexes.Count > 0)
                {
                    SelectedIndex = indexes[0];
                }

                ImageInfo = string.Join(Environment.NewLine, infoLines);
                IsImageLoaded = true;

                LogOperation("Image information loaded successfully");
            }
            else
            {
                var error = result.IsFailure ? result.Error! : string.Join("; ", result.Value.Errors);
                ImageInfo = $"Error loading image: {error}";
                IsImageLoaded = false;

                LogOperation($"Error loading image: {error}");
                await _dialogService.ShowErrorAsync($"Failed to load image information: {error}");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error loading image information");
            ImageInfo = $"Error: {ex.Message}";
            IsImageLoaded = false;

            LogOperation($"Exception: {ex.Message}");
            await _dialogService.ShowErrorAsync($"Error loading image information: {ex.Message}");
        }
        finally
        {
            IsBusy = false;
        }
    }

    /// <summary>
    /// Mount the selected Windows image.
    /// </summary>
    [RelayCommand(CanExecute = nameof(CanMountImage))]
    private async Task MountImageAsync()
    {
        IsBusy = true;
        try
        {
            LogOperation($"Mounting image index {SelectedIndex} to {MountPath}");

            // Create mount directory if it doesn't exist
            var createDirResult = await _fileSystemService.CreateDirectoryAsync(MountPath);
            if (createDirResult.IsFailure)
            {
                await _dialogService.ShowErrorAsync($"Failed to create mount directory: {createDirResult.Error}");
                LogOperation($"Error creating mount directory: {createDirResult.Error}");
                return;
            }

            // Mount the image using DISM
            var script = $@"
                $imagePath = '{ImagePath.Replace("'", "''")}'
                $mountPath = '{MountPath.Replace("'", "''")}'
                $index = {SelectedIndex}

                Mount-WindowsImage -ImagePath $imagePath -Path $mountPath -Index $index -ReadOnly
            ";

            var result = await _powerShellEngine.ExecuteScriptAsync(script);

            if (result.IsSuccess && result.Value!.Success)
            {
                IsImageMounted = true;
                LogOperation("Image mounted successfully");
                await _dialogService.ShowInfoAsync($"Image mounted successfully to {MountPath}");
            }
            else
            {
                var error = result.IsFailure ? result.Error! : string.Join("; ", result.Value.Errors);
                LogOperation($"Error mounting image: {error}");
                await _dialogService.ShowErrorAsync($"Failed to mount image: {error}");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error mounting image");
            LogOperation($"Exception: {ex.Message}");
            await _dialogService.ShowErrorAsync($"Error mounting image: {ex.Message}");
        }
        finally
        {
            IsBusy = false;
        }
    }

    /// <summary>
    /// Unmount the currently mounted image.
    /// </summary>
    [RelayCommand(CanExecute = nameof(CanUnmountImage))]
    private async Task UnmountImageAsync()
    {
        var shouldDiscard = await _dialogService.ShowConfirmationAsync(
            "Do you want to discard changes? Click 'No' to commit changes.",
            "Unmount Image");

        IsBusy = true;
        try
        {
            LogOperation($"Unmounting image from {MountPath}");

            var discardFlag = shouldDiscard ? "-Discard" : "-Save";

            var script = $@"
                $mountPath = '{MountPath.Replace("'", "''")}'
                Dismount-WindowsImage -Path $mountPath {discardFlag}
            ";

            var result = await _powerShellEngine.ExecuteScriptAsync(script);

            if (result.IsSuccess && result.Value!.Success)
            {
                IsImageMounted = false;
                LogOperation("Image unmounted successfully");
                await _dialogService.ShowInfoAsync("Image unmounted successfully");
            }
            else
            {
                var error = result.IsFailure ? result.Error! : string.Join("; ", result.Value.Errors);
                LogOperation($"Error unmounting image: {error}");
                await _dialogService.ShowErrorAsync($"Failed to unmount image: {error}");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error unmounting image");
            LogOperation($"Exception: {ex.Message}");
            await _dialogService.ShowErrorAsync($"Error unmounting image: {ex.Message}");
        }
        finally
        {
            IsBusy = false;
        }
    }

    /// <summary>
    /// Add drivers to the mounted image.
    /// </summary>
    [RelayCommand(CanExecute = nameof(CanUnmountImage))]
    private async Task AddDriversAsync()
    {
        var driverPath = await _dialogService.ShowFolderPickerAsync();

        if (string.IsNullOrEmpty(driverPath))
        {
            return;
        }

        IsBusy = true;
        try
        {
            LogOperation($"Adding drivers from {driverPath}");

            var script = $@"
                $mountPath = '{MountPath.Replace("'", "''")}'
                $driverPath = '{driverPath.Replace("'", "''")}'

                Add-WindowsDriver -Path $mountPath -Driver $driverPath -Recurse
            ";

            var result = await _powerShellEngine.ExecuteScriptAsync(script);

            if (result.IsSuccess && result.Value!.Success)
            {
                LogOperation("Drivers added successfully");
                await _dialogService.ShowInfoAsync("Drivers added successfully");
            }
            else
            {
                var error = result.IsFailure ? result.Error! : string.Join("; ", result.Value.Errors);
                LogOperation($"Error adding drivers: {error}");
                await _dialogService.ShowErrorAsync($"Failed to add drivers: {error}");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error adding drivers");
            LogOperation($"Exception: {ex.Message}");
            await _dialogService.ShowErrorAsync($"Error adding drivers: {ex.Message}");
        }
        finally
        {
            IsBusy = false;
        }
    }

    /// <summary>
    /// Add packages/updates to the mounted image.
    /// </summary>
    [RelayCommand(CanExecute = nameof(CanUnmountImage))]
    private async Task AddPackagesAsync()
    {
        var packagePath = await _dialogService.ShowFilePickerAsync("*.cab", "*.msu");

        if (string.IsNullOrEmpty(packagePath))
        {
            return;
        }

        IsBusy = true;
        try
        {
            LogOperation($"Adding package {packagePath}");

            var script = $@"
                $mountPath = '{MountPath.Replace("'", "''")}'
                $packagePath = '{packagePath.Replace("'", "''")}'

                Add-WindowsPackage -Path $mountPath -PackagePath $packagePath
            ";

            var result = await _powerShellEngine.ExecuteScriptAsync(script);

            if (result.IsSuccess && result.Value!.Success)
            {
                LogOperation("Package added successfully");
                await _dialogService.ShowInfoAsync("Package added successfully");
            }
            else
            {
                var error = result.IsFailure ? result.Error! : string.Join("; ", result.Value.Errors);
                LogOperation($"Error adding package: {error}");
                await _dialogService.ShowErrorAsync($"Failed to add package: {error}");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error adding package");
            LogOperation($"Exception: {ex.Message}");
            await _dialogService.ShowErrorAsync($"Error adding package: {ex.Message}");
        }
        finally
        {
            IsBusy = false;
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
    /// Log an operation to the operation log.
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
        LogOperation("Image Editor initialized");
    }
}
