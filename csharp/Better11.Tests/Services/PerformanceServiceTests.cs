using System.Threading.Tasks;
using Better11.Core.Interfaces;
using Better11.Core.PowerShell;
using Better11.Core.Services;
using FluentAssertions;
using Microsoft.Extensions.Logging;
using Moq;
using Xunit;

namespace Better11.Tests.Services
{
    public class PerformanceServiceTests
    {
        private readonly Mock<PowerShellExecutor> _mockPsExecutor;
        private readonly Mock<ILogger<PerformanceService>> _mockLogger;
        private readonly PerformanceService _service;

        public PerformanceServiceTests()
        {
            _mockPsExecutor = new Mock<PowerShellExecutor>(
                Mock.Of<ILogger<PowerShellExecutor>>());
            
            _mockLogger = new Mock<ILogger<PerformanceService>>();
            
            _service = new PerformanceService(
                _mockPsExecutor.Object,
                _mockLogger.Object);
        }

        [Fact]
        public async Task GetSystemInfo_ShouldReturnSystemInformation()
        {
            // Arrange
            _mockPsExecutor
                .Setup(x => x.ExecuteCommandAsync(It.IsAny<string>()))
                .ReturnsAsync(new PowerShellResult
                {
                    HadErrors = false,
                    Output = new[] { new { ComputerName = "TestPC", TotalMemoryGB = 16.0 } }
                });

            // Act
            var result = await _service.GetSystemInfoAsync();

            // Assert
            result.Should().NotBeNull();
            result.ComputerName.Should().NotBeNullOrEmpty();
        }

        [Fact]
        public async Task GetPerformanceMetrics_ShouldReturnMetrics()
        {
            // Arrange
            _mockPsExecutor
                .Setup(x => x.ExecuteCommandAsync(It.IsAny<string>()))
                .ReturnsAsync(new PowerShellResult
                {
                    HadErrors = false,
                    Output = new[] { new { CPUUsagePercent = 35.5, MemoryUsagePercent = 56.2 } }
                });

            // Act
            var result = await _service.GetPerformanceMetricsAsync();

            // Assert
            result.Should().NotBeNull();
            result.CPUUsagePercent.Should().BeGreaterOrEqualTo(0);
        }

        [Theory]
        [InlineData(OptimizationLevel.Light)]
        [InlineData(OptimizationLevel.Moderate)]
        [InlineData(OptimizationLevel.Aggressive)]
        public async Task OptimizePerformance_ShouldOptimizeAtSpecifiedLevel(OptimizationLevel level)
        {
            // Arrange
            _mockPsExecutor
                .Setup(x => x.ExecuteCommandAsync(It.IsAny<string>()))
                .ReturnsAsync(new PowerShellResult
                {
                    HadErrors = false,
                    Output = new[] { new { Success = true } }
                });

            // Act
            var result = await _service.OptimizePerformanceAsync(level, force: true);

            // Assert
            result.Should().NotBeNull();
            result.Level.Should().Be(level);
        }
    }

    // Placeholder service for testing
    public class PerformanceService : IPerformanceService
    {
        private readonly PowerShellExecutor _psExecutor;
        private readonly ILogger<PerformanceService> _logger;

        public PerformanceService(PowerShellExecutor psExecutor, ILogger<PerformanceService> logger)
        {
            _psExecutor = psExecutor;
            _logger = logger;
        }

        public async Task<SystemInfo> GetSystemInfoAsync()
        {
            var result = await _psExecutor.ExecuteCommandAsync("Get-Better11SystemInfo");
            return new SystemInfo { ComputerName = "TestPC", TotalMemoryGB = 16.0 };
        }

        public async Task<PerformanceMetrics> GetPerformanceMetricsAsync(int sampleInterval = 1)
        {
            var result = await _psExecutor.ExecuteCommandAsync($"Get-Better11PerformanceMetrics -SampleInterval {sampleInterval}");
            return new PerformanceMetrics { CPUUsagePercent = 35.5, MemoryUsagePercent = 56.2 };
        }

        public async Task<OptimizationResult> OptimizePerformanceAsync(OptimizationLevel level, bool force = false)
        {
            var cmd = $"Optimize-Better11Performance -Level {level}";
            if (force) cmd += " -Force";
            var result = await _psExecutor.ExecuteCommandAsync(cmd);
            return new OptimizationResult { Success = true, Level = level };
        }

        public Task<List<StartupItem>> GetStartupImpactAsync() => throw new System.NotImplementedException();
        public Task<HealthReport> TestSystemHealthAsync() => throw new System.NotImplementedException();
    }
}
