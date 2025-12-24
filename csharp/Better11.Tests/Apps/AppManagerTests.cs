using Better11.Core.Apps;
using Better11.Core.Apps.Models;
using FluentAssertions;
using Microsoft.Extensions.Logging;
using Moq;
using System.Text.Json;
using Xunit;

namespace Better11.Tests.Apps
{
    public class AppManagerTests : IDisposable
    {
        private readonly string _testDir;
        private readonly string _catalogPath;
        private readonly string _downloadDir;
        private readonly string _stateFile;
        private readonly Mock<ILogger<AppManager>> _mockLogger;

        public AppManagerTests()
        {
            _testDir = Path.Combine(Path.GetTempPath(), $"better11_test_{Guid.NewGuid()}");
            Directory.CreateDirectory(_testDir);

            _catalogPath = Path.Combine(_testDir, "catalog.json");
            _downloadDir = Path.Combine(_testDir, "downloads");
            _stateFile = Path.Combine(_testDir, "installed.json");
            _mockLogger = new Mock<ILogger<AppManager>>();
        }

        public void Dispose()
        {
            if (Directory.Exists(_testDir))
            {
                Directory.Delete(_testDir, true);
            }
        }

        [Fact]
        public void BuildInstallPlan_WithSimpleApp_ReturnsCorrectPlan()
        {
            // Arrange
            var catalog = new AppCatalog
            {
                Applications = new List<AppMetadata>
                {
                    new AppMetadata
                    {
                        AppId = "simple-app",
                        Name = "Simple App",
                        Version = "1.0.0",
                        Uri = "https://example.com/simple.exe",
                        Sha256 = "abc123",
                        InstallerType = InstallerType.EXE,
                        Dependencies = new List<string>()
                    }
                }
            };
            CreateCatalogFile(catalog);
            var manager = new AppManager(_catalogPath, _downloadDir, _stateFile, logger: _mockLogger.Object);

            // Act
            var plan = manager.BuildInstallPlan("simple-app");

            // Assert
            plan.Should().NotBeNull();
            plan.TargetAppId.Should().Be("simple-app");
            plan.Steps.Should().HaveCount(1);
            plan.Steps[0].AppId.Should().Be("simple-app");
            plan.Steps[0].Action.Should().Be("install");
            plan.Steps[0].Installed.Should().BeFalse();
            plan.Warnings.Should().BeEmpty();
        }

        [Fact]
        public void BuildInstallPlan_WithDependencies_ReturnsOrderedPlan()
        {
            // Arrange
            var catalog = new AppCatalog
            {
                Applications = new List<AppMetadata>
                {
                    new AppMetadata
                    {
                        AppId = "app-a",
                        Name = "App A",
                        Version = "1.0.0",
                        Uri = "https://example.com/a.exe",
                        Sha256 = "abc123",
                        InstallerType = InstallerType.EXE,
                        Dependencies = new List<string> { "app-b", "app-c" }
                    },
                    new AppMetadata
                    {
                        AppId = "app-b",
                        Name = "App B",
                        Version = "1.0.0",
                        Uri = "https://example.com/b.exe",
                        Sha256 = "def456",
                        InstallerType = InstallerType.EXE,
                        Dependencies = new List<string> { "app-c" }
                    },
                    new AppMetadata
                    {
                        AppId = "app-c",
                        Name = "App C",
                        Version = "1.0.0",
                        Uri = "https://example.com/c.exe",
                        Sha256 = "ghi789",
                        InstallerType = InstallerType.EXE,
                        Dependencies = new List<string>()
                    }
                }
            };
            CreateCatalogFile(catalog);
            var manager = new AppManager(_catalogPath, _downloadDir, _stateFile, logger: _mockLogger.Object);

            // Act
            var plan = manager.BuildInstallPlan("app-a");

            // Assert
            plan.Should().NotBeNull();
            plan.Steps.Should().HaveCount(3);
            // Dependencies should come before dependents (leaf -> root)
            plan.Steps[0].AppId.Should().Be("app-c");
            plan.Steps[1].AppId.Should().Be("app-b");
            plan.Steps[2].AppId.Should().Be("app-a");
            plan.Warnings.Should().BeEmpty();
        }

