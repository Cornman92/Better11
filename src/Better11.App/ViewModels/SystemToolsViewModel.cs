using Better11.Core.Interfaces;
using Better11.Core.Models;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Microsoft.Extensions.Logging;
using System.Collections.ObjectModel;

namespace Better11.App.ViewModels;

/// <summary>
/// ViewModel for system tools feature.
/// </summary>
public partial class SystemToolsViewModel : ViewModelBase
{
    private readonly ILogger<SystemToolsViewModel> _logger;
    private readonly IPowerShellEngine _powerShellEngine;
    private readonly IProcessService _processService;
    private readonly ISecurityService _securityService;
    private readonly IDialogService _dialogService;

    private string _selectedTab = "Services";
    private ObservableCollection<WindowsServiceItem> _services = new();
    private ObservableCollection<ScheduledTaskItem> _tasks = new();
    private WindowsServiceItem? _selectedService;
    private ScheduledTaskItem? _selectedTask;
    private string _operationLog = string.Empty;
    private string _registryPath = @"HKEY_LOCAL_MACHINE\SOFTWARE";
    private string _registryValue = string.Empty;

    /// <summary>
    /// Initializes a new instance of the <see cref="SystemToolsViewModel"/> class.
    /// </summary>
    public SystemToolsViewModel(
        ILogger<SystemToolsViewModel> logger,
        IPowerShellEngine powerShellEngine,
        IProcessService processService,
        ISecurityService securityService,
        IDialogService dialogService)
    {
        _logger = logger;
        _powerShellEngine = powerShellEngine;
        _processService = processService;
        _securityService = securityService;
        _dialogService = dialogService;

        Title = "System Tools";
    }

    /// <summary>
    /// Gets or sets the selected tab.
    /// </summary>
    public string SelectedTab
    {
        get => _selectedTab;
        set => SetProperty(ref _selectedTab, value);
    }

    /// <summary>
    /// Gets or sets the services collection.
    /// </summary>
    public ObservableCollection<WindowsServiceItem> Services
    {
        get => _services;
        set => SetProperty(ref _services, value);
    }

    /// <summary>
    /// Gets or sets the tasks collection.
    /// </summary>
    public ObservableCollection<ScheduledTaskItem> Tasks
    {
        get => _tasks;
        set => SetProperty(ref _tasks, value);
    }

    /// <summary>
    /// Gets or sets the selected service.
    /// </summary>
    public WindowsServiceItem? SelectedService
    {
        get => _selectedService;
        set
        {
            if (SetProperty(ref _selectedService, value))
            {
                OnPropertyChanged(nameof(CanStartService));
                OnPropertyChanged(nameof(CanStopService));
                OnPropertyChanged(nameof(CanRestartService));
            }
        }
    }

