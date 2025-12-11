function Get-Better11Apps {
    <#
    .SYNOPSIS
        Retrieves available applications from the Better11 catalog.
    
    .DESCRIPTION
        Lists all available applications that can be installed through Better11,
        including their metadata, versions, dependencies, and installation status.
    
    .PARAMETER CatalogPath
        Path to the catalog JSON file. Defaults to module's Data directory.
    
    .PARAMETER Installed
        If specified, returns only installed applications.
    
    .PARAMETER Available
        If specified, returns only available (not installed) applications.
    
    .PARAMETER AppId
        If specified, returns only the app with matching AppId.
    
    .EXAMPLE
        Get-Better11Apps
        Lists all applications in the catalog.
    
    .EXAMPLE
        Get-Better11Apps -Installed
        Lists only installed applications.
    
    .EXAMPLE
        Get-Better11Apps -AppId "vscode"
        Gets information about Visual Studio Code.
    
    .OUTPUTS
        PSCustomObject[]
        Array of application metadata objects.
    #>
    
    [CmdletBinding()]
    [OutputType([PSCustomObject[]])]
    param(
        [Parameter()]
        [string]$CatalogPath,
        
        [Parameter()]
        [switch]$Installed,
        
        [Parameter()]
        [switch]$Available,
        
        [Parameter()]
        [string]$AppId
    )
    
    begin {
        Write-Better11Log -Message "Retrieving Better11 applications" -Level Info
        
        # Determine catalog path
        if (-not $CatalogPath) {
            $moduleData = $ExecutionContext.SessionState.Module.Parent.PrivateData
            if ($moduleData) {
                $CatalogPath = Join-Path $moduleData.DataPath 'catalog.json'
            }
            else {
                # Fallback to Python catalog location
                $CatalogPath = Join-Path $PSScriptRoot '..\..\..\..\python\better11\apps\catalog.json'
            }
        }
    }
    
    process {
        try {
            # Load catalog
            if (-not (Test-Path $CatalogPath)) {
                throw "Catalog file not found: $CatalogPath"
            }
            
            $catalogData = Get-Content -Path $CatalogPath -Raw | ConvertFrom-Json
            $apps = $catalogData.applications
            
            # Load installation state
            $statePath = Join-Path $env:USERPROFILE '.better11\installed.json'
            $installedApps = @{}
            
            if (Test-Path $statePath) {
                $stateData = Get-Content -Path $statePath -Raw | ConvertFrom-Json
                if ($stateData.applications) {
                    foreach ($app in $stateData.applications) {
                        $installedApps[$app.app_id] = $app
                    }
                }
            }
            
            # Process applications
            $results = foreach ($app in $apps) {
                $isInstalled = $installedApps.ContainsKey($app.app_id)
                
                # Apply filters
                if ($Installed -and -not $isInstalled) { continue }
                if ($Available -and $isInstalled) { continue }
                if ($AppId -and $app.app_id -ne $AppId) { continue }
                
                [PSCustomObject]@{
                    AppId = $app.app_id
                    Name = $app.name
                    Version = $app.version
                    InstallerType = $app.installer_type
                    Description = if ($app.PSObject.Properties['description']) { $app.description } else { $null }
                    Installed = $isInstalled
                    InstalledVersion = if ($isInstalled) { $installedApps[$app.app_id].version } else { $null }
                    InstalledDate = if ($isInstalled -and $installedApps[$app.app_id].PSObject.Properties['installed_date']) { 
                        $installedApps[$app.app_id].installed_date 
                    } else { $null }
                    Uri = $app.uri
                    Sha256 = $app.sha256
                    Dependencies = if ($app.dependencies) { $app.dependencies } else { @() }
                    SilentArgs = if ($app.silent_args) { $app.silent_args } else { @() }
                    UninstallCommand = if ($app.PSObject.Properties['uninstall_command']) { $app.uninstall_command } else { $null }
                    VettedDomains = if ($app.vetted_domains) { $app.vetted_domains } else { @() }
                }
            }
            
            Write-Better11Log -Message "Retrieved $($results.Count) applications" -Level Info
            return $results
        }
        catch {
            Write-Better11Log -Message "Failed to retrieve applications: $_" -Level Error
            throw
        }
    }
}
