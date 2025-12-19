namespace Better11.Core.Apps.Models;

/// <summary>
/// Container for a complete installation plan.
/// </summary>
public class InstallPlanSummary
{
    /// <summary>
    /// The requested application ID.
    /// </summary>
    public required string TargetAppId { get; init; }

    /// <summary>
    /// Ordered steps (leaf → root) for installation.
    /// </summary>
    public List<InstallPlanStep> Steps { get; init; } = new();

    /// <summary>
    /// Collected warnings and errors from planning.
    /// </summary>
    public List<string> Warnings { get; init; } = new();

    /// <summary>
    /// Check if the plan contains any blocked steps.
    /// </summary>
    public bool HasBlockedSteps()
    {
        return Steps.Any(step => step.Action == "blocked");
    }

    /// <summary>
    /// Count of applications that need to be installed.
    /// </summary>
    public int InstallCount()
    {
        return Steps.Count(step => step.Action == "install");
    }

    /// <summary>
    /// Count of applications that are already installed.
    /// </summary>
    public int SkipCount()
    {
        return Steps.Count(step => step.Action == "skip");
    }
}
