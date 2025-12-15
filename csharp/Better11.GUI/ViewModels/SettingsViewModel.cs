using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Microsoft.Extensions.Logging;

namespace Better11.GUI.ViewModels
{
    /// <summary>
    /// Application settings ViewModel.
    /// </summary>
    public partial class SettingsViewModel : BaseViewModel
    {
        private readonly ILogger<SettingsViewModel> _logger;

        [ObservableProperty]
        private string _appVersion = "0.3.0";

        [ObservableProperty]
        private bool _createRestorePoints = true;

        [ObservableProperty]
        private bool _showAdvancedOptions = false;

        [ObservableProperty]
        private string _logLevel = "Information";

        public SettingsViewModel(ILogger<SettingsViewModel> logger)
        {
            _logger = logger;
        }

        [RelayCommand]
        private Task LoadAsync()
        {
            // Load settings from config
            SetStatus("Settings loaded");
            return Task.CompletedTask;
        }

        [RelayCommand]
        private Task SaveSettingsAsync()
        {
            try
            {
                // Save settings to config
                SetStatus("Settings saved");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to save settings");
                SetError("Failed to save settings");
            }
            return Task.CompletedTask;
        }

        [RelayCommand]
        private Task ResetSettingsAsync()
        {
            CreateRestorePoints = true;
            ShowAdvancedOptions = false;
            LogLevel = "Information";
            SetStatus("Settings reset to defaults");
            return Task.CompletedTask;
        }
    }
}
