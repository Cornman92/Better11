using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Better11.Core.Interfaces;
using Microsoft.Extensions.Logging;

namespace Better11.GUI.ViewModels
{
    /// <summary>
    /// Main application ViewModel.
    /// </summary>
    public partial class MainViewModel : BaseViewModel
    {
        private readonly ISysInfoService _sysInfoService;
        private readonly ILogger<MainViewModel> _logger;

        [ObservableProperty]
        private string _appVersion = "0.3.0";

        [ObservableProperty]
        private string _computerName = string.Empty;

        [ObservableProperty]
        private string _windowsVersion = string.Empty;

        public MainViewModel(
            ISysInfoService sysInfoService,
            ILogger<MainViewModel> logger)
        {
            _sysInfoService = sysInfoService;
            _logger = logger;
        }

        [RelayCommand]
        private async Task LoadAsync()
        {
            try
            {
                IsLoading = true;
                var windowsInfo = await _sysInfoService.GetWindowsInfoAsync();
                ComputerName = Environment.MachineName;
                WindowsVersion = windowsInfo.Edition;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to load main data");
                SetError("Failed to load system information");
            }
            finally
            {
                IsLoading = false;
            }
        }
    }
}
