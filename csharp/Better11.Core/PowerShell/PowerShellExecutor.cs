using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Linq;
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
        private readonly Runspace _runspace;
        private bool _disposed = false;

        public PowerShellExecutor(ILogger<PowerShellExecutor> logger)
        {
            _logger = logger;

            // Create runspace with Better11 module
            var initialSessionState = InitialSessionState.CreateDefault();

            // Import Better11 module
            string modulePath = GetBetter11ModulePath();
            if (!string.IsNullOrEmpty(modulePath))
            {
                initialSessionState.ImportPSModule(new[] { modulePath });
                _logger.LogInformation("Better11 PowerShell module loaded from: {ModulePath}", modulePath);
            }
            else
            {
                _logger.LogWarning("Better11 PowerShell module path not found");
            }

            _runspace = RunspaceFactory.CreateRunspace(initialSessionState);
            _runspace.Open();

            _logger.LogInformation("PowerShell runspace created");
        }

        /// <summary>
        /// Executes a PowerShell command and returns the results.
        /// </summary>
        public async Task<PSExecutionResult> ExecuteCommandAsync(string command,
            Dictionary<string, object>? parameters = null)
        {
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
                        errors.Add(error.ToString());
                        _logger.LogError("PowerShell error: {Error}", error);
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
                return new PSExecutionResult
                {
                    Success = false,
                    Output = new List<object>(),
                    Errors = new List<string> { ex.Message }
                };
            }
        }

        /// <summary>
        /// Executes a PowerShell script file.
        /// </summary>
        public async Task<PSExecutionResult> ExecuteScriptAsync(string scriptPath,
            Dictionary<string, object>? parameters = null)
        {
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
                return new PSExecutionResult
                {
                    Success = false,
                    Output = new List<object>(),
                    Errors = new List<string> { ex.Message }
                };
            }
        }

        private string GetBetter11ModulePath()
        {
            // Try multiple locations
            var possiblePaths = new[]
            {
                System.IO.Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "..", "..", "..", "powershell", "Better11", "Better11.psd1"),
                System.IO.Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), ".better11", "modules", "Better11", "Better11.psd1"),
                System.IO.Path.Combine(Environment.CurrentDirectory, "powershell", "Better11", "Better11.psd1")
            };

            foreach (var path in possiblePaths)
            {
                var fullPath = System.IO.Path.GetFullPath(path);
                if (System.IO.File.Exists(fullPath))
                {
                    return fullPath;
                }
            }

            return string.Empty;
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
    /// Result of PowerShell command execution.
    /// </summary>
    public class PSExecutionResult
    {
        public bool Success { get; set; }
        public List<object> Output { get; set; } = new();
        public List<string> Errors { get; set; } = new();
    }
}
