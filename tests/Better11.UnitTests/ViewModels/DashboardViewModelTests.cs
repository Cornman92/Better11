using Better11.App.Services;
using Better11.App.ViewModels;
using Better11.Core.Interfaces;
using Better11.Core.Models;
using Microsoft.Extensions.Logging;
using Moq;
using Xunit;

namespace Better11.UnitTests.ViewModels;

/// <summary>
/// Unit tests for <see cref="DashboardViewModel"/>.
/// </summary>
public class DashboardViewModelTests
{
    private readonly Mock<ILogger<DashboardViewModel>> _mockLogger;
    private readonly Mock<INavigationService> _mockNavigationService;
    private readonly Mock<ISecurityService> _mockSecurityService;
    private readonly Mock<IPowerShellEngine> _mockPowerShellEngine;
    private readonly DashboardViewModel _viewModel;

    public DashboardViewModelTests()
    {
        _mockLogger = new Mock<ILogger<DashboardViewModel>>();
        _mockNavigationService = new Mock<INavigationService>();
        _mockSecurityService = new Mock<ISecurityService>();
        _mockPowerShellEngine = new Mock<IPowerShellEngine>();

        _viewModel = new DashboardViewModel(
            _mockLogger.Object,
            _mockNavigationService.Object,
            _mockSecurityService.Object,
            _mockPowerShellEngine.Object);
    }

    [Fact]
    public void Constructor_SetsTitle()
    {
        // Assert
        Assert.Equal("Dashboard", _viewModel.Title);
    }

    [Fact]
    public void Constructor_InitializesProperties()
    {
        // Assert
        Assert.NotNull(_viewModel.WindowsVersion);
        Assert.NotNull(_viewModel.SystemUptime);
        Assert.NotNull(_viewModel.CpuUsage);
        Assert.NotNull(_viewModel.MemoryUsage);
        Assert.NotNull(_viewModel.DiskUsage);
    }

    [Fact]
    public void NavigateToImageEditor_CallsNavigationService()
    {
        // Act
        _viewModel.NavigateToImageEditorCommand.Execute(null);

        // Assert
        _mockNavigationService.Verify(x => x.NavigateTo("ImageEditor", null), Times.Once);
    }

    [Fact]
    public void NavigateToAppManager_CallsNavigationService()
    {
        // Act
        _viewModel.NavigateToAppManagerCommand.Execute(null);

        // Assert
        _mockNavigationService.Verify(x => x.NavigateTo("AppManager", null), Times.Once);
    }

    [Fact]
    public void NavigateToSettings_CallsNavigationService()
    {
        // Act
        _viewModel.NavigateToSettingsCommand.Execute(null);

        // Assert
        _mockNavigationService.Verify(x => x.NavigateTo("Settings", null), Times.Once);
    }

    [Fact]
    public async Task RefreshSystemInfo_CallsSecurityService()
    {
        // Arrange
        _mockSecurityService.Setup(x => x.IsAdministrator()).Returns(true);
        _mockPowerShellEngine.Setup(x => x.ExecuteScriptAsync(It.IsAny<string>(), default))
            .ReturnsAsync(Result<PowerShellResult>.Success(new PowerShellResult { Success = true }));

        // Act
        await _viewModel.RefreshSystemInfoCommand.ExecuteAsync(null);

        // Assert
        _mockSecurityService.Verify(x => x.IsAdministrator(), Times.AtLeastOnce);
    }

    [Fact]
    public async Task RefreshSystemInfo_UpdatesIsAdministrator()
    {
        // Arrange
        _mockSecurityService.Setup(x => x.IsAdministrator()).Returns(true);
        _mockPowerShellEngine.Setup(x => x.ExecuteScriptAsync(It.IsAny<string>(), default))
            .ReturnsAsync(Result<PowerShellResult>.Success(new PowerShellResult { Success = true }));

        // Act
        await _viewModel.RefreshSystemInfoCommand.ExecuteAsync(null);

        // Assert
        Assert.True(_viewModel.IsAdministrator);
    }

    [Fact]
    public async Task RefreshSystemInfo_SetsBusyState()
    {
        // Arrange
        var busyStates = new List<bool>();
        _mockPowerShellEngine.Setup(x => x.ExecuteScriptAsync(It.IsAny<string>(), default))
            .ReturnsAsync(() =>
            {
                busyStates.Add(_viewModel.IsBusy);
                return Result<PowerShellResult>.Success(new PowerShellResult { Success = true });
            });

        // Act
        await _viewModel.RefreshSystemInfoCommand.ExecuteAsync(null);

        // Assert
        Assert.Contains(true, busyStates); // Was busy during execution
        Assert.False(_viewModel.IsBusy); // Not busy after completion
    }

    [Fact]
    public void IsNotBusy_OppositeToBusy()
    {
        // Arrange
        _viewModel.IsBusy = true;

        // Assert
        Assert.False(_viewModel.IsNotBusy);

        // Arrange
        _viewModel.IsBusy = false;

        // Assert
        Assert.True(_viewModel.IsNotBusy);
    }
}
