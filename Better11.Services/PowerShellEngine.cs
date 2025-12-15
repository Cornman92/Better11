using Better11.Core.Interfaces;
using Better11.Core.Models;
using Microsoft.Extensions.Logging;
using System.Management.Automation;
using System.Management.Automation.Runspaces;
using System.Text.Json;

namespace Better11.Services;

/// <summary>
/// Implementation of PowerShell execution engine.
/// </summary>
public class PowerShellEngine : IPowerShellEngine
{
    private readonly ILogger<PowerShellEngine> _logger;

    /// <summary>
    /// Initializes a new instance of the <see cref="PowerShellEngine"/> class.
    /// </summary>
    /// <param name="logger">The logger instance.</param>
    public PowerShellEngine(ILogger<PowerShellEngine> logger)
    {
        _logger = logger;
    }

    /// <inheritdoc/>
    public async Task<Result<PowerShellResult>> ExecuteScriptAsync(string script, CancellationToken ct = default)
    {
        try
        {
            _logger.LogInformation("Executing PowerShell script");
            _logger.LogDebug("Script: {Script}", script);

            using var powerShell = PowerShell.Create();
            powerShell.AddScript(script);

            var result = await Task.Run(() =>
            {
                var output = powerShell.Invoke();
                return CreateResult(powerShell, output);
            }, ct);

            _logger.LogInformation("PowerShell script executed. Success: {Success}, Errors: {ErrorCount}",
                result.Success, result.Errors.Count);

            return Result<PowerShellResult>.Success(result);
        }
        catch (OperationCanceledException)
        {
            _logger.LogWarning("PowerShell script execution cancelled");
            throw;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error executing PowerShell script");
            return Result<PowerShellResult>.Failure($"Failed to execute script: {ex.Message}");
        }
    }

    /// <inheritdoc/>
    public async Task<Result<PowerShellResult>> ExecuteCommandAsync(
        string command,
        Dictionary<string, object>? parameters = null,
        CancellationToken ct = default)
    {
        try
        {
            _logger.LogInformation("Executing PowerShell command: {Command}", command);

            using var powerShell = PowerShell.Create();
            powerShell.AddCommand(command);

            if (parameters != null)
            {
                foreach (var param in parameters)
                {
                    powerShell.AddParameter(param.Key, param.Value);
                    _logger.LogDebug("Added parameter: {Key} = {Value}", param.Key, param.Value);
                }
            }

            var result = await Task.Run(() =>
            {
                var output = powerShell.Invoke();
                return CreateResult(powerShell, output);
            }, ct);

            _logger.LogInformation("PowerShell command executed. Success: {Success}, Errors: {ErrorCount}",
                result.Success, result.Errors.Count);

            return Result<PowerShellResult>.Success(result);
        }
        catch (OperationCanceledException)
        {
            _logger.LogWarning("PowerShell command execution cancelled");
            throw;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error executing PowerShell command: {Command}", command);
            return Result<PowerShellResult>.Failure($"Failed to execute command: {ex.Message}");
        }
    }

    /// <inheritdoc/>
    public async Task<Result<T>> ExecuteScriptAsync<T>(string script, CancellationToken ct = default)
    {
        try
        {
            _logger.LogInformation("Executing PowerShell script with typed result");

            var scriptResult = await ExecuteScriptAsync(script, ct);

            if (!scriptResult.IsSuccess)
            {
                return Result<T>.Failure(scriptResult.Error!);
            }

            var psResult = scriptResult.Value!;

            if (!psResult.Success)
            {
                var error = string.Join("; ", psResult.Errors);
                return Result<T>.Failure($"PowerShell errors: {error}");
            }

            if (psResult.Output.Count == 0)
            {
                return Result<T>.Failure("No output from PowerShell script");
            }

            // Try to deserialize or convert the output
            var output = psResult.Output[0];

            if (output is T typedOutput)
            {
                return Result<T>.Success(typedOutput);
            }

            // Try JSON deserialization
            try
            {
                var json = output.ToString() ?? string.Empty;
                var deserial ized = JsonSerializer.Deserialize<T>(json);

                if (deserialized != null)
                {
                    return Result<T>.Success(deserialized);
                }
            }
            catch (JsonException)
            {
                // JSON deserialization failed, try direct conversion
            }

            return Result<T>.Failure($"Could not convert PowerShell output to type {typeof(T).Name}");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error executing PowerShell script with typed result");
            return Result<T>.Failure($"Failed to execute script: {ex.Message}");
        }
    }

    /// <inheritdoc/>
    public async Task<Result<PowerShellResult>> ExecuteScriptFileAsync(
        string scriptPath,
        Dictionary<string, object>? parameters = null,
        CancellationToken ct = default)
    {
        try
        {
            _logger.LogInformation("Executing PowerShell script file: {ScriptPath}", scriptPath);

            if (!File.Exists(scriptPath))
            {
                return Result<PowerShellResult>.Failure($"Script file not found: {scriptPath}");
            }

            var script = await File.ReadAllTextAsync(scriptPath, ct);

            using var powerShell = PowerShell.Create();
            powerShell.AddScript(script);

            if (parameters != null)
            {
                foreach (var param in parameters)
                {
                    powerShell.AddParameter(param.Key, param.Value);
                }
            }

            var result = await Task.Run(() =>
            {
                var output = powerShell.Invoke();
                return CreateResult(powerShell, output);
            }, ct);

            _logger.LogInformation("PowerShell script file executed. Success: {Success}, Errors: {ErrorCount}",
                result.Success, result.Errors.Count);

            return Result<PowerShellResult>.Success(result);
        }
        catch (OperationCanceledException)
        {
            _logger.LogWarning("PowerShell script file execution cancelled");
            throw;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error executing PowerShell script file: {ScriptPath}", scriptPath);
            return Result<PowerShellResult>.Failure($"Failed to execute script file: {ex.Message}");
        }
    }

    private PowerShellResult CreateResult(PowerShell powerShell, Collection<PSObject> output)
    {
        var result = new PowerShellResult
        {
            Output = output.Select(o => o.BaseObject).ToList(),
            Errors = powerShell.Streams.Error.Select(e => e.ToString()).ToList(),
            Warnings = powerShell.Streams.Warning.Select(w => w.ToString()).ToList(),
            Success = powerShell.Streams.Error.Count == 0
        };

        return result;
    }
}
