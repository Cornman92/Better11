using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Input;
using Better11.Core.Apps.Models;
using Better11.Core.Interfaces;
using Better11.Core.Models;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Microsoft.Extensions.Logging;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;

namespace Better11.WinUI.ViewModels
{
    /// <summary>
    /// View model for the Applications page.
    /// Manages application listing, installation, and updates.
    /// </summary>
    public partial class ApplicationsViewModel : ObservableObject
    {
        private readonly IAppManager _appManager;
        private readonly ILogger<ApplicationsViewModel> _logger;

        [ObservableProperty]
        private ObservableCollection<AppViewModel> _applications = new();

        [ObservableProperty]
        private ObservableCollection<AppViewModel> _filteredApplications = new();

        [ObservableProperty]
        private string _searchText = string.Empty;

        [ObservableProperty]
        private int _selectedFilterIndex = 0;

        [ObservableProperty]
        private bool _isLoading = false;

        public ApplicationsViewModel(
            IAppManager appManager,
            ILogger<ApplicationsViewModel> logger)
        {
            _appManager = appManager;
            _logger = logger;
        }

        public async Task InitializeAsync()
        {
            await LoadApplicationsAsync();
        }

        [RelayCommand]
        private async Task RefreshAsync()
        {
            await LoadApplicationsAsync();
        }

        partial void OnSearchTextChanged(string value)
        {
            ApplyFilters();
        }

        partial void OnSelectedFilterIndexChanged(int value)
        {
            ApplyFilters();
        }

        private async Task LoadApplicationsAsync()
        {
            try
            {
                IsLoading = true;
                _logger.LogInformation("Loading applications");

                var apps = await _appManager.ListAvailableAppsAsync();
                var statuses = await _appManager.GetAppStatusAsync();

                var statusDict = statuses.ToDictionary(s => s.AppId);

                Applications.Clear();

                foreach (var app in apps)
                {
                    var status = statusDict.GetValueOrDefault(app.AppId);

                    Applications.Add(new AppViewModel
                    {
                        AppId = app.AppId,
                        Name = app.Name,
                        Version = app.Version,
                        Description = app.Description,
                        IsInstalled = status?.Installed ?? false,
                        InstalledVersion = status?.Version ?? string.Empty,
                        HasUpdate = false, // TODO: Check for updates
                        InstallCommand = new RelayCommand(async () => await InstallAppAsync(app.AppId)),
                        UninstallCommand = new RelayCommand(async () => await UninstallAppAsync(app.AppId)),
                        UpdateCommand = new RelayCommand(async () => await UpdateAppAsync(app.AppId)),
                        PlanCommand = new RelayCommand(async () => await ShowPlanAsync(app.AppId))
                    });
                }

                ApplyFilters();

                _logger.LogInformation("Loaded {Count} applications", Applications.Count);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to load applications");
                // TODO: Show error dialog
            }
            finally
            {
                IsLoading = false;
            }
        }

        private void ApplyFilters()
        {
            var filtered = Applications.AsEnumerable();

            // Apply search filter
            if (!string.IsNullOrWhiteSpace(SearchText))
            {
                filtered = filtered.Where(a =>
                    a.Name.Contains(SearchText, StringComparison.OrdinalIgnoreCase) ||
                    (a.Description?.Contains(SearchText, StringComparison.OrdinalIgnoreCase) ?? false));
            }

            // Apply status filter
            filtered = SelectedFilterIndex switch
            {
                1 => filtered.Where(a => a.IsInstalled),  // Installed
                2 => filtered.Where(a => !a.IsInstalled), // Available
                3 => filtered.Where(a => a.HasUpdate),    // Updates Available
                _ => filtered
            };

            FilteredApplications.Clear();
            foreach (var app in filtered)
            {
                FilteredApplications.Add(app);
            }
        }

