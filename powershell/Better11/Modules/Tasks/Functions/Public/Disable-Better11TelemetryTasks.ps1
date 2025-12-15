function Disable-Better11TelemetryTasks {
    <#
    .SYNOPSIS
        Disables known telemetry tasks.
    .DESCRIPTION
        Disables all known Windows telemetry and tracking tasks.
    .EXAMPLE
        Disable-Better11TelemetryTasks
    #>
    [CmdletBinding()]
    param()

    try {
        if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
            throw "Administrator privileges required"
        }
        
        $Results = foreach ($TaskFullPath in $script:TelemetryTasks) {
            $PathParts = $TaskFullPath -split '(?=[^\\]+$)'
            $TaskPath = $PathParts[0]
            $TaskName = $PathParts[1]
            
            $Task = Get-ScheduledTask -TaskPath $TaskPath -TaskName $TaskName -ErrorAction SilentlyContinue
            
            if ($Task) {
                try {
                    Disable-ScheduledTask -TaskPath $TaskPath -TaskName $TaskName -ErrorAction Stop | Out-Null
                    [PSCustomObject]@{
                        Task = $TaskFullPath
                        Success = $true
                        Message = 'Disabled'
                    }
                }
                catch {
                    [PSCustomObject]@{
                        Task = $TaskFullPath
                        Success = $false
                        Message = $_.Exception.Message
                    }
                }
            }
            else {
                [PSCustomObject]@{
                    Task = $TaskFullPath
                    Success = $true
                    Message = 'Not Found'
                }
            }
        }
        
        return $Results
    }
    catch {
        Write-Error "Failed to disable telemetry tasks: $_"
        return @()
    }
}
