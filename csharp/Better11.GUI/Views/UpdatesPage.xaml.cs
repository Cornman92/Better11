using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.Extensions.DependencyInjection;
using Better11.Core.Interfaces;

namespace Better11.GUI.Views
{
    public sealed partial class UpdatesPage : Page
    {
        private readonly IUpdatesService _updatesService;

        public UpdatesPage()
        {
            this.InitializeComponent();
            _updatesService = App.Services.GetRequiredService<IUpdatesService>();
        }

        private async void Page_Loaded(object sender, RoutedEventArgs e)
        {
            LoadingBar.Visibility = Visibility.Visible;
            
            var (start, end) = await _updatesService.GetActiveHoursAsync();
            StartHourComboBox.SelectedIndex = Math.Max(0, start - 6);
            EndHourComboBox.SelectedIndex = Math.Max(0, end - 17);
            
            LoadingBar.Visibility = Visibility.Collapsed;
        }

        private async void CheckUpdates_Click(object sender, RoutedEventArgs e)
        {
            LoadingBar.Visibility = Visibility.Visible;
            StatusText.Text = "Checking for updates...";
            
            var updates = await _updatesService.GetAvailableUpdatesAsync();
            if (updates.Count > 0)
            {
                UpdatesListView.ItemsSource = updates;
                UpdatesListView.Visibility = Visibility.Visible;
                NoUpdatesText.Visibility = Visibility.Collapsed;
                StatusText.Text = $"Found {updates.Count} available updates";
            }
            else
            {
                UpdatesListView.Visibility = Visibility.Collapsed;
                NoUpdatesText.Visibility = Visibility.Visible;
                StatusText.Text = "No updates available";
            }
            
            LoadingBar.Visibility = Visibility.Collapsed;
        }

        private async void PauseUpdates_Click(object sender, RoutedEventArgs e)
        {
            LoadingBar.Visibility = Visibility.Visible;
            await _updatesService.SuspendUpdatesAsync(7);
            StatusText.Text = "Updates paused for 7 days";
            LoadingBar.Visibility = Visibility.Collapsed;
        }

        private async void ResumeUpdates_Click(object sender, RoutedEventArgs e)
        {
            LoadingBar.Visibility = Visibility.Visible;
            await _updatesService.ResumeUpdatesAsync();
            StatusText.Text = "Updates resumed";
            LoadingBar.Visibility = Visibility.Collapsed;
        }

        private async void SetActiveHours_Click(object sender, RoutedEventArgs e)
        {
            int start = StartHourComboBox.SelectedIndex + 6;
            int end = EndHourComboBox.SelectedIndex + 17;
            
            LoadingBar.Visibility = Visibility.Visible;
            await _updatesService.SetActiveHoursAsync(start, end);
            StatusText.Text = $"Active hours set: {start}:00 - {end}:00";
            LoadingBar.Visibility = Visibility.Collapsed;
        }
    }
}
