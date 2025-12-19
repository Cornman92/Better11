# Installation Planning - C# and PowerShell Implementation

**Last Updated**: 2025-12-19
**Status**: ✅ Implemented

## Overview

Better11's installation planning feature allows users to preview dependency trees, installation order, and current system state before executing installations. This feature is implemented using Windows-native technologies (C#, PowerShell, WinUI 3).

## C# Implementation

### Data Models

**Location**: `csharp/Better11.Core/Apps/Models/`

**InstallPlanStep.cs**:
```csharp
public class InstallPlanStep
{
    public required string AppId { get; init; }
    public required string Name { get; init; }
    public required string Version { get; init; }
    public List<string> Dependencies { get; init; } = new();
    public bool Installed { get; init; }
    public required string Action { get; init; }  // "install", "skip", or "blocked"
    public string Notes { get; init; } = string.Empty;
}
```

**InstallPlanSummary.cs**:
```csharp
public class InstallPlanSummary
{
    public required string TargetAppId { get; init; }
    public List<InstallPlanStep> Steps { get; init; } = new();
    public List<string> Warnings { get; init; } = new();

    // Helper methods
    public bool HasBlockedSteps();
    public int InstallCount();
    public int SkipCount();
}
```

### Core Planning Method

**Location**: `csharp/Better11.Core/Apps/AppManager.cs`

```csharp
/// <summary>
/// Build an installation plan without mutating state.
/// </summary>
public InstallPlanSummary BuildInstallPlan(string appId)
{
    // DFS traversal with cycle detection
    // Checks installation status
    // Detects missing dependencies
    // Returns topologically sorted steps (leaf → root)
}
```

**Algorithm Features**:
- ✅ Circular dependency detection with diagnostic paths
- ✅ Missing catalog entry detection
- ✅ Installation status annotation
- ✅ Topological sorting (leaf → root)
- ✅ No state mutation (read-only operation)

### Download Cache with Verification

**Location**: `csharp/Better11.Core/Apps/AppManager.cs`

```csharp
/// <summary>
/// Download with SHA-256 verified cache support.
/// </summary>
public async Task<(string Path, bool CacheHit)> DownloadWithCacheAsync(string appId)
{
    // Check if cached file exists
    // Verify SHA-256 hash
    // Reuse if hash matches, redownload if corrupted
}
```

### Service Layer Integration

**Location**: `csharp/Better11.Core/Services/AppService.cs`

```csharp
public async Task<InstallPlanSummary> GetInstallPlanAsync(string appId)
{
    // Creates AppManager instance
    // Calls BuildInstallPlan
    // Returns plan summary
}
```

## PowerShell Implementation

### Cmdlet

**Location**: `powershell/Better11/Modules/AppManager/Functions/Public/Get-Better11InstallPlan.ps1`

**Cmdlet Name**: `Get-Better11InstallPlan`

### Usage Examples

```powershell
# Basic usage
Get-Better11InstallPlan -AppId "vscode"

# Display as formatted table
Get-Better11InstallPlan -AppId "chrome" | Format-Table

# With verbose output
Get-Better11InstallPlan -AppId "git" -Verbose

# Using custom catalog
Get-Better11InstallPlan -AppId "7zip" -CatalogPath "C:\custom\catalog.json"
```

### Output Format

Returns PSCustomObject array with properties:
- `AppId` - Application identifier
- `Name` - Human-readable name
- `Version` - Version from catalog
- `Action` - "install", "skip", or "blocked"
- `Installed` - Boolean installation status
- `Notes` - Additional information/warnings
- `Dependencies` - List of dependency app IDs

### Example Output

```powershell
PS> Get-Better11InstallPlan -AppId "vscode" | Format-Table

AppId       Name                  Version  Action   Installed Notes
-----       ----                  -------  ------   --------- -----
dotnet-sdk  .NET SDK              8.0.0    skip     True
git         Git for Windows       2.43.0   install  False
vscode      Visual Studio Code    1.85.0   install  False
```

## CLI Implementation

### Command

**Location**: `csharp/Better11.CLI/Commands/AppCommands.cs`

**Command**: `better11 apps plan <app-id>`

### Usage Examples

```bash
# Show installation plan for an application
better11 apps plan vscode

# Plan with warnings and colored output
better11 apps plan chrome
```

### Output Format

The CLI displays a formatted table using Spectre.Console with:
- Color-coded actions (blue=install, green=skip, red=blocked)
- Installation status
- Warning section below table
- Summary line with counts

### Example Output

```
ACTION    APP ID         VERSION    STATUS     NOTES
------    ----------     -------    --------   -----
SKIP      dotnet-sdk     8.0.0      installed  -
INSTALL   git            2.43.0     pending    -
INSTALL   vscode         1.85.0     pending    -

Plan: 2 to install, 1 to skip
```