    /// <summary>
    /// Gets or sets the selected task.
    /// </summary>
    public ScheduledTaskItem? SelectedTask
    {
        get => _selectedTask;
        set
        {
            if (SetProperty(ref _selectedTask, value))
            {
                OnPropertyChanged(nameof(CanEnableTask));
                OnPropertyChanged(nameof(CanDisableTask));
                OnPropertyChanged(nameof(CanRunTask));
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
    /// Gets or sets the registry path.
    /// </summary>
    public string RegistryPath
    {
        get => _registryPath;
        set => SetProperty(ref _registryPath, value);
    }

    /// <summary>
    /// Gets or sets the registry value.
    /// </summary>
    public string RegistryValue
    {
        get => _registryValue;
        set => SetProperty(ref _registryValue, value);
    }

    /// <summary>
    /// Gets whether a service can be started.
    /// </summary>
    public bool CanStartService => SelectedService != null && SelectedService.Status == "Stopped" && !IsBusy;

    /// <summary>
    /// Gets whether a service can be stopped.
    /// </summary>
    public bool CanStopService => SelectedService != null && SelectedService.Status == "Running" && !IsBusy;

    /// <summary>
    /// Gets whether a service can be restarted.
    /// </summary>
    public bool CanRestartService => SelectedService != null && SelectedService.Status == "Running" && !IsBusy;

    /// <summary>
    /// Gets whether a task can be enabled.
    /// </summary>
    public bool CanEnableTask => SelectedTask != null && SelectedTask.State != "Ready" && !IsBusy;

    /// <summary>
    /// Gets whether a task can be disabled.
    /// </summary>
    public bool CanDisableTask => SelectedTask != null && SelectedTask.State == "Ready" && !IsBusy;

    /// <summary>
    /// Gets whether a task can be run.
    /// </summary>
    public bool CanRunTask => SelectedTask != null && !IsBusy;

    /// <summary>
    /// Load Windows services.
    /// </summary>
    [RelayCommand]
    private async Task LoadServicesAsync()
    {
        IsBusy = true;
        try
        {
            LogOperation("Loading Windows services");

            Services.Clear();

            var script = @"
                Get-Service | Select-Object Name, DisplayName, Status, StartType | ForEach-Object {
                    [PSCustomObject]@{
                        Name = $_.Name
                        DisplayName = $_.DisplayName
                        Status = $_.Status.ToString()
                        StartType = $_.StartType.ToString()
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
                        Services.Add(new WindowsServiceItem
                        {
                            Name = psObj.Properties["Name"]?.Value?.ToString() ?? string.Empty,
                            DisplayName = psObj.Properties["DisplayName"]?.Value?.ToString() ?? string.Empty,
                            Status = psObj.Properties["Status"]?.Value?.ToString() ?? string.Empty,
                            StartType = psObj.Properties["StartType"]?.Value?.ToString() ?? string.Empty
                        });
                    }
                }

                LogOperation($"Loaded {Services.Count} services");
            }
            else
            {
                var error = result.IsFailure ? result.Error! : string.Join("; ", result.Value.Errors);
                LogOperation($"Error loading services: {error}");
                await _dialogService.ShowErrorAsync($"Failed to load services: {error}");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error loading services");
            LogOperation($"Exception: {ex.Message}");
            await _dialogService.ShowErrorAsync($"Error loading services: {ex.Message}");
        }
        finally
        {
            IsBusy = false;
        }
    }

    /// <summary>
    /// Start a Windows service.
    /// </summary>
    [RelayCommand(CanExecute = nameof(CanStartService))]
    private async Task StartServiceAsync()
    {
        if (SelectedService == null) return;

        if (!_securityService.IsAdministrator())
        {
            await _dialogService.ShowWarningAsync("Administrator privileges required to start services.");
            return;
        }

        IsBusy = true;
        try
        {
            LogOperation($"Starting service: {SelectedService.Name}");

            var script = $"Start-Service -Name '{SelectedService.Name.Replace("'", "''")}'";
            var result = await _powerShellEngine.ExecuteScriptAsync(script);

            if (result.IsSuccess && result.Value!.Success)
            {
                LogOperation($"✓ Service started: {SelectedService.Name}");
                await _dialogService.ShowInfoAsync($"Service '{SelectedService.DisplayName}' started successfully.");
                await LoadServicesAsync();
            }
            else
            {
                var error = result.IsFailure ? result.Error! : string.Join("; ", result.Value.Errors);
                LogOperation($"✗ Failed to start service: {error}");
                await _dialogService.ShowErrorAsync($"Failed to start service: {error}");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error starting service");
            LogOperation($"Exception: {ex.Message}");
            await _dialogService.ShowErrorAsync($"Error starting service: {ex.Message}");
        }
        finally
        {
            IsBusy = false;
        }
    }

    /// <summary>
    /// Stop a Windows service.
    /// </summary>
    [RelayCommand(CanExecute = nameof(CanStopService))]
    private async Task StopServiceAsync()
    {
        if (SelectedService == null) return;

        if (!_securityService.IsAdministrator())
        {
            await _dialogService.ShowWarningAsync("Administrator privileges required to stop services.");
            return;
        }

        var confirmed = await _dialogService.ShowConfirmationAsync(
            $"Stop service '{SelectedService.DisplayName}'?",
            "Confirm Stop");

        if (!confirmed) return;

        IsBusy = true;
        try
        {
            LogOperation($"Stopping service: {SelectedService.Name}");

            var script = $"Stop-Service -Name '{SelectedService.Name.Replace("'", "''")}'";
            var result = await _powerShellEngine.ExecuteScriptAsync(script);

            if (result.IsSuccess && result.Value!.Success)
            {
                LogOperation($"✓ Service stopped: {SelectedService.Name}");
                await _dialogService.ShowInfoAsync($"Service '{SelectedService.DisplayName}' stopped successfully.");
                await LoadServicesAsync();
            }
            else
            {
                var error = result.IsFailure ? result.Error! : string.Join("; ", result.Value.Errors);
                LogOperation($"✗ Failed to stop service: {error}");
                await _dialogService.ShowErrorAsync($"Failed to stop service: {error}");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error stopping service");
            LogOperation($"Exception: {ex.Message}");
            await _dialogService.ShowErrorAsync($"Error stopping service: {ex.Message}");
        }
        finally
        {
            IsBusy = false;
        }
    }

    /// <summary>
    /// Restart a Windows service.
    /// </summary>
    [RelayCommand(CanExecute = nameof(CanRestartService))]
    private async Task RestartServiceAsync()
    {
        if (SelectedService == null) return;

        if (!_securityService.IsAdministrator())
        {
            await _dialogService.ShowWarningAsync("Administrator privileges required to restart services.");
            return;
        }

        var confirmed = await _dialogService.ShowConfirmationAsync(
            $"Restart service '{SelectedService.DisplayName}'?",
            "Confirm Restart");

        if (!confirmed) return;

        IsBusy = true;
        try
        {
            LogOperation($"Restarting service: {SelectedService.Name}");

            var script = $"Restart-Service -Name '{SelectedService.Name.Replace("'", "''")}'";
            var result = await _powerShellEngine.ExecuteScriptAsync(script);

            if (result.IsSuccess && result.Value!.Success)
            {
                LogOperation($"✓ Service restarted: {SelectedService.Name}");
                await _dialogService.ShowInfoAsync($"Service '{SelectedService.DisplayName}' restarted successfully.");
                await LoadServicesAsync();
            }
            else
            {
                var error = result.IsFailure ? result.Error! : string.Join("; ", result.Value.Errors);
                LogOperation($"✗ Failed to restart service: {error}");
                await _dialogService.ShowErrorAsync($"Failed to restart service: {error}");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error restarting service");
            LogOperation($"Exception: {ex.Message}");
            await _dialogService.ShowErrorAsync($"Error restarting service: {ex.Message}");
        }
        finally
        {
            IsBusy = false;
        }
    }

    /// <summary>
    /// Load scheduled tasks.
    /// </summary>
    [RelayCommand]
    private async Task LoadTasksAsync()
    {
        IsBusy = true;
        try
        {
            LogOperation("Loading scheduled tasks");

            Tasks.Clear();

            var script = @"
                Get-ScheduledTask | Select-Object TaskName, TaskPath, State | ForEach-Object {
                    [PSCustomObject]@{
                        TaskName = $_.TaskName
                        TaskPath = $_.TaskPath
                        State = $_.State.ToString()
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
                        Tasks.Add(new ScheduledTaskItem
                        {
                            TaskName = psObj.Properties["TaskName"]?.Value?.ToString() ?? string.Empty,
                            TaskPath = psObj.Properties["TaskPath"]?.Value?.ToString() ?? string.Empty,
                            State = psObj.Properties["State"]?.Value?.ToString() ?? string.Empty
                        });
                    }
                }

                LogOperation($"Loaded {Tasks.Count} tasks");
            }
            else
            {
                var error = result.IsFailure ? result.Error! : string.Join("; ", result.Value.Errors);
                LogOperation($"Error loading tasks: {error}");
                await _dialogService.ShowErrorAsync($"Failed to load tasks: {error}");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error loading tasks");
            LogOperation($"Exception: {ex.Message}");
            await _dialogService.ShowErrorAsync($"Error loading tasks: {ex.Message}");
        }
        finally
        {
            IsBusy = false;
        }
    }

    /// <summary>
    /// Read a registry value.
    /// </summary>
    [RelayCommand]
    private async Task ReadRegistryAsync()
    {
        if (string.IsNullOrWhiteSpace(RegistryPath))
        {
            await _dialogService.ShowWarningAsync("Please enter a registry path.");
            return;
        }

        IsBusy = true;
        try
        {
            LogOperation($"Reading registry: {RegistryPath}");

            var script = $@"
                $path = '{RegistryPath.Replace("'", "''")}'
                Get-ItemProperty -Path ""Registry::$path"" -ErrorAction SilentlyContinue |
                    Format-List | Out-String
            ";

            var result = await _powerShellEngine.ExecuteScriptAsync(script);

            if (result.IsSuccess && result.Value!.Success && result.Value.Output.Count > 0)
            {
                RegistryValue = result.Value.Output[0]?.ToString() ?? "No data";
                LogOperation($"Registry value read successfully");
            }
            else
            {
                RegistryValue = "Registry key not found or access denied";
                LogOperation($"Failed to read registry key");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error reading registry");
            RegistryValue = $"Error: {ex.Message}";
            LogOperation($"Exception: {ex.Message}");
        }
        finally
        {
            IsBusy = false;
        }
    }

    /// <summary>
    /// Open Registry Editor.
    /// </summary>
    [RelayCommand]
    private async Task OpenRegistryEditorAsync()
    {
        try
        {
            var result = _processService.StartProcess("regedit.exe", string.Empty);
            if (result.IsSuccess)
            {
                LogOperation("Opened Registry Editor");
            }
            else
            {
                await _dialogService.ShowErrorAsync($"Failed to open Registry Editor: {result.Error}");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error opening Registry Editor");
            await _dialogService.ShowErrorAsync($"Error opening Registry Editor: {ex.Message}");
        }
    }

    /// <summary>
    /// Open Event Viewer.
    /// </summary>
    [RelayCommand]
    private async Task OpenEventViewerAsync()
    {
        try
        {
            var result = _processService.StartProcess("eventvwr.msc", string.Empty);
            if (result.IsSuccess)
            {
                LogOperation("Opened Event Viewer");
            }
            else
            {
                await _dialogService.ShowErrorAsync($"Failed to open Event Viewer: {result.Error}");
            }
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error opening Event Viewer");
            await _dialogService.ShowErrorAsync($"Error opening Event Viewer: {ex.Message}");
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
        LogOperation("System Tools initialized");

        // Load services by default
        await LoadServicesAsync();
    }
}

/// <summary>
/// Represents a Windows service item.
/// </summary>
public class WindowsServiceItem
{
    /// <summary>
    /// Gets or sets the service name.
    /// </summary>
    public string Name { get; set; } = string.Empty;

    /// <summary>
    /// Gets or sets the service display name.
    /// </summary>
    public string DisplayName { get; set; } = string.Empty;

    /// <summary>
    /// Gets or sets the service status.
    /// </summary>
    public string Status { get; set; } = string.Empty;

    /// <summary>
    /// Gets or sets the service start type.
    /// </summary>
    public string StartType { get; set; } = string.Empty;
}

/// <summary>
/// Represents a scheduled task item.
/// </summary>
public class ScheduledTaskItem
{
    /// <summary>
    /// Gets or sets the task name.
    /// </summary>
    public string TaskName { get; set; } = string.Empty;

    /// <summary>
    /// Gets or sets the task path.
    /// </summary>
    public string TaskPath { get; set; } = string.Empty;

    /// <summary>
    /// Gets or sets the task state.
    /// </summary>
    public string State { get; set; } = string.Empty;
}
