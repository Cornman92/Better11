using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Better11.Core.Interfaces;
using Better11.Core.Models;
using Microsoft.Extensions.Logging;

namespace Better11.GUI.ViewModels
{
    /// <summary>
    /// Backup and restore ViewModel.
    /// </summary>
    public partial class BackupViewModel : BaseViewModel
    {
        private readonly IBackupService _backupService;
        private readonly ISafetyService _safetyService;
        private readonly ILogger<BackupViewModel> _logger;

        [ObservableProperty]
        private ObservableCollection<RestorePoint> _restorePoints = new();

        [ObservableProperty]
        private string _newRestorePointDescription = string.Empty;

        public BackupViewModel(
            IBackupService backupService,
            ISafetyService safetyService,
            ILogger<BackupViewModel> logger)
        {
            _backupService = backupService;
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

                var points = await _safetyService.GetRestorePointsAsync();
                RestorePoints = new ObservableCollection<RestorePoint>(points);

                SetStatus($"Found {points.Count} restore points");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to load restore points");
                SetError("Failed to load restore points");
            }
            finally
            {
                IsLoading = false;
            }
        }

        [RelayCommand]
        private async Task CreateRestorePointAsync()
        {
            if (string.IsNullOrWhiteSpace(NewRestorePointDescription))
            {
                SetError("Please enter a description");
                return;
            }

            try
            {
                IsLoading = true;
                var success = await _safetyService.CreateRestorePointAsync(NewRestorePointDescription);
                if (success)
                {
                    NewRestorePointDescription = string.Empty;
                    await LoadAsync();
                    SetStatus("Restore point created");
                }
                else
                {
                    SetError("Failed to create restore point");
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to create restore point");
                SetError("Failed to create restore point");
            }
            finally
            {
                IsLoading = false;
            }
        }

        [RelayCommand]
        private async Task BackupRegistryAsync()
        {
            try
            {
                IsLoading = true;
                var result = await _backupService.BackupRegistryAsync();
                if (result != null)
                {
                    SetStatus($"Registry backed up to {result}");
                }
                else
                {
                    SetError("Failed to backup registry");
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to backup registry");
                SetError("Failed to backup registry");
            }
            finally
            {
                IsLoading = false;
            }
        }

        [RelayCommand]
        private async Task ExportSettingsAsync()
        {
            try
            {
                IsLoading = true;
                var path = await _backupService.ExportSettingsAsync();
                if (!string.IsNullOrEmpty(path))
                {
                    SetStatus($"Settings exported to {path}");
                }
                else
                {
                    SetError("Failed to export settings");
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to export settings");
                SetError("Failed to export settings");
            }
            finally
            {
                IsLoading = false;
            }
        }
    }
}
