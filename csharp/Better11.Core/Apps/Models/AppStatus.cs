namespace Better11.Core.Apps.Models;

/// <summary>
/// Installation status for an application.
/// </summary>
public class AppStatus
{
    public required string AppId { get; init; }
    public required string Version { get; init; }
    public required string InstallerPath { get; init; }
    public required bool Installed { get; init; }
    public List<string> DependenciesInstalled { get; init; } = new();
}
