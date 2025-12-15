using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.Extensions.DependencyInjection;
using Better11.GUI.ViewModels;

namespace Better11.GUI.Views
{
    public sealed partial class AppsPage : Page
    {
        private readonly AppsViewModel _viewModel;

        public AppsPage()
        {
            this.InitializeComponent();
            _viewModel = App.Services.GetRequiredService<AppsViewModel>();
        }

        private async void Page_Loaded(object sender, RoutedEventArgs e)
        {
            LoadingBar.Visibility = Visibility.Visible;
            await _viewModel.LoadCommand.ExecuteAsync(null);
            AppsListView.ItemsSource = _viewModel.InstalledApps;
            StatusText.Text = _viewModel.StatusMessage;
            LoadingBar.Visibility = Visibility.Collapsed;
        }

        private async void Refresh_Click(object sender, RoutedEventArgs e)
        {
            LoadingBar.Visibility = Visibility.Visible;
            await _viewModel.LoadCommand.ExecuteAsync(null);
            AppsListView.ItemsSource = _viewModel.InstalledApps;
            StatusText.Text = _viewModel.StatusMessage;
            LoadingBar.Visibility = Visibility.Collapsed;
        }

        private void AppsListView_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            _viewModel.SelectedApp = AppsListView.SelectedItem as Better11.Core.Models.AppInfo;
            UninstallButton.IsEnabled = _viewModel.SelectedApp != null;
        }

        private async void Uninstall_Click(object sender, RoutedEventArgs e)
        {
            if (_viewModel.SelectedApp == null) return;

            var dialog = new ContentDialog
            {
                Title = "Confirm Uninstall",
                Content = $"Are you sure you want to uninstall {_viewModel.SelectedApp.Name}?",
                PrimaryButtonText = "Uninstall",
                CloseButtonText = "Cancel",
                XamlRoot = this.XamlRoot
            };

            var result = await dialog.ShowAsync();
            if (result == ContentDialogResult.Primary)
            {
                LoadingBar.Visibility = Visibility.Visible;
                await _viewModel.UninstallSelectedCommand.ExecuteAsync(null);
                StatusText.Text = _viewModel.StatusMessage;
                LoadingBar.Visibility = Visibility.Collapsed;
            }
        }
    }
}
