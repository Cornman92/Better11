using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.Extensions.DependencyInjection;
using Better11.GUI.ViewModels;
using Better11.Core.Models;

namespace Better11.GUI.Views
{
    public sealed partial class PerformancePage : Page
    {
        private readonly PerformanceViewModel _viewModel;
        private bool _isLoading = true;

        public PerformancePage()
        {
            this.InitializeComponent();
            _viewModel = App.Services.GetRequiredService<PerformanceViewModel>();
        }

        private async void Page_Loaded(object sender, RoutedEventArgs e)
        {
            _isLoading = true;
            LoadingBar.Visibility = Visibility.Visible;
            
            await _viewModel.LoadCommand.ExecuteAsync(null);
            UpdateUI();
            
            LoadingBar.Visibility = Visibility.Collapsed;
            _isLoading = false;
        }

        private void UpdateUI()
        {
            CpuUsageText.Text = $"{_viewModel.CpuUsage:F1}%";
            CpuProgressBar.Value = _viewModel.CpuUsage;
            MemoryUsageText.Text = $"{_viewModel.MemoryUsage:F1}% of {_viewModel.MemoryTotal:F1} GB";
            MemoryProgressBar.Value = _viewModel.MemoryUsage;
            FastStartupToggle.IsOn = _viewModel.FastStartupEnabled;
            StatusText.Text = _viewModel.StatusMessage;

            // Set visual effects combo
            var visualEffects = _viewModel.VisualEffects;
            VisualEffectsComboBox.SelectedIndex = visualEffects switch
            {
                "BestPerformance" => 0,
                "Balanced" => 1,
                "BestAppearance" => 2,
                _ => 1
            };
        }

        private async void MaximumPreset_Click(object sender, RoutedEventArgs e)
        {
            LoadingBar.Visibility = Visibility.Visible;
            await _viewModel.ApplyPresetCommand.ExecuteAsync(PerformancePreset.Maximum);
            UpdateUI();
            LoadingBar.Visibility = Visibility.Collapsed;
        }

        private async void BalancedPreset_Click(object sender, RoutedEventArgs e)
        {
            LoadingBar.Visibility = Visibility.Visible;
            await _viewModel.ApplyPresetCommand.ExecuteAsync(PerformancePreset.Balanced);
            UpdateUI();
            LoadingBar.Visibility = Visibility.Collapsed;
        }

        private async void DefaultPreset_Click(object sender, RoutedEventArgs e)
        {
            LoadingBar.Visibility = Visibility.Visible;
            await _viewModel.ApplyPresetCommand.ExecuteAsync(PerformancePreset.Default);
            UpdateUI();
            LoadingBar.Visibility = Visibility.Collapsed;
        }

        private async void RefreshResources_Click(object sender, RoutedEventArgs e)
        {
            await _viewModel.RefreshResourcesCommand.ExecuteAsync(null);
            CpuUsageText.Text = $"{_viewModel.CpuUsage:F1}%";
            CpuProgressBar.Value = _viewModel.CpuUsage;
            MemoryUsageText.Text = $"{_viewModel.MemoryUsage:F1}%";
            MemoryProgressBar.Value = _viewModel.MemoryUsage;
        }

        private async void VisualEffects_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (_isLoading) return;
            
            var preset = VisualEffectsComboBox.SelectedIndex switch
            {
                0 => VisualEffectsPreset.BestPerformance,
                1 => VisualEffectsPreset.Balanced,
                2 => VisualEffectsPreset.BestAppearance,
                _ => VisualEffectsPreset.Balanced
            };
            
            await _viewModel.SetVisualEffectsCommand.ExecuteAsync(preset);
            StatusText.Text = _viewModel.StatusMessage;
        }

        private async void FastStartupToggle_Toggled(object sender, RoutedEventArgs e)
        {
            if (_isLoading) return;
            await _viewModel.ToggleFastStartupCommand.ExecuteAsync(null);
            StatusText.Text = _viewModel.StatusMessage;
        }
    }
}