        [Fact]
        public void BuildInstallPlan_WithInstalledApp_MarkasSkip()
        {
            // Arrange
            var catalog = new AppCatalog
            {
                Applications = new List<AppMetadata>
                {
                    new AppMetadata
                    {
                        AppId = "installed-app",
                        Name = "Installed App",
                        Version = "1.0.0",
                        Uri = "https://example.com/app.exe",
                        Sha256 = "abc123",
                        InstallerType = InstallerType.EXE,
                        Dependencies = new List<string>()
                    }
                }
            };
            CreateCatalogFile(catalog);

            // Mark app as installed
            var state = new List<AppStatus>
            {
                new AppStatus
                {
                    AppId = "installed-app",
                    Version = "1.0.0",
                    Installed = true,
                    InstallerPath = "/path/to/installer.exe",
                    InstallDate = DateTime.UtcNow
                }
            };
            File.WriteAllText(_stateFile, JsonSerializer.Serialize(state));

            var manager = new AppManager(_catalogPath, _downloadDir, _stateFile, logger: _mockLogger.Object);

            // Act
            var plan = manager.BuildInstallPlan("installed-app");

            // Assert
            plan.Should().NotBeNull();
            plan.Steps.Should().HaveCount(1);
            plan.Steps[0].Action.Should().Be("skip");
            plan.Steps[0].Installed.Should().BeTrue();
        }

        [Fact]
        public void BuildInstallPlan_WithCircularDependency_ReturnsWarning()
        {
            // Arrange
            var catalog = new AppCatalog
            {
                Applications = new List<AppMetadata>
                {
                    new AppMetadata
                    {
                        AppId = "app-a",
                        Name = "App A",
                        Version = "1.0.0",
                        Uri = "https://example.com/a.exe",
                        Sha256 = "abc123",
                        InstallerType = InstallerType.EXE,
                        Dependencies = new List<string> { "app-b" }
                    },
                    new AppMetadata
                    {
                        AppId = "app-b",
                        Name = "App B",
                        Version = "1.0.0",
                        Uri = "https://example.com/b.exe",
                        Sha256 = "def456",
                        InstallerType = InstallerType.EXE,
                        Dependencies = new List<string> { "app-a" }
                    }
                }
            };
            CreateCatalogFile(catalog);
            var manager = new AppManager(_catalogPath, _downloadDir, _stateFile, logger: _mockLogger.Object);

            // Act
            var plan = manager.BuildInstallPlan("app-a");

            // Assert
            plan.Should().NotBeNull();
            plan.Warnings.Should().ContainMatch("*Circular dependency*");
            plan.HasBlockedSteps().Should().BeTrue();
            plan.Steps.Should().Contain(s => s.Action == "blocked");
        }

        [Fact]
        public void BuildInstallPlan_WithMissingDependency_ReturnsWarning()
        {
            // Arrange
            var catalog = new AppCatalog
            {
                Applications = new List<AppMetadata>
                {
                    new AppMetadata
                    {
                        AppId = "app-with-missing-dep",
                        Name = "App With Missing Dep",
                        Version = "1.0.0",
                        Uri = "https://example.com/app.exe",
                        Sha256 = "abc123",
                        InstallerType = InstallerType.EXE,
                        Dependencies = new List<string> { "missing-dep" }
                    }
                }
            };
            CreateCatalogFile(catalog);
            var manager = new AppManager(_catalogPath, _downloadDir, _stateFile, logger: _mockLogger.Object);

            // Act
            var plan = manager.BuildInstallPlan("app-with-missing-dep");

            // Assert
            plan.Should().NotBeNull();
            plan.Warnings.Should().ContainMatch("*Missing catalog entry*missing-dep*");
            plan.HasBlockedSteps().Should().BeTrue();
            plan.Steps.Should().Contain(s => s.AppId == "missing-dep" && s.Action == "blocked");
            plan.Steps.Should().Contain(s => s.AppId == "app-with-missing-dep" && s.Action == "blocked");
        }

        [Fact]
        public void BuildInstallPlan_InstallCount_ReturnsCorrectCount()
        {
            // Arrange
            var catalog = new AppCatalog
            {
                Applications = new List<AppMetadata>
                {
                    new AppMetadata
                    {
                        AppId = "app-a",
                        Name = "App A",
                        Version = "1.0.0",
                        Uri = "https://example.com/a.exe",
                        Sha256 = "abc123",
                        InstallerType = InstallerType.EXE,
                        Dependencies = new List<string> { "app-b" }
                    },
                    new AppMetadata
                    {
                        AppId = "app-b",
                        Name = "App B",
                        Version = "1.0.0",
                        Uri = "https://example.com/b.exe",
                        Sha256 = "def456",
                        InstallerType = InstallerType.EXE,
                        Dependencies = new List<string>()
                    }
                }
            };
            CreateCatalogFile(catalog);
            var manager = new AppManager(_catalogPath, _downloadDir, _stateFile, logger: _mockLogger.Object);

            // Act
            var plan = manager.BuildInstallPlan("app-a");

            // Assert
            plan.InstallCount().Should().Be(2);
            plan.SkipCount().Should().Be(0);
        }

