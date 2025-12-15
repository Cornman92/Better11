using Better11.Core.Interfaces;
using Better11.Services;
using Microsoft.Extensions.Logging;
using Moq;
using Xunit;

namespace Better11.UnitTests.Services;

/// <summary>
/// Unit tests for <see cref="ProcessService"/>.
/// </summary>
public class ProcessServiceTests
{
    private readonly Mock<ILogger<ProcessService>> _mockLogger;
    private readonly IProcessService _service;

    public ProcessServiceTests()
    {
        _mockLogger = new Mock<ILogger<ProcessService>>();
        _service = new ProcessService(_mockLogger.Object);
    }

    [Fact]
    public async Task ExecuteAsync_ValidCommand_Success()
    {
        // Arrange
        var command = OperatingSystem.IsWindows() ? "cmd.exe" : "echo";
        var args = OperatingSystem.IsWindows() ? "/c echo test" : "test";

        // Act
        var result = await _service.ExecuteAsync(command, args);

        // Assert
        Assert.True(result.IsSuccess);
        Assert.NotNull(result.Value);
        Assert.Equal(0, result.Value.ExitCode);
        Assert.True(result.Value.Success);
    }

    [Fact]
    public async Task ExecuteAsync_InvalidCommand_Failure()
    {
        // Arrange
        var command = "nonexistentcommand12345";
        var args = "someargs";

        // Act
        var result = await _service.ExecuteAsync(command, args);

        // Assert
        Assert.True(result.IsFailure);
        Assert.NotNull(result.Error);
    }

    [Fact]
    public async Task ExecuteAsync_CapturesStandardOutput()
    {
        // Arrange
        var command = OperatingSystem.IsWindows() ? "cmd.exe" : "echo";
        var testMessage = "test output";
        var args = OperatingSystem.IsWindows() ? $"/c echo {testMessage}" : testMessage;

        // Act
        var result = await _service.ExecuteAsync(command, args);

        // Assert
        Assert.True(result.IsSuccess);
        Assert.Contains(testMessage, result.Value!.StandardOutput);
    }

    [Fact]
    public async Task ExecuteAsync_WithCancellation_ThrowsOperationCanceledException()
    {
        // Arrange
        var cts = new CancellationTokenSource();
        cts.Cancel();

        var command = OperatingSystem.IsWindows() ? "cmd.exe" : "sleep";
        var args = OperatingSystem.IsWindows() ? "/c timeout 10" : "10";

        // Act & Assert
        await Assert.ThrowsAsync<OperationCanceledException>(async () =>
        {
            await _service.ExecuteAsync(command, args, cts.Token);
        });
    }

    [Fact]
    public void StartProcess_ValidCommand_ReturnsProcessId()
    {
        // Arrange
        var command = OperatingSystem.IsWindows() ? "notepad.exe" : "sleep";
        var args = OperatingSystem.IsWindows() ? "" : "1";

        // Act
        var result = _service.StartProcess(command, args);

        // Assert
        Assert.True(result.IsSuccess);
        Assert.True(result.Value > 0);

        // Cleanup - kill the process
        if (result.IsSuccess)
        {
            try
            {
                _service.KillProcess(result.Value);
            }
            catch
            {
                // Process may have already exited
            }
        }
    }

    [Fact]
    public void IsProcessRunning_RunningProcess_ReturnsTrue()
    {
        // Arrange
        var currentProcessId = Environment.ProcessId;

        // Act
        var result = _service.IsProcessRunning(currentProcessId);

        // Assert
        Assert.True(result);
    }

    [Fact]
    public void IsProcessRunning_NonExistentProcess_ReturnsFalse()
    {
        // Arrange
        var nonExistentProcessId = 999999;

        // Act
        var result = _service.IsProcessRunning(nonExistentProcessId);

        // Assert
        Assert.False(result);
    }

    [Fact]
    public async Task ExecuteAsync_CommandWithExitCode_CapturesExitCode()
    {
        // Arrange
        var command = OperatingSystem.IsWindows() ? "cmd.exe" : "sh";
        var args = OperatingSystem.IsWindows() ? "/c exit 5" : "-c \"exit 5\"";

        // Act
        var result = await _service.ExecuteAsync(command, args);

        // Assert
        Assert.True(result.IsSuccess);
        Assert.NotNull(result.Value);
        Assert.Equal(5, result.Value.ExitCode);
        Assert.False(result.Value.Success); // ExitCode != 0 means failure
    }
}
