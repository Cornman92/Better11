using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.Extensions.DependencyInjection;
using Better11.GUI.ViewModels;

namespace Better11.GUI.Views
{
    public sealed partial class NetworkPage : Page
    {
        private readonly NetworkViewModel _viewModel;

        public NetworkPage()
        {
            this.InitializeComponent();
            _viewModel = App.Services.GetRequiredService<NetworkViewModel>();
        }

        private async void Page_Loaded(object sender, RoutedEventArgs e)
        {
            LoadingBar.Visibility = Visibility.Visible;
            await _viewModel.LoadCommand.ExecuteAsync(null);
            AdaptersListView.ItemsSource = _viewModel.Adapters;
            ConnectionStatusText.Text = _viewModel.IsConnected ? "Connected" : "Disconnected";
            StatusText.Text = _viewModel.StatusMessage;
            LoadingBar.Visibility = Visibility.Collapsed;
        }

        private async void TestConnection_Click(object sender, RoutedEventArgs e)
        {
            LoadingBar.Visibility = Visibility.Visible;
            await _viewModel.TestConnectivityCommand.ExecuteAsync(null);
            ConnectionStatusText.Text = _viewModel.IsConnected ? "Connected" : "Disconnected";
            StatusText.Text = _viewModel.StatusMessage;
            LoadingBar.Visibility = Visibility.Collapsed;
        }

        private async void FlushDns_Click(object sender, RoutedEventArgs e)
        {
            LoadingBar.Visibility = Visibility.Visible;
            await _viewModel.FlushDnsCommand.ExecuteAsync(null);
            StatusText.Text = _viewModel.StatusMessage;
            LoadingBar.Visibility = Visibility.Collapsed;
        }

        private async void ResetTcpIp_Click(object sender, RoutedEventArgs e)
        {
            var dialog = new ContentDialog
            {
                Title = "Reset TCP/IP",
                Content = "This will reset the TCP/IP stack. A restart will be required. Continue?",
                PrimaryButtonText = "Reset",
                CloseButtonText = "Cancel",
                XamlRoot = this.XamlRoot
            };

            var result = await dialog.ShowAsync();
            if (result == ContentDialogResult.Primary)
            {
                LoadingBar.Visibility = Visibility.Visible;
                await _viewModel.ResetTcpIpCommand.ExecuteAsync(null);
                StatusText.Text = _viewModel.StatusMessage;
                LoadingBar.Visibility = Visibility.Collapsed;
            }
        }

        private async void ResetWinsock_Click(object sender, RoutedEventArgs e)
        {
            var dialog = new ContentDialog
            {
                Title = "Reset Winsock",
                Content = "This will reset the Winsock catalog. A restart will be required. Continue?",
                PrimaryButtonText = "Reset",
                CloseButtonText = "Cancel",
                XamlRoot = this.XamlRoot
            };

            var result = await dialog.ShowAsync();
            if (result == ContentDialogResult.Primary)
            {
                LoadingBar.Visibility = Visibility.Visible;
                await _viewModel.ResetWinsockCommand.ExecuteAsync(null);
                StatusText.Text = _viewModel.StatusMessage;
                LoadingBar.Visibility = Visibility.Collapsed;
            }
        }
    }
}
