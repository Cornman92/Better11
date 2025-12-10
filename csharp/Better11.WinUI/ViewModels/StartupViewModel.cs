using System;
using System.Collections.ObjectModel;
using System.Threading.Tasks;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Microsoft.Extensions.Logging;
using Microsoft.UI;
using Windows.UI;

namespace Better11.WinUI.ViewModels
{
    /// <summary>
    /// View model for the Startup page.
    /// </summary>
    public partial class StartupViewModel : ObservableObject
    {
        private readonly ILogger<StartupViewModel> _logger;

        [ObservableProperty]
        private ObservableCollection<StartupProgramViewModel> _startupPrograms = new();

        [ObservableProperty]
        private int _totalPrograms = 0;

        [ObservableProperty]
        private int _enabledPrograms = 0;

        [ObservableProperty]
        private int _highImpactPrograms = 0;

        [ObservableProperty]
        private int _filterIndex = 0;

        [ObservableProperty]
        private bool _isLoading = false;

        public StartupViewModel(ILogger<StartupViewModel> logger)
        {
            _logger = logger;
        }

        public async Task InitializeAsync()
        {
            await LoadStartupProgramsAsync();
        }

        [RelayCommand]
        private async Task LoadStartupProgramsAsync()
        {
            try
            {
                IsLoading = true;
                _logger.LogInformation("Loading startup programs");

                // TODO: Call PowerShell Get-Better11StartupImpact
                await Task.Delay(1000); // Simulate

                // Sample data
                StartupPrograms.Clear();
                StartupPrograms.Add(new StartupProgramViewModel
                {
                    Name = "Microsoft OneDrive",
                    Location = "Registry: HKCU\\Run",
                    Type = "Registry",
                    Impact = "High",
                    ImpactColor = "#F25022",
                    IsEnabled = true
                });
                StartupPrograms.Add(new StartupProgramViewModel
                {
                    Name = "Discord",
                    Location = "Startup Folder",
                    Type = "Shortcut",
                    Impact = "Medium",
                    ImpactColor = "#FFB900",
                    IsEnabled = true
                });
                StartupPrograms.Add(new StartupProgramViewModel
                {
                    Name = "Spotify",
                    Location = "Registry: HKCU\\Run",
                    Type = "Registry",
                    Impact = "Low",
                    ImpactColor = "#7FBA00",
                    IsEnabled = false
                });

                UpdateStatistics();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to load startup programs");
            }
            finally
            {
                IsLoading = false;
            }
        }

        [RelayCommand]
        private async Task RefreshAsync()
        {
            await LoadStartupProgramsAsync();
        }

        [RelayCommand]
        private async Task DisableAllHighImpactAsync()
        {
            _logger.LogInformation("Disabling all high impact startup programs");
            
            foreach (var program in StartupPrograms)
            {
                if (program.Impact == "High")
                {
                    program.IsEnabled = false;
                }
            }
            
            UpdateStatistics();
        }

        [RelayCommand]
        private async Task AnalyzeImpactAsync()
        {
            _logger.LogInformation("Analyzing startup impact");
            // TODO: Show detailed analysis
        }

        private void UpdateStatistics()
        {
            TotalPrograms = StartupPrograms.Count;
            EnabledPrograms = 0;
            HighImpactPrograms = 0;

            foreach (var program in StartupPrograms)
            {
                if (program.IsEnabled) EnabledPrograms++;
                if (program.Impact == "High") HighImpactPrograms++;
            }
        }
    }

    public class StartupProgramViewModel : ObservableObject
    {
        public string Name { get; set; } = string.Empty;
        public string Location { get; set; } = string.Empty;
        public string Type { get; set; } = string.Empty;
        public string Impact { get; set; } = string.Empty;
        public string ImpactColor { get; set; } = string.Empty;
        public bool IsEnabled { get; set; }
    }
}
