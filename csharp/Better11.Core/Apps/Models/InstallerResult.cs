namespace Better11.Core.Apps.Models;

/// <summary>
/// Result of installer execution.
/// </summary>
public class InstallerResult
{
    public List<string> Command { get; init; } = new();
    public int ReturnCode { get; init; }
    public string Stdout { get; init; } = string.Empty;
    public string Stderr { get; init; } = string.Empty;
}
