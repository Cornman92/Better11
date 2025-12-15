using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.Extensions.DependencyInjection;
using Better11.GUI.ViewModels;

namespace Better11.GUI.Views
{
    public sealed partial class SettingsPage : Page
    {
        private readonly SettingsViewModel _viewModel;

        public SettingsPage()
        {
            this.InitializeComponent();
            _viewModel = App.Services.GetRequiredService<SettingsViewModel>();
        }

        private async void Page_Loaded(object sender, RoutedEventArgs e)
        {
            await _viewModel.LoadCommand.ExecuteAsync(null);
            VersionText.Text = $"Version {_viewModel.AppVersion}";
            RestorePointsToggle.IsOn = _viewModel.CreateRestorePoints;
            AdvancedToggle.IsOn = _viewModel.ShowAdvancedOptions;
        }

        private async void SaveSettings_Click(object sender, RoutedEventArgs e)
        {
            _viewModel.CreateRestorePoints = RestorePointsToggle.IsOn;
            _viewModel.ShowAdvancedOptions = AdvancedToggle.IsOn;
            await _viewModel.SaveSettingsCommand.ExecuteAsync(null);
            StatusText.Text = _viewModel.StatusMessage;
        }

        private async void ResetSettings_Click(object sender, RoutedEventArgs e)
        {
            await _viewModel.ResetSettingsCommand.ExecuteAsync(null);
            RestorePointsToggle.IsOn = _viewModel.CreateRestorePoints;
            AdvancedToggle.IsOn = _viewModel.ShowAdvancedOptions;
            StatusText.Text = _viewModel.StatusMessage;
        }
    }
}
