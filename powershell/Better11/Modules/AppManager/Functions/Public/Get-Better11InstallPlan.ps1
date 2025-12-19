<#
.SYNOPSIS
    Build an installation plan for a Better11 application.

.DESCRIPTION
    Generates a detailed installation plan showing dependency order, current installation
    status, and any blockers (circular dependencies, missing catalog entries).

.PARAMETER AppId
    The application ID to plan for.

.PARAMETER CatalogPath
    Path to the application catalog JSON file. Defaults to the module's catalog.

.EXAMPLE
    Get-Better11InstallPlan -AppId "vscode"

    Shows the installation plan for Visual Studio Code, including all dependencies.

.EXAMPLE
    Get-Better11InstallPlan -AppId "chrome" | Format-Table

    Shows the installation plan in table format.

.OUTPUTS
    PSCustomObject[] with properties: AppId, Name, Version, Action, Installed, Notes

.NOTES
    This command is read-only and does not modify system state.
#>
function Get-Better11InstallPlan {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true, ValueFromPipeline = $true)]
        [string]$AppId,

        [Parameter()]
        [string]$CatalogPath = "$PSScriptRoot\..\..\Data\catalog.json"
    )

    begin {
        # Load catalog
        if (-not (Test-Path $CatalogPath)) {
            throw "Catalog not found: $CatalogPath"
        }

        $catalog = Get-Content $CatalogPath -Raw | ConvertFrom-Json
        $stateFile = Join-Path $env:USERPROFILE ".better11\installed.json"

        # Load installation state
        $installedApps = @{}
        if (Test-Path $stateFile) {
            $state = Get-Content $stateFile -Raw | ConvertFrom-Json
            $state.PSObject.Properties | ForEach-Object {
                $installedApps[$_.Name] = $_.Value
            }
        }

        # Helper functions
        function Get-AppFromCatalog {
            param([string]$Id)
            $app = $catalog.applications | Where-Object { $_.appId -eq $Id -or $_.app_id -eq $Id }
            if (-not $app) {
                throw [System.Collections.Generic.KeyNotFoundException]::new("Application '$Id' not found in catalog")
            }
            return $app
        }
    }

    process {
        $summary = @{
            TargetAppId = $AppId
            Steps = @()
            Warnings = @()
        }

        $visited = @{}
        $visitingStack = [System.Collections.Generic.List[string]]::new()
        $visitingSet = @{}
        $blockedReasons = @{}

        function Add-BlockReason {
            param([string]$Target, [string]$Reason)
            if (-not $blockedReasons.ContainsKey($Target)) {
                $blockedReasons[$Target] = @()
            }
            if ($blockedReasons[$Target] -notcontains $Reason) {
                $blockedReasons[$Target] += $Reason
            }
        }

        function Add-Warning {
            param([string]$Message)
            if ($summary.Warnings -notcontains $Message) {
                $summary.Warnings += $Message
            }
        }

        function Invoke-Dfs {
            param([string]$CurrentId)

            if ($visited.ContainsKey($CurrentId)) {
                return
            }

            if ($visitingSet.ContainsKey($CurrentId)) {
                # Circular dependency detected
                $cycleStart = $visitingStack.IndexOf($CurrentId)
                $cycle = $visitingStack[$cycleStart..($visitingStack.Count - 1)] + $CurrentId
                $cycleStr = $cycle -join " -> "
                Add-Warning "Circular dependency detected: $cycleStr"
                foreach ($node in $cycle) {
                    Add-BlockReason $node "Cycle detected"
                }
                return
            }

            try {
                $app = Get-AppFromCatalog -Id $CurrentId
            }
            catch [System.Collections.Generic.KeyNotFoundException] {
                Add-Warning "Missing catalog entry for dependency '$CurrentId'"
                Add-BlockReason $CurrentId "Missing from catalog"
                $summary.Steps += [PSCustomObject]@{
                    AppId = $CurrentId
                    Name = "(missing)"
                    Version = "unknown"
                    Dependencies = @()
                    Installed = $false
                    Action = "blocked"
                    Notes = "Missing from catalog"
                }
                $visited[$CurrentId] = $true
                return
            }

            $visitingStack.Add($CurrentId) | Out-Null
            $visitingSet[$CurrentId] = $true

            $dependencies = if ($app.dependencies) { $app.dependencies } else { @() }
            foreach ($depId in $dependencies) {
                Invoke-Dfs -CurrentId $depId
                if ($blockedReasons.ContainsKey($depId)) {
                    Add-BlockReason $app.appId "Depends on blocked dependency: $depId"
                }
            }

            $visitingStack.RemoveAt($visitingStack.Count - 1)
            $visitingSet.Remove($CurrentId)

            $appIdKey = if ($app.appId) { $app.appId } else { $app.app_id }
            $status = $installedApps[$appIdKey]
            $appVersion = if ($app.version) { $app.version } else { "1.0.0" }
            $isInstalled = $status -and $status.installed -and $status.version -eq $appVersion
            $action = if ($isInstalled) { "skip" } else { "install" }
            if ($blockedReasons.ContainsKey($appIdKey)) {
                $action = "blocked"
            }

            $notes = if ($blockedReasons.ContainsKey($appIdKey)) {
                $blockedReasons[$appIdKey] -join "; "
            } else {
                ""
            }

            $summary.Steps += [PSCustomObject]@{
                AppId = $appIdKey
                Name = $app.name
                Version = $appVersion
                Dependencies = $dependencies
                Installed = [bool]$isInstalled
                Action = $action
                Notes = $notes
            }

            $visited[$CurrentId] = $true
        }

        Invoke-Dfs -CurrentId $AppId

        # Output results
        Write-Verbose "Installation Plan for '$AppId':"
        Write-Verbose "  Steps: $($summary.Steps.Count)"
        Write-Verbose "  Warnings: $($summary.Warnings.Count)"

        if ($summary.Warnings.Count -gt 0) {
            Write-Warning "Planning warnings:"
            foreach ($warning in $summary.Warnings) {
                Write-Warning "  - $warning"
            }
        }

        # Return steps
        return $summary.Steps
    }
}
