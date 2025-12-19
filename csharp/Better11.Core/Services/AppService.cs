using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Security.Cryptography;
using System.Text.Json;
using System.Threading.Tasks;
using Better11.Core.Apps;
using Better11.Core.Apps.Models;
using Better11.Core.Interfaces;
using Better11.Core.Models;
using Better11.Core.PowerShell;
using Microsoft.Extensions.Logging;

namespace Better11.Core.Services
{
    /// <summary>
    /// Service for application management operations.
    /// </summary>
    public class AppService : IAppService
    {
        private readonly PowerShellExecutor _psExecutor;
        private readonly ILogger<AppService> _logger;
        private readonly string _catalogPath;
        private readonly string _downloadDir;
        private readonly string _stateFile;
        private readonly HttpClient _httpClient;

        private AppCatalog? _catalog;
        private Dictionary<string, AppStatus>? _installedApps;

        public AppService(
            PowerShellExecutor psExecutor,
            ILogger<AppService> logger,
            string catalogPath,
            string? downloadDir = null,
            string? stateFile = null)
        {
            _psExecutor = psExecutor;
            _logger = logger;
            _catalogPath = catalogPath;
            _downloadDir = downloadDir ?? Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.UserProfile),
                ".better11", "downloads");
            _stateFile = stateFile ?? Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.UserProfile),
                ".better11", "installed.json");
            _httpClient = new HttpClient();
        }

        /// <inheritdoc/>
        public async Task<List<AppMetadata>> ListAvailableAsync()
        {
            await LoadCatalogAsync();
            return _catalog?.Applications ?? new List<AppMetadata>();
        }

        /// <inheritdoc/>
        public async Task<AppMetadata?> GetAppAsync(string appId)
        {
            await LoadCatalogAsync();
            return _catalog?.Applications.FirstOrDefault(a => 
                a.AppId.Equals(appId, StringComparison.OrdinalIgnoreCase));
        }

        /// <inheritdoc/>
        public async Task<string> DownloadAsync(string appId)
        {
            var app = await GetAppAsync(appId);
            if (app == null)
            {
                throw new ArgumentException($"Application not found: {appId}");
            }

            _logger.LogInformation("Downloading {Name} from {Uri}", app.Name, app.Uri);

            Directory.CreateDirectory(_downloadDir);

            var fileName = Path.GetFileName(new Uri(app.Uri, UriKind.RelativeOrAbsolute).LocalPath);
            var destinationPath = Path.Combine(_downloadDir, fileName);

            // Handle local/relative URIs (for samples)
            if (!app.Uri.StartsWith("http", StringComparison.OrdinalIgnoreCase))
            {
                var catalogDir = Path.GetDirectoryName(_catalogPath) ?? ".";
                var sourcePath = Path.Combine(catalogDir, app.Uri);
                
                if (File.Exists(sourcePath))
                {
                    File.Copy(sourcePath, destinationPath, overwrite: true);
                    _logger.LogInformation("Copied local file to {Path}", destinationPath);
                    return destinationPath;
                }
            }

            // Download from URL
            using var response = await _httpClient.GetAsync(app.Uri);
            response.EnsureSuccessStatusCode();

            using var stream = await response.Content.ReadAsStreamAsync();
            using var fileStream = File.Create(destinationPath);
            await stream.CopyToAsync(fileStream);

            _logger.LogInformation("Downloaded to {Path}", destinationPath);
            return destinationPath;
        }

        /// <inheritdoc/>
        public async Task<(AppStatus Status, InstallerResult Result)> InstallAsync(string appId)
        {
            var app = await GetAppAsync(appId);
            if (app == null)
            {
                throw new ArgumentException($"Application not found: {appId}");
            }

            // Check if already installed
            var existingStatus = (await GetStatusAsync(appId)).FirstOrDefault();
            if (existingStatus?.Installed == true && existingStatus.Version == app.Version)
            {
                _logger.LogInformation("{AppId} is already installed (version {Version})", appId, app.Version);
                return (existingStatus, new InstallerResult
                {
                    ExitCode = 0,
                    StandardOutput = "Already installed"
                });
            }

            // Install dependencies first
            foreach (var depId in app.Dependencies)
            {
                _logger.LogInformation("Installing dependency: {Dep}", depId);
                await InstallAsync(depId);
            }

            // Download and verify
            var installerPath = await DownloadAsync(appId);
            
            if (!await VerifyInstallerAsync(appId, installerPath))
            {
                throw new InvalidOperationException($"Installer verification failed for {appId}");
            }

            // Run installer
            var result = await RunInstallerAsync(app, installerPath);

            // Update status
            var status = new AppStatus
            {
                AppId = appId,
                Version = app.Version,
                InstallerPath = installerPath,
                Installed = result.Success,
                DependenciesInstalled = app.Dependencies,
                InstallDate = DateTime.UtcNow
            };

            await SaveStatusAsync(status);

            return (status, result);
        }

        /// <inheritdoc/>
        public async Task<InstallerResult> UninstallAsync(string appId)
        {
            var app = await GetAppAsync(appId);
            if (app == null)
            {
                throw new ArgumentException($"Application not found: {appId}");
            }

            var status = (await GetStatusAsync(appId)).FirstOrDefault();
            if (status?.Installed != true)
            {
                throw new InvalidOperationException($"{appId} is not currently installed");
            }

            // Check if required by other apps
            var allApps = await ListAvailableAsync();
            var dependents = new List<string>();
            foreach (var otherApp in allApps)
            {
                if (otherApp.Dependencies.Contains(appId))
                {
                    var otherStatus = (await GetStatusAsync(otherApp.AppId)).FirstOrDefault();
                    if (otherStatus?.Installed == true)
                    {
                        dependents.Add(otherApp.AppId);
                    }
                }
            }

            if (dependents.Count > 0)
            {
                throw new InvalidOperationException(
                    $"Cannot uninstall {appId}; required by: {string.Join(", ", dependents)}");
            }

            // Run uninstaller
            var result = await RunUninstallerAsync(app, status.InstallerPath);

            // Update status
            status.Installed = false;
            await SaveStatusAsync(status);

            return result;
        }

        /// <inheritdoc/>
        public async Task<List<AppStatus>> GetStatusAsync(string? appId = null)
        {
            await LoadStateAsync();
            
            if (appId != null)
            {
                if (_installedApps!.TryGetValue(appId, out var status))
                {
                    return new List<AppStatus> { status };
                }
                return new List<AppStatus>();
            }

            return _installedApps!.Values.ToList();
        }

        /// <inheritdoc/>
        public async Task<bool> VerifyInstallerAsync(string appId, string installerPath)
        {
            var app = await GetAppAsync(appId);
            if (app == null)
            {
                return false;
            }

            _logger.LogInformation("Verifying installer: {Path}", installerPath);

            // Verify SHA256 hash
            using var stream = File.OpenRead(installerPath);
            using var sha256 = SHA256.Create();
            var hashBytes = await sha256.ComputeHashAsync(stream);
            var hash = BitConverter.ToString(hashBytes).Replace("-", "").ToLowerInvariant();

            if (!hash.Equals(app.Sha256, StringComparison.OrdinalIgnoreCase))
            {
                _logger.LogError("SHA256 mismatch. Expected: {Expected}, Got: {Actual}", app.Sha256, hash);
                return false;
            }

            _logger.LogInformation("SHA256 verification passed");
            return true;
        }

        private async Task<InstallerResult> RunInstallerAsync(AppMetadata app, string installerPath)
        {
            _logger.LogInformation("Running installer: {Path}", installerPath);

            var command = app.InstallerType switch
            {
                InstallerType.MSI => $"msiexec /i \"{installerPath}\" /quiet /norestart",
                InstallerType.EXE => $"\"{installerPath}\" {string.Join(" ", app.SilentArgs)}",
                InstallerType.APPX => $"Add-AppxPackage -Path \"{installerPath}\"",
                _ => throw new NotSupportedException($"Unsupported installer type: {app.InstallerType}")
            };

            var result = await _psExecutor.ExecuteCommandAsync(command);

            return new InstallerResult
            {
                Command = new List<string> { command },
                ExitCode = result.Success ? 0 : 1,
                StandardOutput = string.Join("\n", result.Output.Select(o => o?.ToString() ?? "")),
                StandardError = string.Join("\n", result.Errors)
            };
        }

        private async Task<InstallerResult> RunUninstallerAsync(AppMetadata app, string? installerPath)
        {
            _logger.LogInformation("Running uninstaller for: {AppId}", app.AppId);

            string command;
            if (!string.IsNullOrEmpty(app.UninstallCommand))
            {
                command = app.UninstallCommand;
            }
            else
            {
                command = app.InstallerType switch
                {
                    InstallerType.MSI when installerPath != null => 
                        $"msiexec /x \"{installerPath}\" /quiet /norestart",
                    InstallerType.APPX => 
                        $"Get-AppxPackage *{app.AppId}* | Remove-AppxPackage",
                    _ => throw new NotSupportedException(
                        $"No uninstall command available for {app.AppId}")
                };
            }

            var result = await _psExecutor.ExecuteCommandAsync(command);

            return new InstallerResult
            {
                Command = new List<string> { command },
                ExitCode = result.Success ? 0 : 1,
                StandardOutput = string.Join("\n", result.Output.Select(o => o?.ToString() ?? "")),
                StandardError = string.Join("\n", result.Errors)
            };
        }

        private async Task LoadCatalogAsync()
        {
            if (_catalog != null) return;

            if (!File.Exists(_catalogPath))
            {
                throw new FileNotFoundException($"Catalog file not found: {_catalogPath}");
            }

            var json = await File.ReadAllTextAsync(_catalogPath);
            _catalog = JsonSerializer.Deserialize<AppCatalog>(json, new JsonSerializerOptions
            {
                PropertyNameCaseInsensitive = true
            });
        }

        private async Task LoadStateAsync()
        {
            if (_installedApps != null) return;

            _installedApps = new Dictionary<string, AppStatus>();

            if (File.Exists(_stateFile))
            {
                var json = await File.ReadAllTextAsync(_stateFile);
                var states = JsonSerializer.Deserialize<List<AppStatus>>(json, new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true
                });

                if (states != null)
                {
                    foreach (var state in states)
                    {
                        _installedApps[state.AppId] = state;
                    }
                }
            }
        }

        private async Task SaveStatusAsync(AppStatus status)
        {
            await LoadStateAsync();
            _installedApps![status.AppId] = status;

            var directory = Path.GetDirectoryName(_stateFile);
            if (!string.IsNullOrEmpty(directory))
            {
                Directory.CreateDirectory(directory);
            }

            var json = JsonSerializer.Serialize(_installedApps.Values.ToList(), new JsonSerializerOptions
            {
                WriteIndented = true
            });

            await File.WriteAllTextAsync(_stateFile, json);
        }

        /// <inheritdoc/>
        public async Task<InstallPlanSummary> GetInstallPlanAsync(string appId)
        {
            // Use the C# AppManager for planning
            var manager = new AppManager(
                _catalogPath,
                _downloadDir,
                _stateFile,
                logger: _logger);

            return await Task.Run(() => manager.BuildInstallPlan(appId));
        }
    }
}
