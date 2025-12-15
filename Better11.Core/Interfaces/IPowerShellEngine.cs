using Better11.Core.Models;

namespace Better11.Core.Interfaces;

/// <summary>
/// Service for executing PowerShell scripts and commands.
/// </summary>
public interface IPowerShellEngine
{
    /// <summary>
    /// Executes a PowerShell script.
    /// </summary>
    /// <param name="script">The PowerShell script to execute.</param>
    /// <param name="ct">Cancellation token.</param>
    /// <returns>Result containing the PowerShell output.</returns>
    Task<Result<PowerShellResult>> ExecuteScriptAsync(string script, CancellationToken ct = default);

    /// <summary>
    /// Executes a PowerShell command with parameters.
    /// </summary>
    /// <param name="command">The PowerShell command to execute.</param>
    /// <param name="parameters">The parameters for the command.</param>
    /// <param name="ct">Cancellation token.</param>
    /// <returns>Result containing the PowerShell output.</returns>
    Task<Result<PowerShellResult>> ExecuteCommandAsync(string command, Dictionary<string, object>? parameters = null, CancellationToken ct = default);

    /// <summary>
    /// Executes a PowerShell script and returns a typed result.
    /// </summary>
    /// <typeparam name="T">The type to deserialize the result to.</typeparam>
    /// <param name="script">The PowerShell script to execute.</param>
    /// <param name="ct">Cancellation token.</param>
    /// <returns>Result containing the typed output.</returns>
    Task<Result<T>> ExecuteScriptAsync<T>(string script, CancellationToken ct = default);

    /// <summary>
    /// Executes a PowerShell script file.
    /// </summary>
    /// <param name="scriptPath">The path to the PowerShell script file.</param>
    /// <param name="parameters">The parameters for the script.</param>
    /// <param name="ct">Cancellation token.</param>
    /// <returns>Result containing the PowerShell output.</returns>
    Task<Result<PowerShellResult>> ExecuteScriptFileAsync(string scriptPath, Dictionary<string, object>? parameters = null, CancellationToken ct = default);
}

/// <summary>
/// Represents the result of a PowerShell execution.
/// </summary>
public class PowerShellResult
{
    /// <summary>
    /// Gets or sets a value indicating whether the execution succeeded.
    /// </summary>
    public bool Success { get; set; }

    /// <summary>
    /// Gets or sets the output objects from PowerShell.
    /// </summary>
    public List<object> Output { get; set; } = new();

    /// <summary>
    /// Gets or sets the error messages, if any.
    /// </summary>
    public List<string> Errors { get; set; } = new();

    /// <summary>
    /// Gets or sets the warnings, if any.
    /// </summary>
    public List<string> Warnings { get; set; } = new();

    /// <summary>
    /// Gets a value indicating whether there were any errors.
    /// </summary>
    public bool HasErrors => Errors.Count > 0;

    /// <summary>
    /// Gets the output as a single string.
    /// </summary>
    public string OutputString => string.Join(Environment.NewLine, Output);
}
