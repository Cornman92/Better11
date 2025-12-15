using Better11.Core.Interfaces;
using Better11.Core.Models;
using Microsoft.Extensions.Logging;
using System.Diagnostics;
using System.Text;

namespace Better11.Services;

/// <summary>
/// Implementation of process management service.
/// </summary>
public class ProcessService : IProcessService
{
    private readonly ILogger<ProcessService> _logger;

    /// <summary>
    /// Initializes a new instance of the <see cref="ProcessService"/> class.
    /// </summary>
    /// <param name="logger">The logger instance.</param>
    public ProcessService(ILogger<ProcessService> logger)
    {
        _logger = logger;
    }

    /// <inheritdoc/>
    public async Task<Result<ProcessResult>> ExecuteAsync(string fileName, string arguments, CancellationToken ct = default)
    {
        try
        {
            _logger.LogInformation("Executing process: {FileName} {Arguments}", fileName, arguments);

            var outputBuilder = new StringBuilder();
            var errorBuilder = new StringBuilder();

            var processInfo = new ProcessStartInfo
            {
                FileName = fileName,
                Arguments = arguments,
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                CreateNoWindow = true
            };

            using var process = new Process { StartInfo = processInfo };

            process.OutputDataReceived += (sender, e) =>
            {
                if (!string.IsNullOrEmpty(e.Data))
                {
                    outputBuilder.AppendLine(e.Data);
                }
            };

            process.ErrorDataReceived += (sender, e) =>
            {
                if (!string.IsNullOrEmpty(e.Data))
                {
                    errorBuilder.AppendLine(e.Data);
                }
            };

            process.Start();
            process.BeginOutputReadLine();
            process.BeginErrorReadLine();

            await process.WaitForExitAsync(ct);

            var result = new ProcessResult
            {
                ExitCode = process.ExitCode,
                StandardOutput = outputBuilder.ToString(),
                StandardError = errorBuilder.ToString()
            };

            _logger.LogInformation("Process exited with code {ExitCode}", process.ExitCode);

            return Result<ProcessResult>.Success(result);
        }
        catch (OperationCanceledException)
        {
            _logger.LogWarning("Process execution cancelled");
            throw;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error executing process: {FileName}", fileName);
            return Result<ProcessResult>.Failure($"Failed to execute process: {ex.Message}");
        }
    }

    /// <inheritdoc/>
    public async Task<Result<int>> ExecuteElevatedAsync(string fileName, string arguments, CancellationToken ct = default)
    {
        try
        {
            _logger.LogInformation("Executing elevated process: {FileName} {Arguments}", fileName, arguments);

            var processInfo = new ProcessStartInfo
            {
                FileName = fileName,
                Arguments = arguments,
                UseShellExecute = true,
                Verb = "runas" // Request elevation
            };

            using var process = Process.Start(processInfo);

            if (process == null)
            {
                return Result<int>.Failure("Failed to start elevated process");
            }

            await process.WaitForExitAsync(ct);

            _logger.LogInformation("Elevated process exited with code {ExitCode}", process.ExitCode);

            return Result<int>.Success(process.ExitCode);
        }
        catch (OperationCanceledException)
        {
            _logger.LogWarning("Elevated process execution cancelled");
            throw;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error executing elevated process: {FileName}", fileName);
            return Result<int>.Failure($"Failed to execute elevated process: {ex.Message}");
        }
    }

    /// <inheritdoc/>
    public Result<int> StartProcess(string fileName, string arguments)
    {
        try
        {
            _logger.LogInformation("Starting process: {FileName} {Arguments}", fileName, arguments);

            var processInfo = new ProcessStartInfo
            {
                FileName = fileName,
                Arguments = arguments,
                UseShellExecute = true
            };

            var process = Process.Start(processInfo);

            if (process == null)
            {
                return Result<int>.Failure("Failed to start process");
            }

            _logger.LogInformation("Process started with ID {ProcessId}", process.Id);

            return Result<int>.Success(process.Id);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error starting process: {FileName}", fileName);
            return Result<int>.Failure($"Failed to start process: {ex.Message}");
        }
    }

    /// <inheritdoc/>
    public Result KillProcess(int processId)
    {
        try
        {
            _logger.LogInformation("Killing process: {ProcessId}", processId);

            var process = Process.GetProcessById(processId);
            process.Kill();

            _logger.LogInformation("Process killed successfully");

            return Result.Success();
        }
        catch (ArgumentException)
        {
            return Result.Failure($"Process with ID {processId} not found");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error killing process: {ProcessId}", processId);
            return Result.Failure($"Failed to kill process: {ex.Message}");
        }
    }

    /// <inheritdoc/>
    public bool IsProcessRunning(int processId)
    {
        try
        {
            var process = Process.GetProcessById(processId);
            return !process.HasExited;
        }
        catch
        {
            return false;
        }
    }
}