        private async Task InstallAppAsync(string appId)
        {
            try
            {
                _logger.LogInformation("Installing app: {AppId}", appId);

                IsLoading = true;

                var result = await _appManager.InstallAppAsync(appId);

                if (result.Success)
                {
                    // TODO: Show success notification
                    await LoadApplicationsAsync(); // Refresh list
                }
                else
                {
                    // TODO: Show error dialog
                    _logger.LogError("Installation failed: {Error}", result.ErrorMessage);
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to install app: {AppId}", appId);
            }
            finally
            {
                IsLoading = false;
            }
        }

        private async Task UninstallAppAsync(string appId)
        {
            try
            {
                _logger.LogInformation("Uninstalling app: {AppId}", appId);

                IsLoading = true;

                var result = await _appManager.UninstallAppAsync(appId);

                if (result.Success)
                {
                    await LoadApplicationsAsync();
                }
                else
                {
                    _logger.LogError("Uninstall failed: {Error}", result.ErrorMessage);
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to uninstall app: {AppId}", appId);
            }
            finally
            {
                IsLoading = false;
            }
        }

        private async Task UpdateAppAsync(string appId)
        {
            // Similar to InstallAppAsync but for updates
            await InstallAppAsync(appId);
        }

        private async Task ShowPlanAsync(string appId)
        {
            try
            {
                _logger.LogInformation("Showing install plan for: {AppId}", appId);

                IsLoading = true;

                var plan = await _appManager.GetInstallPlanAsync(appId);

                // Build the content for the dialog
                var content = new StringBuilder();

                // Add warnings if any
                if (plan.Warnings.Count > 0)
                {
                    content.AppendLine("⚠️ Warnings:");
                    foreach (var warning in plan.Warnings)
                    {
                        content.AppendLine($"  • {warning}");
                    }
                    content.AppendLine();
                }

                // Add installation steps
                content.AppendLine("Installation Steps:");
                content.AppendLine();

                foreach (var step in plan.Steps)
                {
                    var actionSymbol = step.Action switch
                    {
                        "install" => "📦",
                        "skip" => "✓",
                        "blocked" => "❌",
                        _ => "•"
                    };

                    content.AppendLine($"{actionSymbol} {step.Name} (v{step.Version})");
                    content.AppendLine($"   Action: {step.Action.ToUpper()}");

                    if (!string.IsNullOrEmpty(step.Notes))
                    {
                        content.AppendLine($"   Notes: {step.Notes}");
                    }

                    if (step.Dependencies.Count > 0)
                    {
                        content.AppendLine($"   Dependencies: {string.Join(", ", step.Dependencies)}");
                    }

                    content.AppendLine();
                }

                // Add summary
                content.AppendLine("Summary:");
                content.AppendLine($"  • To install: {plan.InstallCount()}");
                content.AppendLine($"  • Already installed: {plan.SkipCount()}");

                if (plan.HasBlockedSteps())
                {
                    content.AppendLine($"  • Blocked: {plan.Steps.Count(s => s.Action == "blocked")}");
                }

                // Create and show the dialog
                var dialog = new ContentDialog
                {
                    Title = $"Installation Plan: {appId}",
                    Content = new ScrollViewer
                    {
                        Content = new TextBlock
                        {
                            Text = content.ToString(),
                            FontFamily = new Microsoft.UI.Xaml.Media.FontFamily("Consolas"),
                            IsTextSelectionEnabled = true
                        },
                        MaxHeight = 500
                    },
                    CloseButtonText = "Cancel",
                    XamlRoot = App.GetService<MainWindow>().Content.XamlRoot
                };

                // Only add install button if plan is valid
                if (!plan.HasBlockedSteps() && plan.InstallCount() > 0)
                {
                    dialog.PrimaryButtonText = "Install";
                    dialog.PrimaryButtonClick += async (_, _) =>
                    {
                        await InstallAppAsync(appId);
                    };
                }

                await dialog.ShowAsync();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to show install plan for: {AppId}", appId);

                var errorDialog = new ContentDialog
                {
                    Title = "Error",
                    Content = $"Failed to generate install plan: {ex.Message}",
                    CloseButtonText = "OK",
                    XamlRoot = App.GetService<MainWindow>().Content.XamlRoot
                };

                await errorDialog.ShowAsync();
            }
            finally
            {
                IsLoading = false;
            }
        }
    }

    public class AppViewModel : ObservableObject
    {
        public string AppId { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public string Version { get; set; } = string.Empty;
        public string? Description { get; set; }
        public bool IsInstalled { get; set; }
        public Visibility IsNotInstalled => IsInstalled ? Visibility.Collapsed : Visibility.Visible;
        public string InstalledVersion { get; set; } = string.Empty;
        public bool HasUpdate { get; set; }
        public ICommand? InstallCommand { get; set; }
        public ICommand? UninstallCommand { get; set; }
        public ICommand? UpdateCommand { get; set; }
        public ICommand? PlanCommand { get; set; }
    }
}
