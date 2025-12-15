using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.Extensions.DependencyInjection;
using Better11.Core.Interfaces;

namespace Better11.GUI.Views
{
    public sealed partial class DriversPage : Page
    {
        private readonly IDriversService _driversService;

        public DriversPage()
        {
            this.InitializeComponent();
            _driversService = App.Services.GetRequiredService<IDriversService>();
        }

        private async void Page_Loaded(object sender, RoutedEventArgs e)
        {
            await LoadDriversAsync();
        }

        private async Task LoadDriversAsync()
        {
            LoadingBar.Visibility = Visibility.Visible;
            
            var drivers = await _driversService.GetDriversAsync();
            DriversListView.ItemsSource = drivers;
            
            var issues = await _driversService.GetDriverIssuesAsync();
            IssuesListView.ItemsSource = issues;
            
            StatusText.Text = $"Found {drivers.Count} drivers, {issues.Count} issues";
            LoadingBar.Visibility = Visibility.Collapsed;
        }

        private async void Refresh_Click(object sender, RoutedEventArgs e)
        {
            await LoadDriversAsync();
        }

        private async void BackupDrivers_Click(object sender, RoutedEventArgs e)
        {
            LoadingBar.Visibility = Visibility.Visible;
            StatusText.Text = "Backing up drivers...";
            
            var result = await _driversService.BackupDriversAsync();
            if (result.Success)
            {
                StatusText.Text = $"Backed up {result.DriversBackedUp} drivers to {result.Path}";
            }
            else
            {
                StatusText.Text = $"Backup failed: {result.Error}";
            }
            
            LoadingBar.Visibility = Visibility.Collapsed;
        }

        private async void ExportList_Click(object sender, RoutedEventArgs e)
        {
            LoadingBar.Visibility = Visibility.Visible;
            
            var path = await _driversService.ExportDriverListAsync();
            if (!string.IsNullOrEmpty(path))
            {
                StatusText.Text = $"Driver list exported to {path}";
            }
            else
            {
                StatusText.Text = "Failed to export driver list";
            }
            
            LoadingBar.Visibility = Visibility.Collapsed;
        }
    }
}
