using CommunityToolkit.Mvvm.ComponentModel;
using Microsoft.Extensions.Logging;

namespace Better11.WinUI.ViewModels
{
    /// <summary>
    /// View model for the Settings page.
    /// </summary>
    public partial class SettingsViewModel : ObservableObject
    {
        private readonly ILogger<SettingsViewModel> _logger;

        [ObservableProperty]
        private bool _autoCheckUpdates = true;

        [ObservableProperty]
        private bool _verifySignatures = true;

        [ObservableProperty]
        private bool _alwaysCreateRestorePoints = true;

        [ObservableProperty]
        private string _selectedTheme = "System Default";

        public SettingsViewModel(ILogger<SettingsViewModel> logger)
        {
            _logger = logger;
        }
    }
}
