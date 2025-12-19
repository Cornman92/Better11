namespace Better11.Core.Apps.Models;

/// <summary>
/// Represents a single step in an installation plan.
/// </summary>
public class InstallPlanStep
{
    /// <summary>
    /// Application identifier.
    /// </summary>
    public required string AppId { get; init; }

    /// <summary>
    /// Human-readable application name.
    /// </summary>
    public required string Name { get; init; }

    /// <summary>
    /// Version from catalog.
    /// </summary>
    public required string Version { get; init; }

    /// <summary>
    /// Direct dependencies of this application.
    /// </summary>
    public List<string> Dependencies { get; init; } = new();

    /// <summary>
    /// Whether the application is already installed.
    /// </summary>
    public bool Installed { get; init; }

    /// <summary>
    /// Action to take: "install", "skip", or "blocked".
    /// </summary>
    public required string Action { get; init; }

    /// <summary>
    /// Additional information or warnings about this step.
    /// </summary>
    public string Notes { get; init; } = string.Empty;
}
