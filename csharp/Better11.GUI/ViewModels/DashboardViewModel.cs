using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Better11.Core.Interfaces;
using Better11.Core.Models;
using Microsoft.Extensions.Logging;

namespace Better11.GUI.ViewModels
{
    /// <summary>
    /// Dashboard ViewModel showing system overview.
    /// </summary>
    public partial class DashboardViewModel : BaseViewModel
    {
        private readonly ISysInfoService _sysInfoService;
        private readonly IPerformanceService _performanceService;
        private readonly IPrivacyService _privacyService;
        private readonly ILogger<DashboardViewModel> _logger;

        [ObservableProperty]
        private string _computerName = string.Empty;

        [ObservableProperty]
        private string _windowsEdition = string.Empty;

        [ObservableProperty]
        private string _windowsBuild = string.Empty;

        [ObservableProperty]
        private double _cpuUsage;

        [ObservableProperty]
        private double _memoryUsage;

        [ObservableProperty]
        private double _memoryTotal;

        [ObservableProperty]
        private string _privacyStatus = "Unknown";

        [ObservableProperty]
        private string _performanceStatus = "Unknown";

        public DashboardViewModel(
            ISysInfoService sysInfoService,
            IPerformanceService performanceService,
            IPrivacyService privacyService,
            ILogger<DashboardViewModel> logger)
        {
            _sysInfoService = sysInfoService;
            _performanceService = performanceService;
            _privacyService = privacyService;
            _logger = logger;
        }

        [RelayCommand]
        private async Task LoadAsync()
        {
            try
            {
                IsLoading = true;
                ClearError();

                // Get Windows info
                var windowsInfo = await _sysInfoService.GetWindowsInfoAsync();
                ComputerName = Environment.MachineName;
                WindowsEdition = windowsInfo.Edition;
                WindowsBuild = windowsInfo.Build;

                // Get resource usage
                var usage = await _performanceService.GetResourceUsageAsync();
                CpuUsage = usage.CPUUsagePercent;
                MemoryUsage = usage.MemoryUsedPercent;
                MemoryTotal = usage.MemoryTotalGB;

                // Get privacy status
                var privacyStatus = await _privacyService.GetPrivacyStatusAsync();
                PrivacyStatus = privacyStatus.TelemetryLevel == TelemetryLevel.Security ||
                               privacyStatus.TelemetryLevel == TelemetryLevel.Basic
                    ? "Protected"
                    : "Review Recommended";

                PerformanceStatus = "Optimized";
                SetStatus("Dashboard loaded successfully");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to load dashboard");
                SetError("Failed to load dashboard data");
            }
            finally
            {
                IsLoading = false;
            }
        }

        [RelayCommand]
        private async Task RefreshResourcesAsync()
        {
            try
            {
                var usage = await _performanceService.GetResourceUsageAsync();
                CpuUsage = usage.CPUUsagePercent;
                MemoryUsage = usage.MemoryUsedPercent;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to refresh resources");
            }
        }
    }
}
