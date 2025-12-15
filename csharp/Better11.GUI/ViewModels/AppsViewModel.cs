using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Better11.Core.Interfaces;
using Better11.Core.Models;
using Microsoft.Extensions.Logging;

namespace Better11.GUI.ViewModels
{
    /// <summary>
    /// Apps management ViewModel.
    /// </summary>
    public partial class AppsViewModel : BaseViewModel
    {
        private readonly IAppService _appService;
        private readonly ILogger<AppsViewModel> _logger;

        [ObservableProperty]
        private ObservableCollection<AppInfo> _installedApps = new();

        [ObservableProperty]
        private AppInfo? _selectedApp;

        public AppsViewModel(
            IAppService appService,
            ILogger<AppsViewModel> logger)
        {
            _appService = appService;
            _logger = logger;
        }

        [RelayCommand]
        private async Task LoadAsync()
        {
            try
            {
                IsLoading = true;
                ClearError();

                var apps = await _appService.GetInstalledAppsAsync();
                InstalledApps = new ObservableCollection<AppInfo>(apps);

                SetStatus($"Found {apps.Count} installed apps");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to load apps");
                SetError("Failed to load installed apps");
            }
            finally
            {
                IsLoading = false;
            }
        }

        [RelayCommand]
        private async Task UninstallSelectedAsync()
        {
            if (SelectedApp == null) return;

            try
            {
                IsLoading = true;
                var success = await _appService.UninstallAppAsync(SelectedApp.Name);
                if (success)
                {
                    InstalledApps.Remove(SelectedApp);
                    SetStatus($"Uninstalled {SelectedApp.Name}");
                    SelectedApp = null;
                }
                else
                {
                    SetError($"Failed to uninstall {SelectedApp.Name}");
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to uninstall app");
                SetError("Failed to uninstall app");
            }
            finally
            {
                IsLoading = false;
            }
        }
    }
}
