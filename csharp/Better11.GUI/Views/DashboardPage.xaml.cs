using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.Extensions.DependencyInjection;
using Better11.GUI.ViewModels;

namespace Better11.GUI.Views
{
    public sealed partial class DashboardPage : Page
    {
        private readonly DashboardViewModel _viewModel;

        public DashboardPage()
        {
            this.InitializeComponent();
            _viewModel = App.Services.GetRequiredService<DashboardViewModel>();
        }

        private async void Page_Loaded(object sender, RoutedEventArgs e)
        {
            await _viewModel.LoadCommand.ExecuteAsync(null);
            UpdateUI();
        }

        private void UpdateUI()
        {
            ComputerNameText.Text = _viewModel.ComputerName;
            WindowsEditionText.Text = _viewModel.WindowsEdition;
            WindowsBuildText.Text = _viewModel.WindowsBuild;
            
            CpuUsageText.Text = $"{_viewModel.CpuUsage:F1}%";
            CpuProgressBar.Value = _viewModel.CpuUsage;
            
            MemoryUsageText.Text = $"{_viewModel.MemoryUsage:F1}% of {_viewModel.MemoryTotal:F1} GB";
            MemoryProgressBar.Value = _viewModel.MemoryUsage;
            
            PrivacyStatusText.Text = _viewModel.PrivacyStatus;
            PerformanceStatusText.Text = _viewModel.PerformanceStatus;
            
            StatusText.Text = _viewModel.StatusMessage;
        }

        private async void RefreshResources_Click(object sender, RoutedEventArgs e)
        {
            await _viewModel.RefreshResourcesCommand.ExecuteAsync(null);
            CpuUsageText.Text = $"{_viewModel.CpuUsage:F1}%";
            CpuProgressBar.Value = _viewModel.CpuUsage;
            MemoryUsageText.Text = $"{_viewModel.MemoryUsage:F1}%";
            MemoryProgressBar.Value = _viewModel.MemoryUsage;
        }
    }
}