        [Fact]
        public async Task DownloadWithCacheAsync_FileNotCached_DownloadsFile()
        {
            // Arrange
            var catalog = new AppCatalog
            {
                Applications = new List<AppMetadata>
                {
                    new AppMetadata
                    {
                        AppId = "test-app",
                        Name = "Test App",
                        Version = "1.0.0",
                        Uri = Path.Combine(_testDir, "test.exe"),
                        Sha256 = await CreateTestFileAndGetHash("test.exe"),
                        InstallerType = InstallerType.EXE,
                        Dependencies = new List<string>()
                    }
                }
            };
            CreateCatalogFile(catalog);
            var manager = new AppManager(_catalogPath, _downloadDir, _stateFile, logger: _mockLogger.Object);

            // Act
            var (path, cacheHit) = await manager.DownloadWithCacheAsync("test-app");

            // Assert
            cacheHit.Should().BeFalse();
            File.Exists(path).Should().BeTrue();
        }

        [Fact]
        public async Task DownloadWithCacheAsync_FileAlreadyCached_UsesCachedFile()
        {
            // Arrange
            var testFileHash = await CreateTestFileAndGetHash("test.exe");
            var catalog = new AppCatalog
            {
                Applications = new List<AppMetadata>
                {
                    new AppMetadata
                    {
                        AppId = "test-app",
                        Name = "Test App",
                        Version = "1.0.0",
                        Uri = Path.Combine(_testDir, "test.exe"),
                        Sha256 = testFileHash,
                        InstallerType = InstallerType.EXE,
                        Dependencies = new List<string>()
                    }
                }
            };
            CreateCatalogFile(catalog);
            var manager = new AppManager(_catalogPath, _downloadDir, _stateFile, logger: _mockLogger.Object);

            // First download to cache
            await manager.DownloadWithCacheAsync("test-app");

            // Act - Second download should hit cache
            var (path, cacheHit) = await manager.DownloadWithCacheAsync("test-app");

            // Assert
            cacheHit.Should().BeTrue();
            File.Exists(path).Should().BeTrue();
        }

        [Fact]
        public async Task DownloadWithCacheAsync_CachedFileCorrupted_RedownloadsFile()
        {
            // Arrange
            var testFileHash = await CreateTestFileAndGetHash("test.exe");
            var catalog = new AppCatalog
            {
                Applications = new List<AppMetadata>
                {
                    new AppMetadata
                    {
                        AppId = "test-app",
                        Name = "Test App",
                        Version = "1.0.0",
                        Uri = Path.Combine(_testDir, "test.exe"),
                        Sha256 = testFileHash,
                        InstallerType = InstallerType.EXE,
                        Dependencies = new List<string>()
                    }
                }
            };
            CreateCatalogFile(catalog);
            var manager = new AppManager(_catalogPath, _downloadDir, _stateFile, logger: _mockLogger.Object);

            // First download to cache
            var (firstPath, _) = await manager.DownloadWithCacheAsync("test-app");

            // Corrupt the cached file
            await File.WriteAllTextAsync(firstPath, "corrupted content");

            // Act - Should detect corruption and redownload
            var (path, cacheHit) = await manager.DownloadWithCacheAsync("test-app");

            // Assert
            cacheHit.Should().BeFalse();
            File.Exists(path).Should().BeTrue();
            // Verify file is not corrupted
            var verifier = new DownloadVerifier();
            await verifier.VerifyHashAsync(path, testFileHash);
        }

        private void CreateCatalogFile(AppCatalog catalog)
        {
            var json = JsonSerializer.Serialize(catalog, new JsonSerializerOptions
            {
                WriteIndented = true
            });
            File.WriteAllText(_catalogPath, json);
        }

        private async Task<string> CreateTestFileAndGetHash(string fileName)
        {
            var filePath = Path.Combine(_testDir, fileName);
            var content = $"Test file content for {fileName}";
            await File.WriteAllTextAsync(filePath, content);

            using var stream = File.OpenRead(filePath);
            using var sha256 = System.Security.Cryptography.SHA256.Create();
            var hashBytes = await sha256.ComputeHashAsync(stream);
            return Convert.ToHexString(hashBytes).ToLowerInvariant();
        }
    }
}
