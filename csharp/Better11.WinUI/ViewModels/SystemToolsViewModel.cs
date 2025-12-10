using CommunityToolkit.Mvvm.ComponentModel;
using Microsoft.Extensions.Logging;

namespace Better11.WinUI.ViewModels
{
    /// <summary>
    /// View model for the System Tools page.
    /// </summary>
    public partial class SystemToolsViewModel : ObservableObject
    {
        private readonly ILogger<SystemToolsViewModel> _logger;

        public SystemToolsViewModel(ILogger<SystemToolsViewModel> logger)
        {
            _logger = logger;
        }
    }
}
