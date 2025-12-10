using Better11.Core.Models;
using Better11.Core.PowerShell;
using Better11.Core.Services;
using FluentAssertions;
using Microsoft.Extensions.Logging;
using Moq;
using Xunit;

namespace Better11.Tests.Services
{
    public class AppManagerServiceTests
    {
        private readonly Mock<PowerShellExecutor> _mockPsExecutor;
        private readonly Mock<ILogger<AppManagerService>> _mockLogger;
        private readonly AppManagerService _service;

        public AppManagerServiceTests()
        {
            _mockPsExecutor = new Mock<PowerShellExecutor>(Mock.Of<ILogger<PowerShellExecutor>>());
            _mockLogger = new Mock<ILogger<AppManagerService>>();
            _service = new AppManagerService(_mockPsExecutor.Object, _mockLogger.Object);
        }

        [Fact]
        public async Task ListAvailableAppsAsync_ShouldReturnApps_WhenSuccessful()
        {
            // Arrange
            var psResult = new PSExecutionResult
            {
                Success = true,
                Output = new List<object>
                {
                    CreatePSObject("vscode", "Visual Studio Code", "1.85.0")
                }
            };

            _mockPsExecutor
                .Setup(x => x.ExecuteCommandAsync("Get-Better11Apps", null))
                .ReturnsAsync(psResult);

            // Act
            var apps = await _service.ListAvailableAppsAsync();

            // Assert
            apps.Should().NotBeNull();
            apps.Should().HaveCount(1);
            apps[0].AppId.Should().Be("vscode");
        }

        [Fact]
        public async Task InstallAppAsync_ShouldReturnSuccess_WhenInstallSucceeds()
        {
            // Arrange
            var psResult = new PSExecutionResult
            {
                Success = true,
                Output = new List<object>
                {
                    CreateInstallResultPSObject(true, "vscode", "1.85.0", "Success")
                }
            };

            _mockPsExecutor
                .Setup(x => x.ExecuteCommandAsync("Install-Better11App", It.IsAny<Dictionary<string, object>>()))
                .ReturnsAsync(psResult);

            // Act
            var result = await _service.InstallAppAsync("vscode");

            // Assert
            result.Should().NotBeNull();
            result.Success.Should().BeTrue();
            result.AppId.Should().Be("vscode");
        }

        private static System.Management.Automation.PSObject CreatePSObject(string appId, string name, string version)
        {
            var psObj = new System.Management.Automation.PSObject();
            psObj.Properties.Add(new System.Management.Automation.PSNoteProperty("AppId", appId));
            psObj.Properties.Add(new System.Management.Automation.PSNoteProperty("Name", name));
            psObj.Properties.Add(new System.Management.Automation.PSNoteProperty("Version", version));
            psObj.Properties.Add(new System.Management.Automation.PSNoteProperty("InstallerType", "exe"));
            psObj.Properties.Add(new System.Management.Automation.PSNoteProperty("Description", "Test app"));
            return psObj;
        }

        private static System.Management.Automation.PSObject CreateInstallResultPSObject(
            bool success, string appId, string version, string status)
        {
            var psObj = new System.Management.Automation.PSObject();
            psObj.Properties.Add(new System.Management.Automation.PSNoteProperty("Success", success));
            psObj.Properties.Add(new System.Management.Automation.PSNoteProperty("AppId", appId));
            psObj.Properties.Add(new System.Management.Automation.PSNoteProperty("Version", version));
            psObj.Properties.Add(new System.Management.Automation.PSNoteProperty("Status", status));
            return psObj;
        }
    }
}
