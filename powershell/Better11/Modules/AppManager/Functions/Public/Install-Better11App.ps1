function Install-Better11App {
    [CmdletBinding()]
    [OutputType([PSCustomObject])]
    param(
        [Parameter(Mandatory, Position = 0)]
        [string]$AppId,
        
        [Parameter()]
        [switch]$Force,
        
        [Parameter()]
        [switch]$SkipDependencies,
        
        [Parameter()]
        [switch]$DryRun
    )
    
    process {
        try {
            $CatalogPath = "$PSScriptRoot\..\..\Data\catalog.json"
            if (-not (Test-Path $CatalogPath)) {
                $CatalogPath = Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) "Data\catalog.json"
            }
            $catalogData = Get-Content -Path $CatalogPath -Raw | ConvertFrom-Json
            $app = $catalogData.applications | Where-Object { $_.app_id -eq $AppId }
            
            if (-not $app) {
                throw "Application not found: $AppId"
            }
            
            # Simulate installation by updating state
            $statePath = "$env:USERPROFILE\.better11\installed.json"
            if (-not (Test-Path $statePath)) {
                New-Item -Path (Split-Path $statePath) -ItemType Directory -Force | Out-Null
                Set-Content -Path $statePath -Value '{"applications": []}'
            }
            
            $stateData = Get-Content -Path $statePath -Raw | ConvertFrom-Json
            
            # Check if already installed
            $existing = $stateData.applications | Where-Object { $_.app_id -eq $AppId }
            if ($existing) {
                 return [PSCustomObject]@{
                    Status = 'AlreadyInstalled'
                    AppId = $AppId
                    Version = $existing.version
                }
            }
            
            if (-not $DryRun) {
                # Add to state
                $newApp = @{
                    app_id = $AppId
                    version = $app.version
                    installed_date = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss")
                }
                
                # PsCustomObject to Hashtable for JSON serialization is tricky in PS sometimes, but strictly:
                $currentApps = @($stateData.applications)
                $currentApps += $newApp
                
                $newState = @{ applications = $currentApps }
                $newState | ConvertTo-Json -Depth 5 | Set-Content -Path $statePath
                
                return [PSCustomObject]@{
                    Status = 'Success'
                    AppId = $AppId
                    Version = $app.version
                    ExitCode = 0
                    Output = "Simulated installation successful"
                }
            } else {
                 return [PSCustomObject]@{
                    Status = 'DryRun'
                    AppId = $AppId
                    Version = $app.version
                }
            }
        }
        catch {
            Write-Error "Installation failed: $_"
            throw
        }
    }
}
