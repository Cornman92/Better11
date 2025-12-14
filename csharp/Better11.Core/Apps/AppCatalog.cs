using System.Text.Json;
using Better11.Core.Apps.Models;

namespace Better11.Core.Apps;

/// <summary>
/// Loads vetted application metadata from disk.
/// </summary>
public class AppCatalog
{
    private readonly Dictionary<string, AppMetadata> _apps;

    public AppCatalog(IEnumerable<AppMetadata> applications)
    {
        var materialized = applications.ToList();
        EnsureUniqueIds(materialized);
        _apps = materialized.ToDictionary(a => a.AppId);
    }

    public static AppCatalog FromFile(string path)
    {
        var json = File.ReadAllText(path);
        var data = JsonSerializer.Deserialize<JsonElement>(json);

        if (data.ValueKind != JsonValueKind.Object)
        {
            throw new ArgumentException("Catalog root must be a JSON object");
        }

        if (!data.TryGetProperty("applications", out var applicationsElement))
        {
            throw new ArgumentException("Catalog file is missing 'applications' array");
        }

        if (applicationsElement.ValueKind != JsonValueKind.Array)
        {
            throw new ArgumentException("'applications' must be an array");
        }

        var applications = new List<AppMetadata>();
        var index = 0;

        foreach (var entry in applicationsElement.EnumerateArray())
        {
            applications.Add(MaterializeEntry(entry, index));
            index++;
        }

        return new AppCatalog(applications);
    }

    private static AppMetadata MaterializeEntry(JsonElement entry, int index)
    {
        if (entry.ValueKind != JsonValueKind.Object)
        {
            throw new ArgumentException($"Application entry at index {index} must be an object");
        }

        var requiredFields = new[] { "app_id", "name", "version", "uri", "sha256", "installer_type" };
        foreach (var field in requiredFields)
        {
            if (!entry.TryGetProperty(field, out var fieldElement) || 
                fieldElement.ValueKind == JsonValueKind.Null ||
                (fieldElement.ValueKind == JsonValueKind.String && string.IsNullOrWhiteSpace(fieldElement.GetString())))
            {
                throw new ArgumentException($"Application entry {index} is missing required field '{field}'");
            }
        }

        var uri = entry.GetProperty("uri").GetString()!;
        if (!Uri.TryCreate(uri, UriKind.RelativeOrAbsolute, out _))
        {
            throw new ArgumentException($"Application entry {index} contains an invalid uri: {uri}");
        }

        var vettedDomains = CoerceStringList(entry, index, "vetted_domains");
        var dependencies = CoerceStringList(entry, index, "dependencies");
        var silentArgs = CoerceStringList(entry, index, "silent_args");

        var uninstallCommand = entry.TryGetProperty("uninstall_command", out var uninstallElement) 
            ? uninstallElement.GetString() 
            : null;

        var signature = entry.TryGetProperty("signature", out var sigElement) 
            ? sigElement.GetString() 
            : null;
        var signatureKey = entry.TryGetProperty("signature_key", out var keyElement) 
            ? keyElement.GetString() 
            : null;

        if ((signature != null && signatureKey == null) || (signature == null && signatureKey != null))
        {
            throw new ArgumentException(
                $"Application entry {index} must provide both 'signature' and 'signature_key' when signing is used");
        }

        var installerTypeStr = entry.GetProperty("installer_type").GetString()!.ToLowerInvariant();
        var installerType = installerTypeStr switch
        {
            "msi" => InstallerType.MSI,
            "exe" => InstallerType.EXE,
            "appx" => InstallerType.APPX,
            _ => throw new ArgumentException($"Unsupported installer_type in application entry {index}: {installerTypeStr}")
        };

        return new AppMetadata
        {
            AppId = entry.GetProperty("app_id").GetString()!,
            Name = entry.GetProperty("name").GetString()!,
            Version = entry.GetProperty("version").GetString()!,
            Uri = uri,
            Sha256 = entry.GetProperty("sha256").GetString()!,
            InstallerType = installerType,
            VettedDomains = vettedDomains,
            Signature = signature,
            SignatureKey = signatureKey,
            Dependencies = dependencies,
            SilentArgs = silentArgs,
            UninstallCommand = uninstallCommand
        };
    }

    private static List<string> CoerceStringList(JsonElement entry, int index, string fieldName)
    {
        if (!entry.TryGetProperty(fieldName, out var element))
        {
            return new List<string>();
        }

        if (element.ValueKind == JsonValueKind.Null)
        {
            return new List<string>();
        }

        if (element.ValueKind != JsonValueKind.Array)
        {
            throw new ArgumentException($"Field '{fieldName}' in application entry {index} must be an array of strings if provided");
        }

        var result = new List<string>();
        foreach (var item in element.EnumerateArray())
        {
            if (item.ValueKind != JsonValueKind.String)
            {
                throw new ArgumentException($"Field '{fieldName}' in application entry {index} must be an array of strings");
            }
            result.Add(item.GetString()!);
        }

        return result;
    }

    private static void EnsureUniqueIds(List<AppMetadata> metadata)
    {
        var seen = new HashSet<string>();
        foreach (var entry in metadata)
        {
            if (seen.Contains(entry.AppId))
            {
                throw new ArgumentException($"Duplicate application id detected: {entry.AppId}");
            }
            seen.Add(entry.AppId);
        }
    }

    public List<AppMetadata> ListAll()
    {
        return _apps.Values.ToList();
    }

    public AppMetadata Get(string appId)
    {
        if (!_apps.TryGetValue(appId, out var app))
        {
            throw new KeyNotFoundException($"Unknown application id: {appId}");
        }
        return app;
    }

    public bool Contains(string appId)
    {
        return _apps.ContainsKey(appId);
    }
}
