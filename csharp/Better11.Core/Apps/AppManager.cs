using Better11.Core.Apps.Models;
using Better11.Core.Models;
using Better11.Core.Validation;
using Microsoft.Extensions.Logging;

namespace Better11.Core.Apps;

/// <summary>
/// Coordinates catalog lookup, downloading, verification, and installation.
/// </summary>
public class AppManager
{
    private readonly CachedAppCatalog _cachedCatalog;
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
        ILogger<AppManager>? logger = null,
        TimeSpan? cacheExpiration = null)
    {
        _cachedCatalog = new CachedAppCatalog(catalogPath, cacheExpiration);
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
        return _cachedCatalog.ListAll();
    }

    /// <summary>
    /// Invalidates the catalog cache, forcing a reload on next access.
    /// </summary>
    public void InvalidateCatalogCache()
    {
        _cachedCatalog.Invalidate();
    }

    /// <summary>
    /// Gets catalog cache statistics.
    /// </summary>
    public CacheStatistics GetCacheStatistics()
    {
        return _cachedCatalog.GetStatistics();
    }

    public async Task<string> DownloadAsync(string appId)
    {
        ValidationHelper.ValidateAppId(appId, nameof(appId));

        var app = _catalog.Get(appId);
        _logger?.LogInformation("Downloading {Name} from {Uri}", app.Name, app.Uri);
        return await _downloader.DownloadAsync(app);
    }

    public async Task<(AppStatus, InstallerResult)> InstallAsync(
        string appId,
        IProgress<OperationProgress>? progress = null,
        CancellationToken cancellationToken = default)
    {
        ValidationHelper.ValidateAppId(appId, nameof(appId));

        var visited = new HashSet<string>();
        return await InstallRecursiveAsync(appId, visited, progress, cancellationToken);
    }

    private async Task<(AppStatus, InstallerResult)> InstallRecursiveAsync(
        string appId,
        HashSet<string> visited,
        IProgress<OperationProgress>? progress = null,
        CancellationToken cancellationToken = default)
    {
        if (visited.Contains(appId))
        {
            throw new DependencyException($"Circular dependency detected at {appId}");
        }
        visited.Add(appId);

        try
        {
            cancellationToken.ThrowIfCancellationRequested();

            progress?.Report(new OperationProgress
            {
                AppId = appId,
                Stage = OperationStage.Initializing,
                PercentComplete = 0,
                Message = $"Initializing installation for {appId}",
                IsComplete = false
            });

            var app = _cachedCatalog.Get(appId);
            var existing = _stateStore.Get(appId);
            if (existing != null && existing.Installed && existing.Version == app.Version)
            {
                _logger?.LogInformation("{AppId} is already installed (version {Version})", appId, app.Version);
                progress?.Report(new OperationProgress
                {
                    AppId = appId,
                    Stage = OperationStage.Completed,
                    PercentComplete = 100,
                    Message = $"{app.Name} is already installed",
                    IsComplete = true
                });
                return (existing, new InstallerResult
                {
                    Command = new List<string>(),
                    ReturnCode = 0,
                    Stdout = "already installed",
                    Stderr = string.Empty
                });
            }

            progress?.Report(new OperationProgress
            {
                AppId = appId,
                Stage = OperationStage.ResolvingDependencies,
                PercentComplete = 10,
                Message = $"Resolving dependencies for {app.Name}",
                IsComplete = false
            });

            var dependencyStatuses = new Dictionary<string, AppStatus>();
            foreach (var dependencyId in app.Dependencies)
            {
                cancellationToken.ThrowIfCancellationRequested();
                var (depStatus, _) = await InstallRecursiveAsync(dependencyId, visited, progress, cancellationToken);
                dependencyStatuses[dependencyId] = depStatus;
            }

            cancellationToken.ThrowIfCancellationRequested();

            progress?.Report(new OperationProgress
            {
                AppId = appId,
                Stage = OperationStage.Downloading,
                PercentComplete = 30,
                Message = $"Starting download for {app.Name}",
                IsComplete = false
            });

            var installerPath = await _downloader.DownloadAsync(app, progress: progress, cancellationToken: cancellationToken);

            progress?.Report(new OperationProgress
            {
                AppId = appId,
                Stage = OperationStage.Verifying,
                PercentComplete = 70,
                Message = $"Verifying {app.Name}",
                IsComplete = false
            });

            await _verifier.VerifyAsync(app, installerPath);

            progress?.Report(new OperationProgress
            {
                AppId = appId,
                Stage = OperationStage.Installing,
                PercentComplete = 80,
                Message = $"Installing {app.Name}",
                IsComplete = false
            });

            var result = _runner.Install(app, installerPath);

            progress?.Report(new OperationProgress
            {
                AppId = appId,
                Stage = OperationStage.UpdatingState,
                PercentComplete = 95,
                Message = $"Updating installation state for {app.Name}",
                IsComplete = false
            });

            var status = _stateStore.MarkInstalled(
                app.AppId,
                app.Version,
                installerPath,
                dependencyStatuses.Keys.ToList());

            progress?.Report(new OperationProgress
            {
                AppId = appId,
                Stage = OperationStage.Completed,
                PercentComplete = 100,
                Message = $"Successfully installed {app.Name}",
                IsComplete = true
            });

            return (status, result);
        }
        finally
        {
            visited.Remove(appId);
        }
    }

    public InstallerResult Uninstall(string appId)
    {
        ValidationHelper.ValidateAppId(appId, nameof(appId));

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
        foreach (var candidate in _cachedCatalog.ListAll())
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
            ValidationHelper.ValidateAppId(appId, nameof(appId));
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

    /// <summary>
    /// Build an installation plan without mutating state.
    /// </summary>
    /// <param name="appId">Target application to plan for</param>
    /// <returns>Installation plan summary with dependency ordering and warnings</returns>
    public InstallPlanSummary BuildInstallPlan(string appId)
    {
        ValidationHelper.ValidateAppId(appId, nameof(appId));

        var summary = new InstallPlanSummary { TargetAppId = appId };
        var visited = new HashSet<string>();
        var visitingStack = new List<string>();
        var visitingSet = new HashSet<string>();
        var blockedReasons = new Dictionary<string, List<string>>();

        void AddBlockReason(string target, string reason)
        {
            if (!blockedReasons.ContainsKey(target))
            {
                blockedReasons[target] = new List<string>();
            }
            if (!blockedReasons[target].Contains(reason))
            {
                blockedReasons[target].Add(reason);
            }
        }

        void AddWarning(string message)
        {
            if (!summary.Warnings.Contains(message))
            {
                summary.Warnings.Add(message);
            }
        }

        void Dfs(string currentId)
        {
            if (visited.Contains(currentId))
            {
                return;
            }

            if (visitingSet.Contains(currentId))
            {
                // Circular dependency detected
                var cycleStart = visitingStack.IndexOf(currentId);
                var cycle = visitingStack.Skip(cycleStart).Append(currentId).ToList();
                AddWarning($"Circular dependency detected: {string.Join(" -> ", cycle)}");
                foreach (var node in cycle)
                {
                    AddBlockReason(node, "Cycle detected");
                }
                return;
            }

            AppMetadata? app;
            try
            {
                app = _catalog.Get(currentId);
            }
            catch (KeyNotFoundException)
            {
                AddWarning($"Missing catalog entry for dependency '{currentId}'");
                AddBlockReason(currentId, "Missing from catalog");
                summary.Steps.Add(new InstallPlanStep
                {
                    AppId = currentId,
                    Name = "(missing)",
                    Version = "unknown",
                    Dependencies = new List<string>(),
                    Installed = false,
                    Action = "blocked",
                    Notes = "Missing from catalog"
                });
                visited.Add(currentId);
                return;
            }

            visitingStack.Add(currentId);
            visitingSet.Add(currentId);

            foreach (var dependencyId in app.Dependencies)
            {
                Dfs(dependencyId);
                if (blockedReasons.ContainsKey(dependencyId))
                {
                    AddBlockReason(app.AppId, $"Depends on blocked dependency: {dependencyId}");
                }
            }

            visitingStack.RemoveAt(visitingStack.Count - 1);
            visitingSet.Remove(currentId);

            var status = _stateStore.Get(app.AppId);
            var isInstalled = status != null && status.Installed && status.Version == app.Version;
            var action = isInstalled ? "skip" : "install";
            if (blockedReasons.ContainsKey(app.AppId))
            {
                action = "blocked";
            }

            var notes = blockedReasons.ContainsKey(app.AppId)
                ? string.Join("; ", blockedReasons[app.AppId])
                : string.Empty;

            summary.Steps.Add(new InstallPlanStep
            {
                AppId = app.AppId,
                Name = app.Name,
                Version = app.Version,
                Dependencies = new List<string>(app.Dependencies),
                Installed = isInstalled,
                Action = action,
                Notes = notes
            });

            visited.Add(currentId);
        }

        Dfs(appId);
        return summary;
    }

    /// <summary>
    /// Download an application installer with cache support.
    /// </summary>
    /// <param name="appId">Application to download</param>
    /// <returns>Tuple of (path, cacheHit)</returns>
    public async Task<(string Path, bool CacheHit)> DownloadWithCacheAsync(string appId)
    {
        ValidationHelper.ValidateAppId(appId, nameof(appId));

        var app = _catalog.Get(appId);
        var destination = _downloader.DestinationFor(app);
        var cacheHit = false;

        if (File.Exists(destination))
        {
            try
            {
                await _verifier.VerifyHashAsync(destination, app.Sha256);
                _logger?.LogInformation("Using cached installer for {AppId} at {Path}", app.AppId, destination);
                cacheHit = true;
            }
            catch (VerificationException)
            {
                _logger?.LogWarning("Cached installer for {AppId} failed verification; redownloading", app.AppId);
                File.Delete(destination);
            }
        }

        if (!cacheHit)
        {
            _logger?.LogInformation("Downloading {Name} from {Uri}", app.Name, app.Uri);
            await _downloader.DownloadAsync(app);
        }

        return (destination, cacheHit);
    }

    /// <summary>
    /// Install multiple applications in sequence with progress reporting.
    /// </summary>
    /// <param name="appIds">List of application IDs to install.</param>
    /// <param name="progress">Optional progress reporter for batch operation.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <param name="continueOnError">If true, continue installing remaining apps even if one fails.</param>
    /// <returns>Batch operation result with individual results for each app.</returns>
    public async Task<BatchOperationResult> BatchInstallAsync(
        IEnumerable<string> appIds,
        IProgress<OperationProgress>? progress = null,
        CancellationToken cancellationToken = default,
        bool continueOnError = true)
    {
        var appIdList = appIds.ToList();
        var result = new BatchOperationResult();
        var processed = 0;

        foreach (var appId in appIdList)
        {
            var itemStart = DateTime.Now;

            try
            {
                ValidationHelper.ValidateAppId(appId, nameof(appId));

                progress?.Report(new OperationProgress
                {
                    AppId = appId,
                    Stage = OperationStage.Initializing,
                    PercentComplete = (double)processed / appIdList.Count * 100,
                    Message = $"Installing {appId} ({processed + 1} of {appIdList.Count})",
                    IsComplete = false
                });

                var (status, installerResult) = await InstallAsync(appId, progress, cancellationToken);

                result.Results.Add(new BatchItemResult
                {
                    AppId = appId,
                    Success = installerResult.ReturnCode == 0,
                    Version = status.Version,
                    Status = installerResult.ReturnCode == 0 ? "Installed" : "Failed",
                    ErrorMessage = installerResult.ReturnCode != 0 ? installerResult.Stderr : null,
                    Duration = DateTime.Now - itemStart
                });

                _logger?.LogInformation("Batch install: {AppId} completed with code {Code}",
                    appId, installerResult.ReturnCode);
            }
            catch (Exception ex)
            {
                _logger?.LogError(ex, "Batch install: Failed to install {AppId}", appId);

                result.Results.Add(new BatchItemResult
                {
                    AppId = appId,
                    Success = false,
                    ErrorMessage = ex.Message,
                    Status = "Error",
                    Duration = DateTime.Now - itemStart
                });

                if (!continueOnError)
                {
                    break;
                }
            }

            processed++;
        }

        result.EndTime = DateTime.Now;

        progress?.Report(new OperationProgress
        {
            AppId = string.Join(", ", appIdList),
            Stage = OperationStage.Completed,
            PercentComplete = 100,
            Message = $"Batch installation complete: {result.SuccessCount}/{result.TotalCount} succeeded",
            IsComplete = true
        });

        return result;
    }

    /// <summary>
    /// Uninstall multiple applications in sequence.
    /// </summary>
    /// <param name="appIds">List of application IDs to uninstall.</param>
    /// <param name="continueOnError">If true, continue uninstalling remaining apps even if one fails.</param>
    /// <returns>Batch operation result with individual results for each app.</returns>
    public BatchOperationResult BatchUninstall(
        IEnumerable<string> appIds,
        bool continueOnError = true)
    {
        var appIdList = appIds.ToList();
        var result = new BatchOperationResult();

        foreach (var appId in appIdList)
        {
            var itemStart = DateTime.Now;

            try
            {
                ValidationHelper.ValidateAppId(appId, nameof(appId));

                var installerResult = Uninstall(appId);

                result.Results.Add(new BatchItemResult
                {
                    AppId = appId,
                    Success = installerResult.ReturnCode == 0,
                    Status = installerResult.ReturnCode == 0 ? "Uninstalled" : "Failed",
                    ErrorMessage = installerResult.ReturnCode != 0 ? installerResult.Stderr : null,
                    Duration = DateTime.Now - itemStart
                });

                _logger?.LogInformation("Batch uninstall: {AppId} completed with code {Code}",
                    appId, installerResult.ReturnCode);
            }
            catch (Exception ex)
            {
                _logger?.LogError(ex, "Batch uninstall: Failed to uninstall {AppId}", appId);

                result.Results.Add(new BatchItemResult
                {
                    AppId = appId,
                    Success = false,
                    ErrorMessage = ex.Message,
                    Status = "Error",
                    Duration = DateTime.Now - itemStart
                });

                if (!continueOnError)
                {
                    break;
                }
            }
        }

        result.EndTime = DateTime.Now;
        return result;
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
