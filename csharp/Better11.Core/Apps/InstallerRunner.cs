using System.Diagnostics;
using System.Runtime.InteropServices;
using Better11.Core.Apps.Models;

namespace Better11.Core.Apps;

/// <summary>
/// Executes Windows installers with optional dry-run support.
/// </summary>
public class InstallerRunner
{
    private readonly bool _dryRun;

    public InstallerRunner(bool? dryRun = null)
    {
        // Default to dry-run on non-Windows hosts to keep tests safe
        _dryRun = dryRun ?? !RuntimeInformation.IsOSPlatform(OSPlatform.Windows);
    }

    public InstallerResult Install(AppMetadata app, string installerPath)
    {
        var command = InstallCommand(app, installerPath);
        return Execute(command);
    }

    public InstallerResult Uninstall(AppMetadata app, string? installerPath = null)
    {
        var command = UninstallCommand(app, installerPath);
        return Execute(command);
    }

    private InstallerResult Execute(List<string> command)
    {
        if (_dryRun)
        {
            return new InstallerResult
            {
                Command = command,
                ReturnCode = 0,
                Stdout = string.Empty,
                Stderr = string.Empty
            };
        }

        var processStartInfo = new ProcessStartInfo
        {
            FileName = command[0],
            Arguments = string.Join(" ", command.Skip(1).Select(QuoteArgument)),
            UseShellExecute = false,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            CreateNoWindow = true
        };

        try
        {
            using var process = Process.Start(processStartInfo);
            if (process == null)
            {
                throw new InstallerException("Failed to start installer process");
            }

            var stdout = process.StandardOutput.ReadToEnd();
            var stderr = process.StandardError.ReadToEnd();
            process.WaitForExit();

            if (process.ExitCode != 0)
            {
                throw new InstallerException(
                    $"Installer failed with exit code {process.ExitCode}: {stderr.Trim()}");
            }

            return new InstallerResult
            {
                Command = command,
                ReturnCode = process.ExitCode,
                Stdout = stdout,
                Stderr = stderr
            };
        }
        catch (Exception ex)
        {
            throw new InstallerException($"Failed to execute installer: {ex.Message}", ex);
        }
    }

    private List<string> InstallCommand(AppMetadata app, string installerPath)
    {
        return app.InstallerType switch
        {
            InstallerType.MSI => new List<string> { "msiexec", "/i", installerPath, "/qn", "/norestart" }
                .Concat(app.SilentArgs).ToList(),
            InstallerType.EXE => new List<string> { installerPath }
                .Concat(app.SilentArgs.Count > 0 ? app.SilentArgs : new List<string> { "/quiet", "/norestart" })
                .ToList(),
            InstallerType.APPX => new List<string>
            {
                "powershell", "-NoProfile", "-Command",
                $"Add-AppxPackage -ForceApplicationShutdown \"{installerPath}\""
            },
            _ => throw new InstallerException($"Unsupported installer type: {app.InstallerType}")
        };
    }

    private List<string> UninstallCommand(AppMetadata app, string? installerPath)
    {
        if (!string.IsNullOrEmpty(app.UninstallCommand))
        {
            return ParseCommandLine(app.UninstallCommand);
        }

        return app.InstallerType switch
        {
            InstallerType.MSI => installerPath == null
                ? throw new InstallerException("MSI uninstall requires installer_path when uninstall_command is not provided")
                : new List<string> { "msiexec", "/x", installerPath, "/qn", "/norestart" },
            InstallerType.APPX => throw new InstallerException("AppX uninstall requires an explicit uninstall_command with package identity"),
            InstallerType.EXE => throw new InstallerException("Executable uninstall requires an explicit uninstall_command"),
            _ => throw new InstallerException($"Unsupported installer type: {app.InstallerType}")
        };
    }

    private static string QuoteArgument(string arg)
    {
        if (arg.Contains(' ') || arg.Contains('"'))
        {
            return $"\"{arg.Replace("\"", "\\\"")}\"";
        }
        return arg;
    }

    private static List<string> ParseCommandLine(string commandLine)
    {
        var result = new List<string>();
        var current = new System.Text.StringBuilder();
        var inQuotes = false;

        foreach (var c in commandLine)
        {
            if (c == '"')
            {
                inQuotes = !inQuotes;
            }
            else if (char.IsWhiteSpace(c) && !inQuotes)
            {
                if (current.Length > 0)
                {
                    result.Add(current.ToString());
                    current.Clear();
                }
            }
            else
            {
                current.Append(c);
            }
        }

        if (current.Length > 0)
        {
            result.Add(current.ToString());
        }

        return result;
    }
}

/// <summary>
/// Exception thrown when installer execution fails.
/// </summary>
public class InstallerException : Exception
{
    public InstallerException(string message) : base(message) { }
    public InstallerException(string message, Exception innerException) : base(message, innerException) { }
}
