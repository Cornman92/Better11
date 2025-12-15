using Better11.Core.Interfaces;
using Better11.Core.Models;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Microsoft.Extensions.Logging;
using System.Collections.ObjectModel;

namespace Better11.App.ViewModels;

/// <summary>
/// ViewModel for the Application Manager feature.
/// </summary>
public partial class AppManagerViewModel : ViewModelBase
{
    private readonly ILogger<AppManagerViewModel> _logger;
    private readonly IProcessService _processService;
    private readonly IPowerShellEngine _powerShellEngine;
    private readonly IDialogService _dialogService;

    private string _searchQuery = string.Empty;
    private string _selectedPackageManager = "winget";
    private ObservableCollection<AppPackage> _searchResults = new();
    private ObservableCollection<AppPackage> _installedApps = new();
    private AppPackage? _selectedPackage;
    private string _operationLog = string.Empty;
    private bool _isWingetAvailable;
    private bool _isChocoAvailable;

    /// <summary>
    /// Initializes a new instance of the <see cref="AppManagerViewModel"/> class.
    /// </summary>
    public AppManagerViewModel(
        ILogger<AppManagerViewModel> logger,
        IProcessService processService,
        IPowerShellEngine powerShellEngine,
        IDialogService dialogService)
    {
        _logger = logger;
        _processService = processService;
        _powerShellEngine = powerShellEngine;
        _dialogService = dialogService;

        Title = "App Manager";
    }

    /// <summary>
    /// Gets or sets the search query.
    /// </summary>
    public string SearchQuery
    {
        get => _searchQuery;
        set => SetProperty(ref _searchQuery, value);
    }

    /// <summary>
    /// Gets or sets the selected package manager.
    /// </summary>
    public string SelectedPackageManager
    {
        get => _selectedPackageManager;
        set => SetProperty(ref _selectedPackageManager, value);
    }

    /// <summary>
    /// Gets or sets the search results.
    /// </summary>
    public ObservableCollection<AppPackage> SearchResults
    {
        get => _searchResults;
        set => SetProperty(ref _searchResults, value);
    }

    /// <summary>
    /// Gets or sets the installed applications.
    /// </summary>
    public ObservableCollection<AppPackage> InstalledApps
    {
        get => _installedApps;
        set => SetProperty(ref _installedApps, value);
    }

