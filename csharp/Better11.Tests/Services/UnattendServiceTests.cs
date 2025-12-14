using System;
using System.IO;
using System.Threading.Tasks;
using Better11.Core.Models;
using Better11.Core.Services;
using Microsoft.Extensions.Logging;
using Moq;
using Xunit;

namespace Better11.Tests.Services
{
    public class UnattendServiceTests
    {
        private readonly Mock<ILogger<UnattendService>> _loggerMock;
        private readonly UnattendService _service;

        public UnattendServiceTests()
        {
            _loggerMock = new Mock<ILogger<UnattendService>>();
            _service = new UnattendService(_loggerMock.Object);
        }

        [Fact]
        public void CreateWorkstationTemplate_ReturnsValidConfiguration()
        {
            // Arrange
            var productKey = "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX";
            var adminUser = "TestAdmin";

            // Act
            var config = _service.CreateWorkstationTemplate(productKey, adminUser);

            // Assert
            Assert.Equal(productKey, config.ProductKey);
            Assert.Single(config.Accounts);
            Assert.Equal(adminUser, config.Accounts[0].Name);
            Assert.True(config.Accounts[0].AutoLogon);
            Assert.NotEmpty(config.FirstLogonCommands);
        }

        [Fact]
        public void CreateLabTemplate_ReturnsValidConfiguration()
        {
            // Arrange
            var productKey = "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX";

            // Act
            var config = _service.CreateLabTemplate(productKey);

            // Assert
            Assert.Equal(productKey, config.ProductKey);
            Assert.Equal("UTC", config.TimeZone);
            Assert.Single(config.Accounts);
            Assert.Equal("LabAdmin", config.Accounts[0].Name);
        }

        [Fact]
        public void ValidateConfiguration_ReturnsNull_ForValidConfig()
        {
            // Arrange
            var config = new UnattendConfiguration
            {
                ProductKey = "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX",
                Language = "en-US",
                TimeZone = "Pacific Standard Time",
                Accounts = { new LocalAccount("Admin", "Password123", false) }
            };

            // Act
            var result = _service.ValidateConfiguration(config);

            // Assert
            Assert.Null(result);
        }

        [Fact]
        public void ValidateConfiguration_ReturnsError_WhenProductKeyMissing()
        {
            // Arrange
            var config = new UnattendConfiguration
            {
                Language = "en-US",
                TimeZone = "Pacific Standard Time",
                Accounts = { new LocalAccount("Admin", "Password123", false) }
            };

            // Act
            var result = _service.ValidateConfiguration(config);

            // Assert
            Assert.NotNull(result);
            Assert.Contains("Product key", result);
        }

        [Fact]
        public void ValidateConfiguration_ReturnsError_WhenNoAccounts()
        {
            // Arrange
            var config = new UnattendConfiguration
            {
                ProductKey = "XXXXX-XXXXX-XXXXX-XXXXX-XXXXX",
                Language = "en-US",
                TimeZone = "Pacific Standard Time"
            };

            // Act
            var result = _service.ValidateConfiguration(config);

            // Assert
            Assert.NotNull(result);
            Assert.Contains("account", result.ToLower());
        }

        [Fact]
        public async Task GenerateUnattendAsync_CreatesFile()
        {
            // Arrange
            var config = _service.CreateWorkstationTemplate("XXXXX-XXXXX-XXXXX-XXXXX-XXXXX");
            var outputPath = Path.Combine(Path.GetTempPath(), $"unattend_test_{Guid.NewGuid()}.xml");

            try
            {
                // Act
                var result = await _service.GenerateUnattendAsync(config, outputPath);

                // Assert
                Assert.Equal(outputPath, result);
                Assert.True(File.Exists(outputPath));

                var content = await File.ReadAllTextAsync(outputPath);
                Assert.Contains("unattend", content);
                Assert.Contains("windowsPE", content);
                Assert.Contains("specialize", content);
                Assert.Contains("oobeSystem", content);
            }
            finally
            {
                if (File.Exists(outputPath))
                {
                    File.Delete(outputPath);
                }
            }
        }
    }
}
