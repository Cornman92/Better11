using Better11.App.Services;
using Better11.Core.Interfaces;
using CommunityToolkit.Mvvm.Input;
using Microsoft.Extensions.Logging;
using System.Runtime.InteropServices;

namespace Better11.App.ViewModels;

/// <summary>
/// ViewModel for the Dashboard view showing system information and quick actions.
/// </summary>
public partial class DashboardViewModel : ViewModelBase
{
    private readonly ILogger<DashboardViewModel> _logger;
    private readonly INavigationService _navigationService;
    private readonly ISecurityService _securityService;
    private readonly IPowerShellEngine _powerShellEngine;

    private string _windowsVersion = "Loading...";
    private string _systemUptime = "Loading...";
    private string _cpuUsage = "0%";
    private string _memoryUsage = "0%";
    private string _diskUsage = "0%";
    private bool _isAdministrator;

    /// <summary>
    /// Initializes a new instance of the <see cref="DashboardViewModel"/> class.
    /// </summary>
    public DashboardViewModel(
        ILogger<DashboardViewModel> logger,
        INavigationService navigationService,
        ISecurityService securityService,
        IPowerShellEngine powerShellEngine)
    {
        _logger = logger;
        _navigationService = navigationService;
        _securityService = securityService;
        _powerShellEngine = powerShellEngine;

        Title = "Dashboard";
    }

    /// <summary>
    /// Gets or sets the Windows version information.
    /// </summary>
    public string WindowsVersion
    {
        get => _windowsVersion;
        set => SetProperty(ref _windowsVersion, value);
    }

    /// <summary>
    /// Gets or sets the system uptime.
    /// </summary>
    public string SystemUptime
    {
        get => _systemUptime;
        set => SetProperty(ref _systemUptime, value);
    }

    /// <summary>
    /// Gets or sets the CPU usage percentage.
    /// </summary>
    public string CpuUsage
    {
        get => _cpuUsage;
        set => SetProperty(ref _cpuUsage, value);
    }

    /// <summary>
    /// Gets or sets the memory usage percentage.
    /// </summary>
    public string MemoryUsage
    {
        get => _memoryUsage;
        set => SetProperty(ref _memoryUsage, value);
    }

    /// <summary>
    /// Gets or sets the disk usage percentage.
    /// </summary>
    public string DiskUsage
    {
        get => _diskUsage;
        set => SetProperty(ref _diskUsage, value);
    }

    /// <summary>
    /// Gets or sets a value indicating whether the app is running as administrator.
    /// </summary>
    public bool IsAdministrator
    {
        get => _isAdministrator;
        set => SetProperty(ref _isAdministrator, value);
    }

    /// <summary>
    /// Navigates to the Image Editor.
    /// </summary>
    [RelayCommand]
    private void NavigateToImageEditor()
    {
        _logger.LogInformation("Navigating to Image Editor");
        _navigationService.NavigateTo("ImageEditor");
    }

    /// <summary>
    /// Navigates to the App Manager.
    /// </summary>
    [RelayCommand]
    private void NavigateToAppManager()
    {
        _logger.LogInformation("Navigating to App Manager");
        _navigationService.NavigateTo("AppManager");
    }

    /// <summary>
    /// Navigates to Settings.
    /// </summary>
    [RelayCommand]
    private void NavigateToSettings()
    {
        _logger.LogInformation("Navigating to Settings");
        _navigationService.NavigateTo("Settings");
    }

    /// <summary>
    /// Refreshes the system information.
    /// </summary>
    [RelayCommand]
    private async Task RefreshSystemInfoAsync()
    {
        IsBusy = true;
        try
        {
            _logger.LogInformation("Refreshing system information");

            // Check administrator status
            IsAdministrator = _securityService.IsAdministrator();

            // Get Windows version
            await LoadWindowsVersionAsync();

            // Get system uptime
            await LoadSystemUptimeAsync();

            // Get system metrics (simplified for now)
            await LoadSystemMetricsAsync();

            _logger.LogInformation("System information refreshed successfully");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error refreshing system information");
        }
        finally
        {
            IsBusy = false;
        }
    }

    /// <inheritdoc/>
    public override async Task InitializeAsync()
    {
        await RefreshSystemInfoAsync();
    }

    private async Task LoadWindowsVersionAsync()
    {
        try
        {
            var script = @"
                $os = Get-CimInstance Win32_OperatingSystem
                ""$($os.Caption) (Build $($os.BuildNumber))""
            ";

            var result = await _powerShellEngine.ExecuteScriptAsync(script);

            if (result.IsSuccess && result.Value!.Success && result.Value.Output.Count > 0)
            {
                WindowsVersion = result.Value.Output[0]?.ToString() ?? "Unknown";
            }
            else
            {
                WindowsVersion = $"Windows {Environment.OSVersion.Version}";
            }
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Error loading Windows version");
            WindowsVersion = $"Windows {Environment.OSVersion.Version}";
        }
    }

    private async Task LoadSystemUptimeAsync()
    {
        try
        {
            var uptime = TimeSpan.FromMilliseconds(Environment.TickCount64);
            SystemUptime = $"{uptime.Days}d {uptime.Hours}h {uptime.Minutes}m";

            await Task.CompletedTask;
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Error loading system uptime");
            SystemUptime = "Unknown";
        }
    }

    private async Task LoadSystemMetricsAsync()
    {
        try
        {
            // Get memory info
            var memInfo = new MEMORYSTATUSEX();
            if (GlobalMemoryStatusEx(memInfo))
            {
                var usedMemory = memInfo.ullTotalPhys - memInfo.ullAvailPhys;
                var memoryPercent = (double)usedMemory / memInfo.ullTotalPhys * 100;
                MemoryUsage = $"{memoryPercent:F1}%";
            }

            // Simplified CPU and disk metrics
            CpuUsage = "Calculating...";
            DiskUsage = "Calculating...";

            await Task.CompletedTask;
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Error loading system metrics");
        }
    }

    [DllImport("kernel32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static extern bool GlobalMemoryStatusEx([In, Out] MEMORYSTATUSEX lpBuffer);

    [StructLayout(LayoutKind.Sequential)]
    private class MEMORYSTATUSEX
    {
        public uint dwLength = (uint)Marshal.SizeOf(typeof(MEMORYSTATUSEX));
        public uint dwMemoryLoad;
        public ulong ullTotalPhys;
        public ulong ullAvailPhys;
        public ulong ullTotalPageFile;
        public ulong ullAvailPageFile;
        public ulong ullTotalVirtual;
        public ulong ullAvailVirtual;
        public ulong ullAvailExtendedVirtual;
    }
}