    /// <summary>
    /// Gets or sets the selected package.
    /// </summary>
    public AppPackage? SelectedPackage
    {
        get => _selectedPackage;
        set
        {
            if (SetProperty(ref _selectedPackage, value))
            {
                OnPropertyChanged(nameof(CanInstallPackage));
                OnPropertyChanged(nameof(CanUninstallPackage));
            }
        }
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
    /// Gets or sets whether winget is available.
    /// </summary>
    public bool IsWingetAvailable
    {
        get => _isWingetAvailable;
        set => SetProperty(ref _isWingetAvailable, value);
    }

    /// <summary>
    /// Gets or sets whether Chocolatey is available.
    /// </summary>
    public bool IsChocoAvailable
    {
        get => _isChocoAvailable;
        set => SetProperty(ref _isChocoAvailable, value);
    }

    /// <summary>
    /// Gets whether a package can be installed.
    /// </summary>
    public bool CanInstallPackage => SelectedPackage != null && !SelectedPackage.IsInstalled && !IsBusy;

    /// <summary>
    /// Gets whether a package can be uninstalled.
    /// </summary>
    public bool CanUninstallPackage => SelectedPackage != null && SelectedPackage.IsInstalled && !IsBusy;

    /// <summary>
    /// Search for applications using the selected package manager.
    /// </summary>
    [RelayCommand]
    private async Task SearchAppsAsync()
    {
        if (string.IsNullOrWhiteSpace(SearchQuery))
        {
            await _dialogService.ShowWarningAsync("Please enter a search query.");
            return;
        }

        IsBusy = true;
        try
        {
            LogOperation($"Searching for '{SearchQuery}' using {SelectedPackageManager}");

            SearchResults.Clear();

            if (SelectedPackageManager == "winget")
            {
                await SearchWithWingetAsync();
            }
            else if (SelectedPackageManager == "choco")
            {
                await SearchWithChocoAsync();
            }

            LogOperation($"Found {SearchResults.Count} results");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error searching for applications");
            LogOperation($"Error: {ex.Message}");
            await _dialogService.ShowErrorAsync($"Error searching for applications: {ex.Message}");
        }
        finally
        {
            IsBusy = false;
        }
    }

    /// <summary>
    /// Install the selected application.
    /// </summary>
    [RelayCommand(CanExecute = nameof(CanInstallPackage))]
    private async Task InstallPackageAsync()
    {
        if (SelectedPackage == null)
        {
            return;
        }

        var confirmed = await _dialogService.ShowConfirmationAsync(
            $"Do you want to install {SelectedPackage.Name}?",
            "Install Application");

        if (!confirmed)
        {
            return;
        }

        IsBusy = true;
        try
        {
            LogOperation($"Installing {SelectedPackage.Name} ({SelectedPackage.Id})");

            Result<ProcessResult> result;

            if (SelectedPackageManager == "winget")
            {
                result = await _processService.ExecuteAsync(
                    "winget",
                    $"install --id {SelectedPackage.Id} --accept-source-agreements --accept-package-agreements");
            }
            else // choco
            {
                result = await _processService.ExecuteAsync(
                    "choco",
                    $"install {SelectedPackage.Id} -y");
            }

            if (result.IsSuccess && result.Value!.Success)
            {
                LogOperation($"Successfully installed {SelectedPackage.Name}");
                await _dialogService.ShowInfoAsync($"{SelectedPackage.Name} installed successfully");

                // Refresh installed apps
                await LoadInstalledAppsAsync();
            }
            else
            {
                var error = result.IsFailure ? result.Error! : result.Value.StandardError;
                LogOperation($"Installation failed: {error}");
                await _dialogService.ShowErrorAsync($"Failed to install {SelectedPackage.Name}: {error}");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error installing package");
            LogOperation($"Exception: {ex.Message}");
            await _dialogService.ShowErrorAsync($"Error installing package: {ex.Message}");
        }
        finally
        {
            IsBusy = false;
        }
    }

    /// <summary>
    /// Uninstall the selected application.
    /// </summary>
    [RelayCommand(CanExecute = nameof(CanUninstallPackage))]
    private async Task UninstallPackageAsync()
    {
        if (SelectedPackage == null)
        {
            return;
        }

        var confirmed = await _dialogService.ShowConfirmationAsync(
            $"Do you want to uninstall {SelectedPackage.Name}?",
            "Uninstall Application");

        if (!confirmed)
        {
            return;
        }

        IsBusy = true;
        try
        {
            LogOperation($"Uninstalling {SelectedPackage.Name} ({SelectedPackage.Id})");

            Result<ProcessResult> result;

            if (SelectedPackageManager == "winget")
            {
                result = await _processService.ExecuteAsync(
                    "winget",
                    $"uninstall --id {SelectedPackage.Id}");
            }
            else // choco
            {
                result = await _processService.ExecuteAsync(
                    "choco",
                    $"uninstall {SelectedPackage.Id} -y");
            }

            if (result.IsSuccess && result.Value!.Success)
            {
                LogOperation($"Successfully uninstalled {SelectedPackage.Name}");
                await _dialogService.ShowInfoAsync($"{SelectedPackage.Name} uninstalled successfully");

                // Refresh installed apps
                await LoadInstalledAppsAsync();
            }
            else
            {
                var error = result.IsFailure ? result.Error! : result.Value.StandardError;
                LogOperation($"Uninstallation failed: {error}");
                await _dialogService.ShowErrorAsync($"Failed to uninstall {SelectedPackage.Name}: {error}");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error uninstalling package");
            LogOperation($"Exception: {ex.Message}");
            await _dialogService.ShowErrorAsync($"Error uninstalling package: {ex.Message}");
        }
        finally
        {
            IsBusy = false;
        }
    }

    /// <summary>
    /// Load installed applications.
    /// </summary>
    [RelayCommand]
    private async Task LoadInstalledAppsAsync()
    {
        IsBusy = true;
        try
        {
            LogOperation("Loading installed applications");

            InstalledApps.Clear();

            if (SelectedPackageManager == "winget")
            {
                var script = @"
                    winget list | Select-Object -Skip 2 | ForEach-Object {
                        $line = $_.Trim()
                        if ($line -match '^(.+?)\s{2,}(.+?)\s{2,}(.+?)$') {
                            [PSCustomObject]@{
                                Name = $matches[1].Trim()
                                Id = $matches[2].Trim()
                                Version = $matches[3].Trim()
                            }
                        }
                    }
                ";

                var result = await _powerShellEngine.ExecuteScriptAsync(script);

                if (result.IsSuccess && result.Value!.Success)
                {
                    foreach (var item in result.Value.Output)
                    {
                        if (item is System.Management.Automation.PSObject psObj)
                        {
                            var name = psObj.Properties["Name"]?.Value?.ToString() ?? string.Empty;
                            var id = psObj.Properties["Id"]?.Value?.ToString() ?? string.Empty;
                            var version = psObj.Properties["Version"]?.Value?.ToString() ?? string.Empty;

                            if (!string.IsNullOrEmpty(name) && !string.IsNullOrEmpty(id))
                            {
                                InstalledApps.Add(new AppPackage
                                {
                                    Name = name,
                                    Id = id,
                                    Version = version,
                                    IsInstalled = true
                                });
                            }
                        }
                    }
                }
            }

            LogOperation($"Loaded {InstalledApps.Count} installed applications");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error loading installed applications");
            LogOperation($"Error: {ex.Message}");
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

    /// <inheritdoc/>
    public override async Task InitializeAsync()
    {
        await base.InitializeAsync();

        LogOperation("App Manager initialized");

        // Check for available package managers
        await CheckPackageManagersAsync();

        // Load installed apps
        await LoadInstalledAppsAsync();
    }

    /// <summary>
    /// Search for applications using winget.
    /// </summary>
    private async Task SearchWithWingetAsync()
    {
        var script = $@"
            $query = '{SearchQuery.Replace("'", "''")}'
            winget search $query | Select-Object -Skip 2 | ForEach-Object {{
                $line = $_.Trim()
                if ($line -match '^(.+?)\s{{2,}}(.+?)\s{{2,}}(.+?)$') {{
                    [PSCustomObject]@{{
                        Name = $matches[1].Trim()
                        Id = $matches[2].Trim()
                        Version = $matches[3].Trim()
                    }}
                }}
            }} | Select-Object -First 20
        ";

        var result = await _powerShellEngine.ExecuteScriptAsync(script);

        if (result.IsSuccess && result.Value!.Success)
        {
            foreach (var item in result.Value.Output)
            {
                if (item is System.Management.Automation.PSObject psObj)
                {
                    var name = psObj.Properties["Name"]?.Value?.ToString() ?? string.Empty;
                    var id = psObj.Properties["Id"]?.Value?.ToString() ?? string.Empty;
                    var version = psObj.Properties["Version"]?.Value?.ToString() ?? string.Empty;

                    if (!string.IsNullOrEmpty(name) && !string.IsNullOrEmpty(id))
                    {
                        SearchResults.Add(new AppPackage
                        {
                            Name = name,
                            Id = id,
                            Version = version,
                            Source = "winget"
                        });
                    }
                }
            }
        }
        else
        {
            var error = result.IsFailure ? result.Error! : string.Join("; ", result.Value.Errors);
            LogOperation($"Winget search failed: {error}");
        }
    }

    /// <summary>
    /// Search for applications using Chocolatey.
    /// </summary>
    private async Task SearchWithChocoAsync()
    {
        var result = await _processService.ExecuteAsync("choco", $"search {SearchQuery} --limit-output");

        if (result.IsSuccess && result.Value!.Success)
        {
            var lines = result.Value.StandardOutput.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries);

            foreach (var line in lines.Take(20))
            {
                var parts = line.Split('|');
                if (parts.Length >= 2)
                {
                    SearchResults.Add(new AppPackage
                    {
                        Name = parts[0],
                        Id = parts[0],
                        Version = parts[1],
                        Source = "chocolatey"
                    });
                }
            }
        }
        else
        {
            var error = result.IsFailure ? result.Error! : result.Value.StandardError;
            LogOperation($"Chocolatey search failed: {error}");
        }
    }

    /// <summary>
    /// Check which package managers are available.
    /// </summary>
    private async Task CheckPackageManagersAsync()
    {
        // Check winget
        var wingetResult = await _processService.ExecuteAsync("winget", "--version");
        IsWingetAvailable = wingetResult.IsSuccess && wingetResult.Value!.Success;

        LogOperation($"winget: {(IsWingetAvailable ? "Available" : "Not available")}");

        // Check Chocolatey
        var chocoResult = await _processService.ExecuteAsync("choco", "--version");
        IsChocoAvailable = chocoResult.IsSuccess && chocoResult.Value!.Success;

        LogOperation($"Chocolatey: {(IsChocoAvailable ? "Available" : "Not available")}");

        // Set default package manager to the first available one
        if (!IsWingetAvailable && IsChocoAvailable)
        {
            SelectedPackageManager = "choco";
        }
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
}

/// <summary>
/// Represents an application package.
/// </summary>
public class AppPackage
{
    /// <summary>
    /// Gets or sets the package name.
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// Gets or sets the package ID.
    /// </summary>
    public string Id { get; set; } = string.Empty;

    /// <summary>
    /// Gets or sets the package version.
    /// </summary>
    public string Version { get; set; } = string.Empty;

    /// <summary>
    /// Gets or sets the package source.
    /// </summary>
    public string Source { get; set; } = string.Empty;

    /// <summary>
    /// Gets or sets whether the package is installed.
    /// </summary>
    public bool IsInstalled { get; set; }

    /// <summary>
    /// Gets or sets the package description.
    /// </summary>
    public string Description { get; set; } = string.Empty;
}
