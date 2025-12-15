using Better11.Core.Apps.Models;
using Microsoft.Extensions.Logging;

namespace Better11.Core.Apps;

/// <summary>
/// Coordinates catalog lookup, downloading, verification, and installation.
/// </summary>
public class AppManager
{
    private readonly AppCatalog _catalog;
    private readonly AppDownloader _downloader;
    private readonly DownloadVerifier _verifier;
    private readonly InstallerRunner _runner;
    private readonly InstallationStateStore _stateStore;
    private readonly ILogger<AppManager>? _logger;

    public AppManager(
        string catalogPath,
        string? downloadDir = null,
        string? stateFile = null,
        AppDownloader? downloader = null,
        DownloadVerifier? verifier = null,
        InstallerRunner? runner = null,
        ILogger<AppManager>? logger = null)
    {
        _catalog = AppCatalog.FromFile(catalogPath);
        var catalogDir = Path.GetDirectoryName(catalogPath) ?? Directory.GetCurrentDirectory();
        downloadDir ??= Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), ".better11", "downloads");
        stateFile ??= Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), ".better11", "installed.json");

        _downloader = downloader ?? new AppDownloader(downloadDir, catalogDir);
        _verifier = verifier ?? new DownloadVerifier();
        _runner = runner ?? new InstallerRunner();
        _stateStore = new InstallationStateStore(stateFile);
        _logger = logger;
    }

    public List<AppMetadata> ListAvailable()
    {
        return _catalog.ListAll();
    }

    public async Task<string> DownloadAsync(string appId)
    {
        var app = _catalog.Get(appId);
        _logger?.LogInformation("Downloading {Name} from {Uri}", app.Name, app.Uri);
        return await _downloader.DownloadAsync(app);
    }

    public async Task<(AppStatus, InstallerResult)> InstallAsync(string appId)
    {
        var visited = new HashSet<string>();
        return await InstallRecursiveAsync(appId, visited);
    }

    private async Task<(AppStatus, InstallerResult)> InstallRecursiveAsync(string appId, HashSet<string> visited)
    {
        if (visited.Contains(appId))
        {
            throw new DependencyException($"Circular dependency detected at {appId}");
        }
        visited.Add(appId);

        try
        {
            var app = _catalog.Get(appId);
            var existing = _stateStore.Get(appId);
            if (existing != null && existing.Installed && existing.Version == app.Version)
            {
                _logger?.LogInformation("{AppId} is already installed (version {Version})", appId, app.Version);
                return (existing, new InstallerResult
                {
                    Command = new List<string>(),
                    ReturnCode = 0,
                    Stdout = "already installed",
                    Stderr = string.Empty
                });
            }

            var dependencyStatuses = new Dictionary<string, AppStatus>();
            foreach (var dependencyId in app.Dependencies)
            {
                var (depStatus, _) = await InstallRecursiveAsync(dependencyId, visited);
                dependencyStatuses[dependencyId] = depStatus;
            }

            var installerPath = await DownloadAsync(appId);
            await _verifier.VerifyAsync(app, installerPath);
            var result = _runner.Install(app, installerPath);
            var status = _stateStore.MarkInstalled(
                app.AppId,
                app.Version,
                installerPath,
                dependencyStatuses.Keys.ToList());

            return (status, result);
        }
        finally
        {
            visited.Remove(appId);
        }
    }

    public InstallerResult Uninstall(string appId)
    {
        EnsureNotRequiredByDependents(appId);
        var status = _stateStore.Get(appId);
        if (status == null || !status.Installed)
        {
            throw new DependencyException($"{appId} is not currently installed");
        }

        var app = _catalog.Get(appId);
        var installerPath = !string.IsNullOrEmpty(status.InstallerPath) ? status.InstallerPath : null;
        var result = _runner.Uninstall(app, installerPath);
        _stateStore.MarkUninstalled(appId);
        return result;
    }

    private void EnsureNotRequiredByDependents(string appId)
    {
        var dependents = new List<string>();
        foreach (var candidate in _catalog.ListAll())
        {
            if (candidate.Dependencies.Contains(appId))
            {
                var status = _stateStore.Get(candidate.AppId);
                if (status != null && status.Installed)
                {
                    dependents.Add(candidate.AppId);
                }
            }
        }

        if (dependents.Count > 0)
        {
            var joined = string.Join(", ", dependents.OrderBy(x => x));
            throw new DependencyException($"Cannot uninstall {appId}; required by: {joined}");
        }
    }

    public List<AppStatus> Status(string? appId = null)
    {
        if (appId != null)
        {
            var status = _stateStore.Get(appId);
            return status != null ? new List<AppStatus> { status } : new List<AppStatus>();
        }
        return _stateStore.List();
    }

    public List<string> SummarizedStatus(string? appId = null)
    {
        var messages = new List<string>();
        foreach (var entry in Status(appId))
        {
            var installed = entry.Installed ? "installed" : "not installed";
            messages.Add($"{entry.AppId} v{entry.Version}: {installed}");
        }
        return messages;
    }
}

/// <summary>
/// Exception thrown when dependency resolution fails.
/// </summary>
public class DependencyException : Exception
{
    public DependencyException(string message) : base(message) { }
    public DependencyException(string message, Exception innerException) : base(message, innerException) { }
}
