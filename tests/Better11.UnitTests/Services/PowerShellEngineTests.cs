using Better11.Core.Interfaces;
using Better11.Services;
using Microsoft.Extensions.Logging;
using Moq;
using Xunit;

namespace Better11.UnitTests.Services;

/// <summary>
/// Unit tests for <see cref="PowerShellEngine"/>.
/// </summary>
public class PowerShellEngineTests
{
    private readonly Mock<ILogger<PowerShellEngine>> _mockLogger;
    private readonly IPowerShellEngine _engine;

    public PowerShellEngineTests()
    {
        _mockLogger = new Mock<ILogger<PowerShellEngine>>();
        _engine = new PowerShellEngine(_mockLogger.Object);
    }

    [Fact]
    public async Task ExecuteScriptAsync_SimpleScript_Success()
    {
        // Arrange
        var script = "Write-Output 'Hello World'";

        // Act
        var result = await _engine.ExecuteScriptAsync(script);

        // Assert
        Assert.True(result.IsSuccess);
        Assert.NotNull(result.Value);
        Assert.True(result.Value.Success);
        Assert.NotEmpty(result.Value.Output);
    }

    [Fact]
    public async Task ExecuteScriptAsync_MultipleOutputs_ReturnsAll()
    {
        // Arrange
        var script = @"
            Write-Output 'First'
            Write-Output 'Second'
            Write-Output 'Third'
        ";

        // Act
        var result = await _engine.ExecuteScriptAsync(script);

        // Assert
        Assert.True(result.IsSuccess);
        Assert.True(result.Value!.Success);
        Assert.True(result.Value.Output.Count >= 3);
    }

    [Fact]
    public async Task ExecuteScriptAsync_WithError_CapturesError()
    {
        // Arrange
        var script = "Get-Item 'C:\\NonExistentPath\\file.txt' -ErrorAction Stop";

        // Act
        var result = await _engine.ExecuteScriptAsync(script);

        // Assert
        Assert.True(result.IsSuccess); // Script execution succeeded
        Assert.NotNull(result.Value);
        Assert.False(result.Value.Success); // But PowerShell reported errors
        Assert.NotEmpty(result.Value.Errors);
    }

    [Fact]
    public async Task ExecuteScriptAsync_WithWarning_CapturesWarning()
    {
        // Arrange
        var script = "Write-Warning 'This is a warning'";

        // Act
        var result = await _engine.ExecuteScriptAsync(script);

        // Assert
        Assert.True(result.IsSuccess);
        Assert.True(result.Value!.Success);
        Assert.NotEmpty(result.Value.Warnings);
    }

    [Fact]
    public async Task ExecuteCommandAsync_SimpleCommand_Success()
    {
        // Arrange
        var command = "Get-Process";
        var parameters = new Dictionary<string, object>
        {
            { "Name", "powershell" }
        };

        // Act
        var result = await _engine.ExecuteCommandAsync(command, parameters);

        // Assert
        Assert.True(result.IsSuccess);
        Assert.NotNull(result.Value);
    }

    [Fact]
    public async Task ExecuteCommandAsync_WithoutParameters_Success()
    {
        // Arrange
        var command = "Get-Date";

        // Act
        var result = await _engine.ExecuteCommandAsync(command);

        // Assert
        Assert.True(result.IsSuccess);
        Assert.NotNull(result.Value);
        Assert.True(result.Value.Success);
        Assert.NotEmpty(result.Value.Output);
    }

    [Fact]
    public async Task ExecuteScriptAsync_WithVariables_Success()
    {
        // Arrange
        var script = @"
            $name = 'Better11'
            $version = '1.0.0'
            Write-Output ""$name v$version""
        ";

        // Act
        var result = await _engine.ExecuteScriptAsync(script);

        // Assert
        Assert.True(result.IsSuccess);
        Assert.True(result.Value!.Success);
        Assert.NotEmpty(result.Value.Output);
    }

    [Fact]
    public async Task ExecuteScriptAsync_MathOperation_ReturnsCorrectResult()
    {
        // Arrange
        var script = "2 + 2";

        // Act
        var result = await _engine.ExecuteScriptAsync(script);

        // Assert
        Assert.True(result.IsSuccess);
        Assert.True(result.Value!.Success);
        Assert.NotEmpty(result.Value.Output);
        Assert.Equal(4, Convert.ToInt32(result.Value.Output[0]));
    }

    [Fact]
    public async Task ExecuteScriptAsync_TypedResult_Success()
    {
        // Arrange
        var script = "Get-Date";

        // Act
        var result = await _engine.ExecuteScriptAsync<DateTime>(script);

        // Assert
        Assert.True(result.IsSuccess);
        Assert.IsType<DateTime>(result.Value);
    }

    [Fact]
    public async Task ExecuteScriptAsync_EmptyScript_Success()
    {
        // Arrange
        var script = string.Empty;

        // Act
        var result = await _engine.ExecuteScriptAsync(script);

        // Assert
        Assert.True(result.IsSuccess);
        Assert.NotNull(result.Value);
    }

    [Fact]
    public async Task ExecuteScriptAsync_WithCancellation_ThrowsOperationCanceledException()
    {
        // Arrange
        var cts = new CancellationTokenSource();
        cts.Cancel();

        var script = "Start-Sleep -Seconds 10";

        // Act & Assert
        await Assert.ThrowsAsync<OperationCanceledException>(async () =>
        {
            await _engine.ExecuteScriptAsync(script, cts.Token);
        });
    }

    [Fact]
    public async Task ExecuteScriptAsync_GetProcessInfo_ReturnsProcesses()
    {
        // Arrange
        var script = "Get-Process | Select-Object -First 5 | Select-Object Name, Id";

        // Act
        var result = await _engine.ExecuteScriptAsync(script);

        // Assert
        Assert.True(result.IsSuccess);
        Assert.True(result.Value!.Success);
        Assert.NotEmpty(result.Value.Output);
    }

    [Fact]
    public async Task ExecuteScriptAsync_StringOutput_Success()
    {
        // Arrange
        var testString = "Test Output String";
        var script = $"'{testString}'";

        // Act
        var result = await _engine.ExecuteScriptAsync(script);

        // Assert
        Assert.True(result.IsSuccess);
        Assert.True(result.Value!.Success);
        Assert.Contains(testString, result.Value.OutputString);
    }

    [Fact]
    public async Task ExecuteScriptFileAsync_InvalidPath_Failure()
    {
        // Arrange
        var nonExistentPath = "C:\\NonExistent\\script.ps1";

        // Act
        var result = await _engine.ExecuteScriptFileAsync(nonExistentPath);

        // Assert
        Assert.True(result.IsFailure);
        Assert.NotNull(result.Error);
    }

    [Fact]
    public async Task ExecuteCommandAsync_InvalidCommand_CapturesError()
    {
        // Arrange
        var command = "Get-NonExistentCommand";

        // Act
        var result = await _engine.ExecuteCommandAsync(command);

        // Assert
        Assert.True(result.IsSuccess); // Execution succeeded
        Assert.False(result.Value!.Success); // But PowerShell reported errors
        Assert.NotEmpty(result.Value.Errors);
    }
}
