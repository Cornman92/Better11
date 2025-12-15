using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.Extensions.DependencyInjection;
using Better11.Core.Interfaces;
using Better11.Core.Models;

namespace Better11.GUI.Views
{
    public sealed partial class GamingPage : Page
    {
        private readonly IGamingService _gamingService;
        private bool _isLoading = true;

        public GamingPage()
        {
            this.InitializeComponent();
            _gamingService = App.Services.GetRequiredService<IGamingService>();
        }

        private async void Page_Loaded(object sender, RoutedEventArgs e)
        {
            _isLoading = true;
            LoadingBar.Visibility = Visibility.Visible;
            
            var settings = await _gamingService.GetGamingSettingsAsync();
            GameModeToggle.IsOn = settings.GameModeEnabled;
            GameBarToggle.IsOn = settings.GameBarEnabled;
            GPUSchedulingToggle.IsOn = settings.GPUSchedulingEnabled;
            MouseAccelToggle.IsOn = settings.MouseAccelerationEnabled;
            NagleToggle.IsOn = settings.NagleAlgorithmEnabled;
            
            LoadingBar.Visibility = Visibility.Collapsed;
            _isLoading = false;
        }

        private async void MaxPreset_Click(object sender, RoutedEventArgs e)
        {
            LoadingBar.Visibility = Visibility.Visible;
            await _gamingService.ApplyGamingPresetAsync(GamingPreset.Maximum);
            StatusText.Text = "Maximum gaming preset applied";
            LoadingBar.Visibility = Visibility.Collapsed;
        }

        private async void BalancedPreset_Click(object sender, RoutedEventArgs e)
        {
            LoadingBar.Visibility = Visibility.Visible;
            await _gamingService.ApplyGamingPresetAsync(GamingPreset.Balanced);
            StatusText.Text = "Balanced gaming preset applied";
            LoadingBar.Visibility = Visibility.Collapsed;
        }

        private async void DefaultPreset_Click(object sender, RoutedEventArgs e)
        {
            LoadingBar.Visibility = Visibility.Visible;
            await _gamingService.ApplyGamingPresetAsync(GamingPreset.Default);
            StatusText.Text = "Default settings restored";
            LoadingBar.Visibility = Visibility.Collapsed;
        }

        private async void GameMode_Toggled(object sender, RoutedEventArgs e)
        {
            if (_isLoading) return;
            await _gamingService.SetGameModeAsync(GameModeToggle.IsOn);
        }

        private async void GameBar_Toggled(object sender, RoutedEventArgs e)
        {
            if (_isLoading) return;
            await _gamingService.SetGameBarAsync(GameBarToggle.IsOn);
        }

        private async void GPUScheduling_Toggled(object sender, RoutedEventArgs e)
        {
            if (_isLoading) return;
            await _gamingService.SetGPUSchedulingAsync(GPUSchedulingToggle.IsOn);
            StatusText.Text = "Restart required to apply GPU scheduling changes";
        }

        private async void MouseAccel_Toggled(object sender, RoutedEventArgs e)
        {
            if (_isLoading) return;
            await _gamingService.SetMouseAccelerationAsync(MouseAccelToggle.IsOn);
        }

        private async void Nagle_Toggled(object sender, RoutedEventArgs e)
        {
            if (_isLoading) return;
            await _gamingService.SetNagleAlgorithmAsync(NagleToggle.IsOn);
        }

        private async void HighPerformance_Click(object sender, RoutedEventArgs e)
        {
            LoadingBar.Visibility = Visibility.Visible;
            await _gamingService.SetHighPerformancePowerAsync(false);
            StatusText.Text = "High Performance power plan activated";
            LoadingBar.Visibility = Visibility.Collapsed;
        }

        private async void UltimatePerformance_Click(object sender, RoutedEventArgs e)
        {
            LoadingBar.Visibility = Visibility.Visible;
            await _gamingService.SetHighPerformancePowerAsync(true);
            StatusText.Text = "Ultimate Performance power plan activated";
            LoadingBar.Visibility = Visibility.Collapsed;
        }
    }
}
