using System;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using System.Windows;
using Better11.Core.Apps;
using Better11.Core.Apps.Models;

namespace Better11.GUI
{
    public partial class MainWindow : Window
    {
        private AppManager? _manager;

        public MainWindow()
        {
            InitializeComponent();
            Loaded += MainWindow_Loaded;
        }

        private void MainWindow_Loaded(object sender, RoutedEventArgs e)
        {
            try
            {
                var catalogPath = GetCatalogPath();
                _manager = new AppManager(catalogPath);
                RefreshAppList();
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Failed to load catalog: {ex.Message}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private string GetCatalogPath()
        {
            var baseDir = AppDomain.CurrentDomain.BaseDirectory;
            var catalogPath = Path.Combine(
                baseDir,
                "..", "..", "..", "..", "..",
                "better11", "apps", "catalog.json");
            return Path.GetFullPath(catalogPath);
        }

        private void RefreshAppList()
        {
            if (_manager == null) return;

            try
            {
                var apps = _manager.ListAvailable();
                AppListBox.ItemsSource = apps;
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Failed to load applications: {ex.Message}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private string? GetSelectedAppId()
        {
            if (AppListBox.SelectedItem is AppMetadata app)
            {
                return app.AppId;
            }
            return null;
        }

        private void Report(string message)
        {
            StatusLabel.Text = message;
        }

        private async void DownloadButton_Click(object sender, RoutedEventArgs e)
        {
            var appId = GetSelectedAppId();
            if (appId == null)
            {
                MessageBox.Show("Select an app to download", "Select", MessageBoxButton.OK, MessageBoxImage.Information);
                return;
            }

            if (_manager == null) return;

            try
            {
                Report($"Downloading {appId}...");
                var destination = await _manager.DownloadAsync(appId);
                Report($"Downloaded {appId} to {destination}");
                MessageBox.Show($"Downloaded to {destination}", "Success", MessageBoxButton.OK, MessageBoxImage.Information);
            }
            catch (Exception ex)
            {
                Report($"Download failed: {ex.Message}");
                MessageBox.Show($"Download failed: {ex.Message}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private async void InstallButton_Click(object sender, RoutedEventArgs e)
        {
            var appId = GetSelectedAppId();
            if (appId == null)
            {
                MessageBox.Show("Select an app to install", "Select", MessageBoxButton.OK, MessageBoxImage.Information);
                return;
            }

            if (_manager == null) return;

            try
            {
                Report($"Installing {appId}...");
                var (status, result) = await _manager.InstallAsync(appId);
                var command = result.Command.Count > 0 ? string.Join(" ", result.Command) : "already installed";
                Report($"Installed {status.AppId} ({command})");
                MessageBox.Show($"Installed {status.AppId} v{status.Version}", "Success", MessageBoxButton.OK, MessageBoxImage.Information);
            }
            catch (Exception ex)
            {
                Report($"Installation failed: {ex.Message}");
                MessageBox.Show($"Installation failed: {ex.Message}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private void UninstallButton_Click(object sender, RoutedEventArgs e)
        {
            var appId = GetSelectedAppId();
            if (appId == null)
            {
                MessageBox.Show("Select an app to uninstall", "Select", MessageBoxButton.OK, MessageBoxImage.Information);
                return;
            }

            if (_manager == null) return;

            try
            {
                Report($"Uninstalling {appId}...");
                var result = _manager.Uninstall(appId);
                var command = string.Join(" ", result.Command);
                Report($"Uninstalled {appId} ({command})");
                MessageBox.Show($"Uninstalled {appId}", "Success", MessageBoxButton.OK, MessageBoxImage.Information);
            }
            catch (Exception ex)
            {
                Report($"Uninstall failed: {ex.Message}");
                MessageBox.Show($"Uninstall failed: {ex.Message}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private void RefreshButton_Click(object sender, RoutedEventArgs e)
        {
            RefreshAppList();
            Report("Refreshed application list");
        }
    }
}
