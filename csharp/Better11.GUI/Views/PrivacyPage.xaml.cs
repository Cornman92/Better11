using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.Extensions.DependencyInjection;
using Better11.GUI.ViewModels;
using Better11.Core.Models;

namespace Better11.GUI.Views
{
    public sealed partial class PrivacyPage : Page
    {
        private readonly PrivacyViewModel _viewModel;
        private bool _isLoading = true;

        public PrivacyPage()
        {
            this.InitializeComponent();
            _viewModel = App.Services.GetRequiredService<PrivacyViewModel>();
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
            TelemetryComboBox.SelectedIndex = (int)_viewModel.TelemetryLevel;
            CortanaToggle.IsOn = _viewModel.CortanaEnabled;
            LocationToggle.IsOn = _viewModel.LocationEnabled;
            AdvertisingIdToggle.IsOn = _viewModel.AdvertisingIdEnabled;
            ActivityHistoryToggle.IsOn = _viewModel.ActivityHistoryEnabled;
            StatusText.Text = _viewModel.StatusMessage;
        }

        private async void TelemetryComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (_isLoading) return;
            
            var level = (TelemetryLevel)TelemetryComboBox.SelectedIndex;
            await _viewModel.SetTelemetryCommand.ExecuteAsync(level);
            StatusText.Text = _viewModel.StatusMessage;
        }

        private async void CortanaToggle_Toggled(object sender, RoutedEventArgs e)
        {
            if (_isLoading) return;
            await _viewModel.ToggleCortanaCommand.ExecuteAsync(null);
            StatusText.Text = _viewModel.StatusMessage;
        }

        private async void LocationToggle_Toggled(object sender, RoutedEventArgs e)
        {
            if (_isLoading) return;
            await _viewModel.ToggleLocationCommand.ExecuteAsync(null);
            StatusText.Text = _viewModel.StatusMessage;
        }

        private async void AdvertisingIdToggle_Toggled(object sender, RoutedEventArgs e)
        {
            if (_isLoading) return;
            await _viewModel.ToggleAdvertisingIdCommand.ExecuteAsync(null);
            StatusText.Text = _viewModel.StatusMessage;
        }

        private async void ApplyRecommended_Click(object sender, RoutedEventArgs e)
        {
            LoadingBar.Visibility = Visibility.Visible;
            await _viewModel.ApplyRecommendedCommand.ExecuteAsync(null);
            _isLoading = true;
            UpdateUI();
            _isLoading = false;
            LoadingBar.Visibility = Visibility.Collapsed;
        }
    }
}
