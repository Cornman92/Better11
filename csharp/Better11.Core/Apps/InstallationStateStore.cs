using System.Text.Json;
using Better11.Core.Apps.Models;

namespace Better11.Core.Apps;

/// <summary>
/// Manages installation state persistence.
/// </summary>
public class InstallationStateStore
{
    private readonly string _stateFile;
    private Dictionary<string, AppStatus> _state;

    public InstallationStateStore(string stateFile)
    {
        _stateFile = stateFile;
        var directory = Path.GetDirectoryName(_stateFile);
        if (!string.IsNullOrEmpty(directory))
        {
            Directory.CreateDirectory(directory);
        }
        _state = new Dictionary<string, AppStatus>();
        if (File.Exists(_stateFile))
        {
            Load();
        }
    }

    private void Load()
    {
        var json = File.ReadAllText(_stateFile);
        var data = JsonSerializer.Deserialize<Dictionary<string, JsonElement>>(json);
        if (data == null) return;

        foreach (var (appId, entry) in data)
        {
            _state[appId] = new AppStatus
            {
                AppId = appId,
                Version = entry.GetProperty("version").GetString()!,
                InstallerPath = entry.GetProperty("installer_path").GetString()!,
                Installed = entry.GetProperty("installed").GetBoolean(),
                DependenciesInstalled = entry.TryGetProperty("dependencies_installed", out var deps)
                    ? deps.EnumerateArray().Select(e => e.GetString()!).ToList()
                    : new List<string>()
            };
        }
    }

    private void Persist()
    {
        var serialized = _state.ToDictionary(
            kvp => kvp.Key,
            kvp => new
            {
                version = kvp.Value.Version,
                installer_path = kvp.Value.InstallerPath,
                installed = kvp.Value.Installed,
                dependencies_installed = kvp.Value.DependenciesInstalled
            });

        var json = JsonSerializer.Serialize(serialized, new JsonSerializerOptions { WriteIndented = true });
        File.WriteAllText(_stateFile, json);
    }

    public AppStatus MarkInstalled(string appId, string version, string installerPath, List<string>? dependencies = null)
    {
        var status = new AppStatus
        {
            AppId = appId,
            Version = version,
            InstallerPath = installerPath,
            Installed = true,
            DependenciesInstalled = dependencies ?? new List<string>()
        };
        _state[appId] = status;
        Persist();
        return status;
    }

    public void MarkUninstalled(string appId)
    {
        if (_state.TryGetValue(appId, out var status))
        {
            _state[appId] = new AppStatus
            {
                AppId = status.AppId,
                Version = status.Version,
                InstallerPath = status.InstallerPath,
                Installed = false,
                DependenciesInstalled = status.DependenciesInstalled
            };
            Persist();
        }
    }

    public AppStatus? Get(string appId)
    {
        return _state.TryGetValue(appId, out var status) ? status : null;
    }

    public List<AppStatus> List()
    {
        return _state.Values.ToList();
    }
}
