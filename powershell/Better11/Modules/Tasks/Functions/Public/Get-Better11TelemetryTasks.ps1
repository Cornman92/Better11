function Get-Better11TelemetryTasks {
    <#
    .SYNOPSIS
        Gets known telemetry tasks.
    .DESCRIPTION
        Lists Windows telemetry and tracking tasks and their status.
    .EXAMPLE
        Get-Better11TelemetryTasks
    #>
    [CmdletBinding()]
    param()

    try {
        $Results = foreach ($TaskFullPath in $script:TelemetryTasks) {
            $PathParts = $TaskFullPath -split '(?=[^\\]+$)'
            $TaskPath = $PathParts[0]
            $TaskName = $PathParts[1]
            
            $Task = Get-ScheduledTask -TaskPath $TaskPath -TaskName $TaskName -ErrorAction SilentlyContinue
            
            if ($Task) {
                [PSCustomObject]@{
                    Name = $TaskName
                    Path = $TaskPath
                    State = $Task.State
                    Exists = $true
                    Description = $Task.Description
                }
            }
            else {
                [PSCustomObject]@{
                    Name = $TaskName
                    Path = $TaskPath
                    State = 'Not Found'
                    Exists = $false
                    Description = $null
                }
            }
        }
        
        return $Results
    }
    catch {
        Write-Error "Failed to get telemetry tasks: $_"
        return @()
    }
}
