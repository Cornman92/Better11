using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Better11.Core.Interfaces;
using Better11.Core.Models;
using Microsoft.Extensions.Logging;

namespace Better11.GUI.ViewModels
{
    /// <summary>
    /// Performance optimization ViewModel.
    /// </summary>
    public partial class PerformanceViewModel : BaseViewModel
    {
        private readonly IPerformanceService _performanceService;
        private readonly ISafetyService _safetyService;
        private readonly ILogger<PerformanceViewModel> _logger;

        [ObservableProperty]
        private string _visualEffects = string.Empty;

        [ObservableProperty]
        private bool _fastStartupEnabled;

        [ObservableProperty]
        private double _cpuUsage;

        [ObservableProperty]
        private double _memoryUsage;

        [ObservableProperty]
        private double _memoryTotal;

        public PerformanceViewModel(
            IPerformanceService performanceService,
            ISafetyService safetyService,
            ILogger<PerformanceViewModel> logger)
        {
            _performanceService = performanceService;
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

                var settings = await _performanceService.GetPerformanceSettingsAsync();
                VisualEffects = settings.VisualEffects;
                FastStartupEnabled = settings.FastStartupEnabled;

                var usage = await _performanceService.GetResourceUsageAsync();
                CpuUsage = usage.CPUUsagePercent;
                MemoryUsage = usage.MemoryUsedPercent;
                MemoryTotal = usage.MemoryTotalGB;

                SetStatus("Performance settings loaded");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to load performance settings");
                SetError("Failed to load performance settings");
            }
            finally
            {
                IsLoading = false;
            }
        }

        [RelayCommand]
        private async Task ApplyPresetAsync(PerformancePreset preset)
        {
            try
            {
                IsLoading = true;
                
                await _safetyService.CreateRestorePointAsync($"Better11: Performance {preset}");
                
                var success = await _performanceService.ApplyPerformancePresetAsync(preset);
                if (success)
                {
                    await LoadAsync();
                    SetStatus($"{preset} performance preset applied");
                }
                else
                {
                    SetError("Failed to apply performance preset");
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to apply performance preset");
                SetError("Failed to apply performance preset");
            }
            finally
            {
                IsLoading = false;
            }
        }

        [RelayCommand]
        private async Task ToggleFastStartupAsync()
        {
            try
            {
                if (FastStartupEnabled)
                {
                    await _performanceService.DisableFastStartupAsync();
                    FastStartupEnabled = false;
                    SetStatus("Fast Startup disabled");
                }
                else
                {
                    await _performanceService.EnableFastStartupAsync();
                    FastStartupEnabled = true;
                    SetStatus("Fast Startup enabled");
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to toggle Fast Startup");
                SetError("Failed to toggle Fast Startup");
            }
        }

        [RelayCommand]
        private async Task SetVisualEffectsAsync(VisualEffectsPreset preset)
        {
            try
            {
                IsLoading = true;
                var success = await _performanceService.SetVisualEffectsAsync(preset);
                if (success)
                {
                    VisualEffects = preset.ToString();
                    SetStatus($"Visual effects set to {preset}");
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to set visual effects");
                SetError("Failed to set visual effects");
            }
            finally
            {
                IsLoading = false;
            }
        }

        [RelayCommand]
        private async Task RefreshResourcesAsync()
        {
            try
            {
                var usage = await _performanceService.GetResourceUsageAsync();
                CpuUsage = usage.CPUUsagePercent;
                MemoryUsage = usage.MemoryUsedPercent;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to refresh resources");
            }
        }
    }
}
