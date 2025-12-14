using System;
using System.Text.Json;
using Better11.Core.Models;
using Xunit;

namespace Better11.Tests.Models
{
    public class AppModelsTests
    {
        [Fact]
        public void AppMetadata_IsDomainVetted_ReturnsTrueForVettedDomain()
        {
            // Arrange
            var app = new AppMetadata
            {
                AppId = "test-app",
                VettedDomains = { "example.com", "trusted.org" }
            };

            // Act & Assert
            Assert.True(app.IsDomainVetted("example.com"));
            Assert.True(app.IsDomainVetted("EXAMPLE.COM"));
            Assert.True(app.IsDomainVetted("trusted.org"));
        }

        [Fact]
        public void AppMetadata_IsDomainVetted_ReturnsFalseForUnvettedDomain()
        {
            // Arrange
            var app = new AppMetadata
            {
                AppId = "test-app",
                VettedDomains = { "example.com" }
            };

            // Act & Assert
            Assert.False(app.IsDomainVetted("malicious.com"));
            Assert.False(app.IsDomainVetted("example.org"));
        }

        [Fact]
        public void AppMetadata_RequiresSignatureVerification_ReturnsTrueWhenBothPresent()
        {
            // Arrange
            var app = new AppMetadata
            {
                AppId = "test-app",
                Signature = "abc123",
                SignatureKey = "key123"
            };

            // Act & Assert
            Assert.True(app.RequiresSignatureVerification);
        }

        [Fact]
        public void AppMetadata_RequiresSignatureVerification_ReturnsFalseWhenMissing()
        {
            // Arrange
            var appNoSig = new AppMetadata { AppId = "test-app", SignatureKey = "key123" };
            var appNoKey = new AppMetadata { AppId = "test-app", Signature = "abc123" };
            var appNeither = new AppMetadata { AppId = "test-app" };

            // Act & Assert
            Assert.False(appNoSig.RequiresSignatureVerification);
            Assert.False(appNoKey.RequiresSignatureVerification);
            Assert.False(appNeither.RequiresSignatureVerification);
        }

        [Fact]
        public void AppMetadata_CanDeserializeFromJson()
        {
            // Arrange
            var json = @"{
                ""app_id"": ""demo-exe"",
                ""name"": ""Demo Utility"",
                ""version"": ""1.0.0"",
                ""uri"": ""samples/demo-app.exe"",
                ""sha256"": ""abc123"",
                ""installer_type"": ""exe"",
                ""vetted_domains"": [""example.com""],
                ""dependencies"": [""dep1"", ""dep2""],
                ""silent_args"": [""/S""]
            }";

            // Act
            var app = JsonSerializer.Deserialize<AppMetadata>(json, new JsonSerializerOptions
            {
                PropertyNameCaseInsensitive = true
            });

            // Assert
            Assert.NotNull(app);
            Assert.Equal("demo-exe", app!.AppId);
            Assert.Equal("Demo Utility", app.Name);
            Assert.Equal("1.0.0", app.Version);
            Assert.Equal(InstallerType.EXE, app.InstallerType);
            Assert.Single(app.VettedDomains);
            Assert.Equal(2, app.Dependencies.Count);
            Assert.Single(app.SilentArgs);
        }

        [Fact]
        public void InstallerResult_Success_IsBasedOnExitCode()
        {
            // Arrange
            var successResult = new InstallerResult { ExitCode = 0 };
            var failResult = new InstallerResult { ExitCode = 1 };

            // Act & Assert
            Assert.True(successResult.Success);
            Assert.False(failResult.Success);
        }
    }
}
