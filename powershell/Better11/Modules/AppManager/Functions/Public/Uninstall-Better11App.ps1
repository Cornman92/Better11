function Uninstall-Better11App {
    [CmdletBinding()]
    [OutputType([PSCustomObject])]
    param(
        [Parameter(Mandatory, Position = 0)]
        [string]$AppId,
        
        [Parameter()]
        [switch]$Force
    )
    
    process {
        try {
            $statePath = "$env:USERPROFILE\.better11\installed.json"
            if (-not (Test-Path $statePath)) {
                return [PSCustomObject]@{
                    Status = 'NotInstalled'
                    AppId = $AppId
                }
            }
            
            $stateData = Get-Content -Path $statePath -Raw | ConvertFrom-Json
            $apps = @($stateData.applications)
            
            $target = $apps | Where-Object { $_.app_id -eq $AppId }
            if (-not $target) {
                 return [PSCustomObject]@{
                    Status = 'NotInstalled'
                    AppId = $AppId
                }
            }
            
            # Remove
            $newApps = $apps | Where-Object { $_.app_id -ne $AppId }
            $newState = @{ applications = $newApps }
            $newState | ConvertTo-Json -Depth 5 | Set-Content -Path $statePath
            
            return [PSCustomObject]@{
                Status = 'Success'
                AppId = $AppId
            }
        }
        catch {
             Write-Error "Uninstall failed: $_"
             throw
        }
    }
}
