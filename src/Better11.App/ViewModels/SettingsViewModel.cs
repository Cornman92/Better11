using Better11.Core.Interfaces;
using CommunityToolkit.Mvvm.Input;
using Microsoft.Extensions.Logging;
using Microsoft.UI.Xaml;

namespace Better11.App.ViewModels;

/// <summary>
/// ViewModel for the Settings view.
/// </summary>
public partial class SettingsViewModel : ViewModelBase
{
    private readonly ILogger<SettingsViewModel> _logger;
    private readonly IConfigurationService _configurationService;

    private ElementTheme _selectedTheme;
    private string _selectedLanguage = "en-US";
    private bool _checkForUpdates;
    private bool _startWithWindows;
    private string _downloadsPath = string.Empty;
    private string _logsPath = string.Empty;

    /// <summary>
    /// Initializes a new instance of the <see cref="SettingsViewModel"/> class.
    /// </summary>
    public SettingsViewModel(
        ILogger<SettingsViewModel> logger,
        IConfigurationService configurationService)
    {
        _logger = logger;
        _configurationService = configurationService;

        Title = "Settings";

        // Load settings
        LoadSettings();
    }

    /// <summary>
    /// Gets or sets the selected theme.
    /// </summary>
    public ElementTheme SelectedTheme
    {
        get => _selectedTheme;
        set
        {
            if (SetProperty(ref _selectedTheme, value))
            {
                _ = ApplyThemeAsync(value);
            }
        }
    }

    /// <summary>
    /// Gets or sets the selected language.
    /// </summary>
    public string SelectedLanguage
    {
        get => _selectedLanguage;
        set => SetProperty(ref _selectedLanguage, value);
    }

    /// <summary>
    /// Gets or sets a value indicating whether to check for updates.
    /// </summary>
    public bool CheckForUpdates
    {
        get => _checkForUpdates;
        set => SetProperty(ref _checkForUpdates, value);
    }

    /// <summary>
    /// Gets or sets a value indicating whether to start with Windows.
    /// </summary>
    public bool StartWithWindows
    {
        get => _startWithWindows;
        set => SetProperty(ref _startWithWindows, value);
    }

    /// <summary>
    /// Gets or sets the downloads path.
    /// </summary>
    public string DownloadsPath
    {
        get => _downloadsPath;
        set => SetProperty(ref _downloadsPath, value);
    }

    /// <summary>
    /// Gets or sets the logs path.
    /// </summary>
    public string LogsPath
    {
        get => _logsPath;
        set => SetProperty(ref _logsPath, value);
    }

    /// <summary>
    /// Saves the settings.
    /// </summary>
    [RelayCommand]
    private async Task SaveSettingsAsync()
    {
        IsBusy = true;
        try
        {
            _logger.LogInformation("Saving settings");

            _configurationService.SetValue("App.Theme", SelectedTheme.ToString());
            _configurationService.SetValue("App.Language", SelectedLanguage);
            _configurationService.SetValue("App.CheckForUpdates", CheckForUpdates);
            _configurationService.SetValue("App.StartWithWindows", StartWithWindows);
            _configurationService.SetValue("Paths.Downloads", DownloadsPath);
            _configurationService.SetValue("Paths.Logs", LogsPath);

            await _configurationService.SaveAsync();

            _logger.LogInformation("Settings saved successfully");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error saving settings");
        }
        finally
        {
            IsBusy = false;
        }
    }

    /// <summary>
    /// Resets settings to defaults.
    /// </summary>
    [RelayCommand]
    private async Task ResetSettingsAsync()
    {
        _logger.LogInformation("Resetting settings to defaults");

        SelectedTheme = ElementTheme.Default;
        SelectedLanguage = "en-US";
        CheckForUpdates = true;
        StartWithWindows = false;

        DownloadsPath = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.UserProfile),
            "Downloads", "Better11");

        LogsPath = Path.Combine(
            Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
            "Better11", "Logs");

        await SaveSettingsAsync();
    }

    private void LoadSettings()
    {
        _logger.LogDebug("Loading settings");

        // Load theme
        var themeString = _configurationService.GetValue("App.Theme", "Default");
        SelectedTheme = Enum.TryParse<ElementTheme>(themeString, out var theme) ? theme : ElementTheme.Default;

        // Load other settings
        SelectedLanguage = _configurationService.GetValue("App.Language", "en-US");
        CheckForUpdates = _configurationService.GetValue("App.CheckForUpdates", true);
        StartWithWindows = _configurationService.GetValue("App.StartWithWindows", false);

        DownloadsPath = _configurationService.GetValue("Paths.Downloads",
            Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), "Downloads", "Better11"));

        LogsPath = _configurationService.GetValue("Paths.Logs",
            Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "Better11", "Logs"));

        _logger.LogDebug("Settings loaded successfully");
    }

    private async Task ApplyThemeAsync(ElementTheme theme)
    {
        try
        {
            _logger.LogInformation("Applying theme: {Theme}", theme);

            // Get the main window
            if (App.Current.Services.GetService(typeof(MainWindow)) is MainWindow window)
            {
                if (window.Content is FrameworkElement rootElement)
                {
                    rootElement.RequestedTheme = theme;
                }
            }

            await Task.CompletedTask;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error applying theme");
        }
    }
}
