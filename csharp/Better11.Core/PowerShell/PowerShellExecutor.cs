using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Management.Automation;
using System.Management.Automation.Runspaces;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;

namespace Better11.Core.PowerShell
{
    /// <summary>
    /// Executes PowerShell commands and scripts with the Better11 module loaded.
    /// </summary>
    public class PowerShellExecutor : IDisposable
    {
        private readonly ILogger<PowerShellExecutor> _logger;
        private readonly Runspace? _runspace;
        private bool _disposed = false;

        public PowerShellExecutor(ILogger<PowerShellExecutor> logger)
        {
            _logger = logger;

            try
            {
                // Create runspace
                var initialSessionState = InitialSessionState.CreateDefault();

                // Import Better11 module
                string modulePath = GetBetter11ModulePath();
                if (!string.IsNullOrEmpty(modulePath))
                {
                    initialSessionState.ImportPSModule(new[] { modulePath });
                    _logger.LogInformation("Better11 module loaded from: {ModulePath}", modulePath);
                }
                else
                {
                    _logger.LogWarning("Better11 module path not found");
                }

                _runspace = RunspaceFactory.CreateRunspace(initialSessionState);
                _runspace.Open();

                _logger.LogInformation("PowerShell runspace created successfully");
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to create PowerShell runspace");
                throw;
            }
        }

        /// <summary>
        /// Executes a PowerShell command and returns the results.
        /// </summary>
        /// <param name="command">Command to execute.</param>
        /// <param name="parameters">Optional command parameters.</param>
        /// <returns>Execution result.</returns>
        public async Task<PSExecutionResult> ExecuteCommandAsync(
            string command,
            Dictionary<string, object>? parameters = null)
        {
            if (_runspace == null)
            {
                throw new InvalidOperationException("PowerShell runspace not initialized");
            }

            try
            {
                _logger.LogDebug("Executing PowerShell command: {Command}", command);

                using var powershell = System.Management.Automation.PowerShell.Create();
                powershell.Runspace = _runspace;

                powershell.AddCommand(command);

                if (parameters != null)
                {
                    foreach (var param in parameters)
                    {
                        powershell.AddParameter(param.Key, param.Value);
                    }
                }

                var results = await Task.Run(() => powershell.Invoke());

                var errors = new List<string>();
                if (powershell.HadErrors)
                {
                    foreach (var error in powershell.Streams.Error)
                    {
                        var errorMessage = error.ToString();
                        errors.Add(errorMessage);
                        _logger.LogError("PowerShell error: {Error}", errorMessage);
                    }
                }

                var output = new List<object>();
                foreach (var result in results)
                {
                    output.Add(result.BaseObject);
                }

                return new PSExecutionResult
                {
                    Success = !powershell.HadErrors,
                    Output = output,
                    Errors = errors
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to execute PowerShell command: {Command}", command);
                throw;
            }
        }

        /// <summary>
        /// Executes a PowerShell script file.
        /// </summary>
        /// <param name="scriptPath">Path to the script file.</param>
        /// <param name="parameters">Optional script parameters.</param>
        /// <returns>Execution result.</returns>
        public async Task<PSExecutionResult> ExecuteScriptAsync(
            string scriptPath,
            Dictionary<string, object>? parameters = null)
        {
            if (_runspace == null)
            {
                throw new InvalidOperationException("PowerShell runspace not initialized");
            }

            try
            {
                _logger.LogDebug("Executing PowerShell script: {Script}", scriptPath);

                using var powershell = System.Management.Automation.PowerShell.Create();
                powershell.Runspace = _runspace;

                powershell.AddCommand(scriptPath);

                if (parameters != null)
                {
                    powershell.AddParameters(parameters);
                }

                var results = await Task.Run(() => powershell.Invoke());

                var errors = new List<string>();
                if (powershell.HadErrors)
                {
                    foreach (var error in powershell.Streams.Error)
                    {
                        errors.Add(error.ToString());
                    }
                }

                var output = new List<object>();
                foreach (var result in results)
                {
                    output.Add(result.BaseObject);
                }

                return new PSExecutionResult
                {
                    Success = !powershell.HadErrors,
                    Output = output,
                    Errors = errors
                };
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to execute PowerShell script: {Script}", scriptPath);
                throw;
            }
        }

        private string GetBetter11ModulePath()
        {
            try
            {
                // Get path relative to assembly location
                var assemblyDir = AppDomain.CurrentDomain.BaseDirectory;
                var modulePath = Path.Combine(
                    assemblyDir,
                    "..", "..", "..", "..",
                    "powershell", "Better11", "Better11.psd1");

                var fullPath = Path.GetFullPath(modulePath);

                if (File.Exists(fullPath))
                {
                    return fullPath;
                }

                _logger.LogWarning("Better11 module not found at: {Path}", fullPath);
                return string.Empty;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error determining Better11 module path");
                return string.Empty;
            }
        }

        public void Dispose()
        {
            Dispose(true);
            GC.SuppressFinalize(this);
        }

        protected virtual void Dispose(bool disposing)
        {
            if (!_disposed)
            {
                if (disposing)
                {
                    _runspace?.Dispose();
                }
                _disposed = true;
            }
        }
    }

    /// <summary>
    /// Result of a PowerShell execution.
    /// </summary>
    public class PSExecutionResult
    {
        public bool Success { get; set; }
        public List<object> Output { get; set; } = new();
        public List<string> Errors { get; set; } = new();
    }
}
