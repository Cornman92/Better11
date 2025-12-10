using Better11.App.ViewModels;
using Better11.Core.Interfaces;
using Microsoft.Extensions.Logging;
using Microsoft.UI.Xaml;
using Moq;
using Xunit;

namespace Better11.UnitTests.ViewModels;

/// <summary>
/// Unit tests for <see cref="SettingsViewModel"/>.
/// </summary>
public class SettingsViewModelTests
{
    private readonly Mock<ILogger<SettingsViewModel>> _mockLogger;
    private readonly Mock<IConfigurationService> _mockConfigService;
    private readonly SettingsViewModel _viewModel;

    public SettingsViewModelTests()
    {
        _mockLogger = new Mock<ILogger<SettingsViewModel>>();
        _mockConfigService = new Mock<IConfigurationService>();

        _viewModel = new SettingsViewModel(
            _mockLogger.Object,
            _mockConfigService.Object);
    }

    [Fact]
    public void Constructor_SetsTitle()
    {
        // Assert
        Assert.Equal("Settings", _viewModel.Title);
    }

    [Fact]
    public void Constructor_InitializesProperties()
    {
        // Assert
        Assert.NotNull(_viewModel.SelectedLanguage);
        Assert.NotNull(_viewModel.DownloadsPath);
        Assert.NotNull(_viewModel.LogsPath);
    }

    [Fact]
    public async Task InitializeAsync_LoadsConfiguration()
    {
        // Arrange
        _mockConfigService.Setup(x => x.GetValue("App.Theme", It.IsAny<string>()))
            .Returns("Dark");
        _mockConfigService.Setup(x => x.GetValue("App.Language", It.IsAny<string>()))
            .Returns("fr-FR");
        _mockConfigService.Setup(x => x.GetValue("App.CheckForUpdates", It.IsAny<bool>()))
            .Returns(false);

        // Act
        await _viewModel.InitializeAsync();

        // Assert
        _mockConfigService.Verify(x => x.GetValue("App.Theme", It.IsAny<string>()), Times.Once);
        _mockConfigService.Verify(x => x.GetValue("App.Language", It.IsAny<string>()), Times.Once);
        _mockConfigService.Verify(x => x.GetValue("App.CheckForUpdates", It.IsAny<bool>()), Times.Once);
    }

    [Fact]
    public async Task SaveSettingsAsync_CallsConfigurationService()
    {
        // Arrange
        _viewModel.SelectedLanguage = "de-DE";
        _viewModel.CheckForUpdates = true;

        // Act
        await _viewModel.SaveSettingsCommand.ExecuteAsync(null);

        // Assert
        _mockConfigService.Verify(x => x.SetValue("App.Language", "de-DE"), Times.Once);
        _mockConfigService.Verify(x => x.SetValue("App.CheckForUpdates", true), Times.Once);
        _mockConfigService.Verify(x => x.SaveAsync(), Times.Once);
    }

    [Fact]
    public async Task SaveSettingsAsync_SetsBusyState()
    {
        // Arrange
        var busyStates = new List<bool>();
        _mockConfigService.Setup(x => x.SaveAsync())
            .Returns(() =>
            {
                busyStates.Add(_viewModel.IsBusy);
                return Task.CompletedTask;
            });

        // Act
        await _viewModel.SaveSettingsCommand.ExecuteAsync(null);

        // Assert
        Assert.Contains(true, busyStates); // Was busy during save
        Assert.False(_viewModel.IsBusy); // Not busy after completion
    }

    [Fact]
    public async Task ResetSettingsAsync_ResetsToDefaults()
    {
        // Arrange
        _viewModel.SelectedLanguage = "de-DE";
        _viewModel.CheckForUpdates = false;
        _viewModel.StartWithWindows = true;

        // Act
        await _viewModel.ResetSettingsCommand.ExecuteAsync(null);

        // Assert
        Assert.Equal("en-US", _viewModel.SelectedLanguage);
        Assert.True(_viewModel.CheckForUpdates);
        Assert.False(_viewModel.StartWithWindows);
    }

    [Fact]
    public async Task ResetSettingsAsync_CallsSaveSettings()
    {
        // Act
        await _viewModel.ResetSettingsCommand.ExecuteAsync(null);

        // Assert
        _mockConfigService.Verify(x => x.SaveAsync(), Times.Once);
    }

    [Fact]
    public void SelectedTheme_PropertyChange_TriggersNotification()
    {
        // Arrange
        var propertyChanged = false;
        _viewModel.PropertyChanged += (s, e) =>
        {
            if (e.PropertyName == nameof(SettingsViewModel.SelectedTheme))
            {
                propertyChanged = true;
            }
        };

        // Act
        _viewModel.SelectedTheme = ElementTheme.Dark;

        // Assert
        Assert.True(propertyChanged);
    }

    [Fact]
    public void SelectedLanguage_PropertyChange_TriggersNotification()
    {
        // Arrange
        var propertyChanged = false;
        _viewModel.PropertyChanged += (s, e) =>
        {
            if (e.PropertyName == nameof(SettingsViewModel.SelectedLanguage))
            {
                propertyChanged = true;
            }
        };

        // Act
        _viewModel.SelectedLanguage = "es-ES";

        // Assert
        Assert.True(propertyChanged);
    }

    [Fact]
    public void CheckForUpdates_PropertyChange_TriggersNotification()
    {
        // Arrange
        var propertyChanged = false;
        _viewModel.PropertyChanged += (s, e) =>
        {
            if (e.PropertyName == nameof(SettingsViewModel.CheckForUpdates))
            {
                propertyChanged = true;
            }
        };

        // Act
        _viewModel.CheckForUpdates = true;

        // Assert
        Assert.True(propertyChanged);
    }
}
