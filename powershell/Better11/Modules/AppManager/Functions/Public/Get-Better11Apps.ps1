function Get-Better11Apps {
    <#
    .SYNOPSIS
        Retrieves available applications from the Better11 catalog.
    #>
    
    [CmdletBinding()]
    [OutputType([PSCustomObject[]])]
    param(
        [Parameter()]
        [string]$CatalogPath = "$PSScriptRoot\..\..\Data\catalog.json",
        
        [Parameter()]
        [switch]$Installed,
        
        [Parameter()]
        [switch]$Available
    )
    
    process {
        try {
            # Load catalog
            if (-not (Test-Path $CatalogPath)) {
                # Fallback to try to find it relative to module root if PSScriptRoot is weird
                $CatalogPath = Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) "Data\catalog.json"
                if (-not (Test-Path $CatalogPath)) {
                     throw "Catalog file not found: $CatalogPath"
                }
            }
            
            $catalogData = Get-Content -Path $CatalogPath -Raw | ConvertFrom-Json
            $apps = $catalogData.applications
            
            # Load installation state
            $statePath = "$env:USERPROFILE\.better11\installed.json"
            $installedApps = @{}
            
            if (Test-Path $statePath) {
                $stateData = Get-Content -Path $statePath -Raw | ConvertFrom-Json
                foreach ($app in $stateData.applications) {
                    $installedApps[$app.app_id] = $app
                }
            }
            
            # Process applications
            $results = foreach ($app in $apps) {
                $isInstalled = $installedApps.ContainsKey($app.app_id)
                
                # Filter based on parameters
                if ($Installed -and -not $isInstalled) { continue }
                if ($Available -and $isInstalled) { continue }
                
                [PSCustomObject]@{
                    AppId = $app.app_id
                    Name = $app.name
                    Version = $app.version
                    InstallerType = $app.installer_type
                    Description = $app.description
                    Installed = $isInstalled
                    InstalledVersion = if ($isInstalled) { $installedApps[$app.app_id].version } else { $null }
                    Uri = $app.uri
                    Dependencies = $app.dependencies
                }
            }
            
            return $results
        }
        catch {
            Write-Error "Failed to retrieve applications: $_"
            throw
        }
    }
}