### With Warnings

```
ACTION    APP ID         VERSION    STATUS     NOTES
------    ----------     -------    --------   ------------------------
BLOCKED   missing-dep    unknown    pending    Missing from catalog
BLOCKED   my-app         1.0.0      pending    Depends on blocked dependency: missing-dep

Warnings:
  - Missing catalog entry for dependency 'missing-dep'

Installation cannot proceed due to blocked dependencies
```

## WinUI 3 GUI Integration

### Location

- **XAML**: `csharp/Better11.WinUI/Views/ApplicationsPage.xaml`
- **ViewModel**: `csharp/Better11.WinUI/ViewModels/ApplicationsViewModel.cs`

### UI Features

✅ **Plan Button**: Added to application cards (next to Install button)
⏳ **Plan Dialog**: TODO - ContentDialog to show plan details

### Implementation Status

The "Plan" button has been added to the UI but the command handler and dialog need to be implemented. The implementation should:

1. **Add to AppViewModel** (model for each app card):
```csharp
public ICommand PlanCommand { get; init; }
```

2. **Add to ApplicationsViewModel**:
```csharp
private async Task ShowPlanAsync(string appId)
{
    var plan = await _appService.GetInstallPlanAsync(appId);

    // Create and show ContentDialog with plan details
    var dialog = new ContentDialog
    {
        Title = $"Installation Plan for {appId}",
        Content = CreatePlanView(plan),
        CloseButtonText = "Close",
        PrimaryButtonText = plan.HasBlockedSteps() ? null : "Install",
        XamlRoot = /* ... */
    };

    var result = await dialog.ShowAsync();
    if (result == ContentDialogResult.Primary)
    {
        await InstallAppAsync(appId);
    }
}
```

3. **Plan View** should display:
   - Table of steps with Action, App ID, Version, Status
   - Warnings section (if any)
   - Summary counts
   - Disable Install button if blocked

## Security Features

### SHA-256 Hash Verification

All cached installers undergo verification before reuse:
- ✅ Integrity check - file hasn't been corrupted
- ✅ Authenticity - matches catalog specification
- ✅ Protection - prevents using tampered installers

### Read-Only Planning

The `BuildInstallPlan` operation:
- ✅ Never downloads files
- ✅ Never modifies installation state
- ✅ Never executes installers
- ✅ Never changes system configuration

Safe to run at any time without side effects.

## Benefits

### 1. Transparency
See exactly what will be installed before committing.

### 2. Resource Planning
- Estimate disk space requirements
- Plan network bandwidth usage
- Schedule maintenance windows

### 3. Troubleshooting
- Clear diagnostics for circular dependencies
- Missing catalog entry detection
- Version conflict identification

### 4. Efficiency
- Cache reuse eliminates redundant downloads
- Useful for re-installations and shared dependencies

## Testing

### Unit Tests
Located in `csharp/Better11.Tests/`

Tests should cover:
- ✅ Circular dependency detection
- ✅ Missing catalog entries
- ✅ Topological ordering
- ✅ Cache hit/miss scenarios
- ✅ Hash verification

### Manual Testing

```powershell
# Test planning
Get-Better11InstallPlan -AppId "test-app"

# Test CLI
better11 apps plan test-app

# Test caching
better11 apps install test-app
# (should show cache hit on second run)
```

## Future Enhancements

### 1. Interactive Planning
- Allow users to exclude optional dependencies
- Version pinning for specific dependencies

### 2. Cost Estimation
- Download size totals
- Estimated installation time
- Disk space requirements

### 3. Conflict Detection
- Version mismatches across dependency chains
- Resolution strategy suggestions

### 4. Plan Export
- JSON export for automation
- Markdown report generation
- CI/CD integration

## Related Files

### C# Core
- `csharp/Better11.Core/Apps/AppManager.cs` - Core planning logic
- `csharp/Better11.Core/Apps/Models/InstallPlanStep.cs` - Data model
- `csharp/Better11.Core/Apps/Models/InstallPlanSummary.cs` - Summary container
- `csharp/Better11.Core/Services/AppService.cs` - Service wrapper
- `csharp/Better11.Core/Interfaces/IAppService.cs` - Service interface

### CLI
- `csharp/Better11.CLI/Commands/AppCommands.cs` - CLI command

### PowerShell
- `powershell/Better11/Modules/AppManager/Functions/Public/Get-Better11InstallPlan.ps1` - PowerShell cmdlet

### GUI
- `csharp/Better11.WinUI/Views/ApplicationsPage.xaml` - UI layout
- `csharp/Better11.WinUI/ViewModels/ApplicationsViewModel.cs` - View model

### Documentation
- `docs/install_planning.md` - Original planning document
- `plan.md` - Implementation plan (reference)
