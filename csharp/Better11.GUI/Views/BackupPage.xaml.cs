using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.Extensions.DependencyInjection;
using Better11.GUI.ViewModels;

namespace Better11.GUI.Views
{
    public sealed partial class BackupPage : Page
    {
        private readonly BackupViewModel _viewModel;

        public BackupPage()
        {
            this.InitializeComponent();
            _viewModel = App.Services.GetRequiredService<BackupViewModel>();
        }

        private async void Page_Loaded(object sender, RoutedEventArgs e)
        {
            LoadingBar.Visibility = Visibility.Visible;
            await _viewModel.LoadCommand.ExecuteAsync(null);
            RestorePointsListView.ItemsSource = _viewModel.RestorePoints;
            StatusText.Text = _viewModel.StatusMessage;
            LoadingBar.Visibility = Visibility.Collapsed;
        }

        private async void Refresh_Click(object sender, RoutedEventArgs e)
        {
            LoadingBar.Visibility = Visibility.Visible;
            await _viewModel.LoadCommand.ExecuteAsync(null);
            RestorePointsListView.ItemsSource = _viewModel.RestorePoints;
            StatusText.Text = _viewModel.StatusMessage;
            LoadingBar.Visibility = Visibility.Collapsed;
        }

        private async void CreateRestorePoint_Click(object sender, RoutedEventArgs e)
        {
            _viewModel.NewRestorePointDescription = RestorePointDescriptionBox.Text;
            LoadingBar.Visibility = Visibility.Visible;
            await _viewModel.CreateRestorePointCommand.ExecuteAsync(null);
            RestorePointDescriptionBox.Text = "";
            RestorePointsListView.ItemsSource = _viewModel.RestorePoints;
            StatusText.Text = _viewModel.StatusMessage;
            LoadingBar.Visibility = Visibility.Collapsed;
        }

        private async void BackupRegistry_Click(object sender, RoutedEventArgs e)
        {
            LoadingBar.Visibility = Visibility.Visible;
            await _viewModel.BackupRegistryCommand.ExecuteAsync(null);
            StatusText.Text = _viewModel.StatusMessage;
            LoadingBar.Visibility = Visibility.Collapsed;
        }

        private async void ExportSettings_Click(object sender, RoutedEventArgs e)
        {
            LoadingBar.Visibility = Visibility.Visible;
            await _viewModel.ExportSettingsCommand.ExecuteAsync(null);
            StatusText.Text = _viewModel.StatusMessage;
            LoadingBar.Visibility = Visibility.Collapsed;
        }
    }
}
