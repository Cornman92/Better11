using Better11.Core.Models;

namespace Better11.Core.Interfaces;

/// <summary>
/// Service for process management and execution.
/// </summary>
public interface IProcessService
{
    /// <summary>
    /// Executes a process and waits for it to complete.
    /// </summary>
    /// <param name="fileName">The name of the file to execute.</param>
    /// <param name="arguments">The command-line arguments.</param>
    /// <param name="ct">Cancellation token.</param>
    /// <returns>Result containing the exit code and output.</returns>
    Task<Result<ProcessResult>> ExecuteAsync(string fileName, string arguments, CancellationToken ct = default);

    /// <summary>
    /// Executes a process with elevated permissions.
    /// </summary>
    /// <param name="fileName">The name of the file to execute.</param>
    /// <param name="arguments">The command-line arguments.</param>
    /// <param name="ct">Cancellation token.</param>
    /// <returns>Result containing the exit code.</returns>
    Task<Result<int>> ExecuteElevatedAsync(string fileName, string arguments, CancellationToken ct = default);

    /// <summary>
    /// Starts a process without waiting for it to complete.
    /// </summary>
    /// <param name="fileName">The name of the file to execute.</param>
    /// <param name="arguments">The command-line arguments.</param>
    /// <returns>Result containing the process ID.</returns>
    Result<int> StartProcess(string fileName, string arguments);

    /// <summary>
    /// Kills a process by its ID.
    /// </summary>
    /// <param name="processId">The ID of the process to kill.</param>
    /// <returns>Result indicating success or failure.</returns>
    Result KillProcess(int processId);

    /// <summary>
    /// Checks if a process is running.
    /// </summary>
    /// <param name="processId">The ID of the process.</param>
    /// <returns>True if the process is running; otherwise, false.</returns>
    bool IsProcessRunning(int processId);
}

/// <summary>
/// Represents the result of a process execution.
/// </summary>
public class ProcessResult
{
    /// <summary>
    /// Gets or sets the exit code of the process.
    /// </summary>
    public int ExitCode { get; set; }

    /// <summary>
    /// Gets or sets the standard output of the process.
    /// </summary>
    public string StandardOutput { get; set; } = string.Empty;

    /// <summary>
    /// Gets or sets the standard error of the process.
    /// </summary>
    public string StandardError { get; set; } = string.Empty;

    /// <summary>
    /// Gets a value indicating whether the process succeeded (exit code 0).
    /// </summary>
    public bool Success => ExitCode == 0;
}
