using CommunityToolkit.Mvvm.ComponentModel;
using Microsoft.Extensions.Logging;

namespace Better11.WinUI.ViewModels
{
    /// <summary>
    /// Main view model for the application.
    /// </summary>
    public partial class MainViewModel : ObservableObject
    {
        private readonly ILogger<MainViewModel> _logger;

        [ObservableProperty]
        private string _title = "Better11";

        [ObservableProperty]
        private string _statusMessage = "Ready";

        public MainViewModel(ILogger<MainViewModel> logger)
        {
            _logger = logger;
            _logger.LogInformation("MainViewModel initialized");
        }

        public void UpdateStatus(string message)
        {
            StatusMessage = message;
            _logger.LogInformation("Status updated: {Message}", message);
        }
    }
}
