using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Better11.Core.Interfaces;
using Microsoft.Extensions.Logging;

namespace Better11.GUI.ViewModels
{
    /// <summary>
    /// Network management ViewModel.
    /// </summary>
    public partial class NetworkViewModel : BaseViewModel
    {
        private readonly INetworkService _networkService;
        private readonly ILogger<NetworkViewModel> _logger;

        [ObservableProperty]
        private ObservableCollection<NetworkAdapterViewModel> _adapters = new();

        [ObservableProperty]
        private bool _isConnected;

        public NetworkViewModel(
            INetworkService networkService,
            ILogger<NetworkViewModel> logger)
        {
            _networkService = networkService;
            _logger = logger;
        }

        [RelayCommand]
        private async Task LoadAsync()
        {
            try
            {
                IsLoading = true;
                ClearError();

                var adapters = await _networkService.GetNetworkAdaptersAsync();
                Adapters = new ObservableCollection<NetworkAdapterViewModel>(
                    adapters.Select(a => new NetworkAdapterViewModel
                    {
                        Name = a.Name,
                        Description = a.Description,
                        Status = a.Status,
                        IPAddress = a.IPAddresses.FirstOrDefault() ?? "N/A",
                        MacAddress = a.MacAddress
                    }));

                IsConnected = await _networkService.TestConnectivityAsync();
                SetStatus("Network information loaded");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to load network info");
                SetError("Failed to load network information");
            }
            finally
            {
                IsLoading = false;
            }
        }

        [RelayCommand]
        private async Task FlushDnsAsync()
        {
            try
            {
                IsLoading = true;
                await _networkService.FlushDnsAsync();
                SetStatus("DNS cache flushed");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to flush DNS");
                SetError("Failed to flush DNS cache");
            }
            finally
            {
                IsLoading = false;
            }
        }

        [RelayCommand]
        private async Task ResetTcpIpAsync()
        {
            try
            {
                IsLoading = true;
                await _networkService.ResetTcpIpAsync();
                SetStatus("TCP/IP stack reset. Restart required.");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to reset TCP/IP");
                SetError("Failed to reset TCP/IP stack");
            }
            finally
            {
                IsLoading = false;
            }
        }

        [RelayCommand]
        private async Task ResetWinsockAsync()
        {
            try
            {
                IsLoading = true;
                await _networkService.ResetWinsockAsync();
                SetStatus("Winsock catalog reset. Restart required.");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to reset Winsock");
                SetError("Failed to reset Winsock");
            }
            finally
            {
                IsLoading = false;
            }
        }

        [RelayCommand]
        private async Task TestConnectivityAsync()
        {
            try
            {
                IsLoading = true;
                IsConnected = await _networkService.TestConnectivityAsync();
                SetStatus(IsConnected ? "Internet connected" : "No internet connection");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to test connectivity");
                SetError("Failed to test connectivity");
            }
            finally
            {
                IsLoading = false;
            }
        }
    }

    public class NetworkAdapterViewModel
    {
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public string Status { get; set; } = string.Empty;
        public string IPAddress { get; set; } = string.Empty;
        public string MacAddress { get; set; } = string.Empty;
    }
}
