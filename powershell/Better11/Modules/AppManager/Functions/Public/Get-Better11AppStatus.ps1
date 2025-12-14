function Get-Better11AppStatus {
    [CmdletBinding()]
    [OutputType([PSCustomObject[]])]
    param(
        [Parameter()]
        [string]$AppId
    )
    
    process {
        $apps = Get-Better11Apps
        if ($AppId) {
            $apps = $apps | Where-Object { $_.AppId -eq $AppId }
        }
        
        foreach ($app in $apps) {
            [PSCustomObject]@{
                AppId = $app.AppId
                Version = $app.Version
                Installed = $app.Installed
                InstallerPath = "" 
            }
        }
    }
}
