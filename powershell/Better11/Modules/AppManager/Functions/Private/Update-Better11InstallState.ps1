function Update-Better11InstallState {
    <#
    .SYNOPSIS
        Updates the installation state file.
    
    .DESCRIPTION
        Internal function to track installed applications.
    
    .PARAMETER AppId
        Application ID.
    
    .PARAMETER Version
        Application version.
    
    .PARAMETER Installed
        Installation status.
    
    .PARAMETER InstallerPath
        Path to installer file.
    #>
    
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$AppId,
        
        [Parameter(Mandatory = $true)]
        [string]$Version,
        
        [Parameter(Mandatory = $true)]
        [bool]$Installed,
        
        [Parameter()]
        [string]$InstallerPath
    )
    
    process {
        try {
            $statePath = Join-Path $env:USERPROFILE '.better11\installed.json'
            $stateDir = Split-Path $statePath -Parent
            
            # Ensure directory exists
            if (-not (Test-Path $stateDir)) {
                New-Item -Path $stateDir -ItemType Directory -Force | Out-Null
            }
            
            # Load existing state
            $state = if (Test-Path $statePath) {
                Get-Content -Path $statePath -Raw | ConvertFrom-Json
            } else {
                [PSCustomObject]@{
                    applications = @()
                }
            }
            
            # Update or add app state
            $appState = $state.applications | Where-Object { $_.app_id -eq $AppId }
            
            if ($appState) {
                $appState.version = $Version
                $appState.installed = $Installed
                $appState.installed_date = (Get-Date).ToString('o')
                if ($InstallerPath) {
                    $appState.installer_path = $InstallerPath
                }
            }
            else {
                $newAppState = [PSCustomObject]@{
                    app_id = $AppId
                    version = $Version
                    installed = $Installed
                    installed_date = (Get-Date).ToString('o')
                    installer_path = if ($InstallerPath) { $InstallerPath } else { "" }
                    dependencies_installed = @()
                }
                $state.applications = @($state.applications) + @($newAppState)
            }
            
            # Save state
            $state | ConvertTo-Json -Depth 10 | Set-Content -Path $statePath -Force
            
            Write-Verbose "Updated installation state for $AppId"
        }
        catch {
            Write-Better11Log -Message "Failed to update installation state: $_" -Level Error
            throw
        }
    }
}
