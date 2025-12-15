using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Better11.Core.Interfaces;
using Better11.Core.Models;
using Microsoft.Extensions.Logging;

namespace Better11.GUI.ViewModels
{
    /// <summary>
    /// Privacy settings ViewModel.
    /// </summary>
    public partial class PrivacyViewModel : BaseViewModel
    {
        private readonly IPrivacyService _privacyService;
        private readonly ISafetyService _safetyService;
        private readonly ILogger<PrivacyViewModel> _logger;

        [ObservableProperty]
        private TelemetryLevel _telemetryLevel;

        [ObservableProperty]
        private bool _cortanaEnabled;

        [ObservableProperty]
        private bool _locationEnabled;

        [ObservableProperty]
        private bool _advertisingIdEnabled;

        [ObservableProperty]
        private bool _activityHistoryEnabled;

        public PrivacyViewModel(
            IPrivacyService privacyService,
            ISafetyService safetyService,
            ILogger<PrivacyViewModel> logger)
        {
            _privacyService = privacyService;
            _safetyService = safetyService;
            _logger = logger;
        }

        [RelayCommand]
        private async Task LoadAsync()
        {
            try
            {
                IsLoading = true;
                ClearError();

                var status = await _privacyService.GetPrivacyStatusAsync();
                TelemetryLevel = status.TelemetryLevel;
                CortanaEnabled = status.CortanaEnabled;
                LocationEnabled = status.LocationEnabled;
                AdvertisingIdEnabled = status.AdvertisingIdEnabled;
                ActivityHistoryEnabled = status.ActivityHistoryEnabled;

                SetStatus("Privacy settings loaded");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to load privacy settings");
                SetError("Failed to load privacy settings");
            }
            finally
            {
                IsLoading = false;
            }
        }

        [RelayCommand]
        private async Task SetTelemetryAsync(TelemetryLevel level)
        {
            try
            {
                IsLoading = true;
                await _privacyService.SetTelemetryLevelAsync(level);
                TelemetryLevel = level;
                SetStatus($"Telemetry level set to {level}");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to set telemetry level");
                SetError("Failed to set telemetry level");
            }
            finally
            {
                IsLoading = false;
            }
        }

        [RelayCommand]
        private async Task ToggleCortanaAsync()
        {
            try
            {
                var newValue = !CortanaEnabled;
                await _privacyService.SetCortanaEnabledAsync(newValue);
                CortanaEnabled = newValue;
                SetStatus($"Cortana {(newValue ? "enabled" : "disabled")}");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to toggle Cortana");
                SetError("Failed to toggle Cortana");
            }
        }

        [RelayCommand]
        private async Task ToggleLocationAsync()
        {
            try
            {
                var newValue = !LocationEnabled;
                await _privacyService.SetLocationEnabledAsync(newValue);
                LocationEnabled = newValue;
                SetStatus($"Location {(newValue ? "enabled" : "disabled")}");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to toggle location");
                SetError("Failed to toggle location");
            }
        }

        [RelayCommand]
        private async Task ToggleAdvertisingIdAsync()
        {
            try
            {
                var newValue = !AdvertisingIdEnabled;
                await _privacyService.SetAdvertisingIdEnabledAsync(newValue);
                AdvertisingIdEnabled = newValue;
                SetStatus($"Advertising ID {(newValue ? "enabled" : "disabled")}");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to toggle advertising ID");
                SetError("Failed to toggle advertising ID");
            }
        }

        [RelayCommand]
        private async Task ApplyRecommendedAsync()
        {
            try
            {
                IsLoading = true;
                
                // Create restore point first
                await _safetyService.CreateRestorePointAsync("Better11: Privacy Settings");
                
                var success = await _privacyService.ApplyRecommendedSettingsAsync();
                if (success)
                {
                    await LoadAsync();
                    SetStatus("Recommended privacy settings applied");
                }
                else
                {
                    SetError("Some settings could not be applied");
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to apply recommended settings");
                SetError("Failed to apply recommended settings");
            }
            finally
            {
                IsLoading = false;
            }
        }
    }
}
