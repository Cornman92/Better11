function Get-Better11ScheduledTasks {
    <#
    .SYNOPSIS
        Gets scheduled tasks.
    .DESCRIPTION
        Lists scheduled tasks with optional filtering.
    .PARAMETER Path
        Filter by task path pattern.
    .PARAMETER State
        Filter by state (Ready, Running, Disabled).
    .EXAMPLE
        Get-Better11ScheduledTasks
        Get-Better11ScheduledTasks -Path "*Microsoft*"
    #>
    [CmdletBinding()]
    param(
        [Parameter()]
        [string]$Path = "*",
        
        [Parameter()]
        [ValidateSet('Ready', 'Running', 'Disabled', 'All')]
        [string]$State = 'All'
    )

    try {
        $Tasks = Get-ScheduledTask | Where-Object { $_.TaskPath -like $Path }
        
        if ($State -ne 'All') {
            $Tasks = $Tasks | Where-Object { $_.State -eq $State }
        }
        
        $Results = foreach ($Task in $Tasks) {
            $Info = Get-ScheduledTaskInfo -TaskName $Task.TaskName -TaskPath $Task.TaskPath -ErrorAction SilentlyContinue
            
            [PSCustomObject]@{
                Name = $Task.TaskName
                Path = $Task.TaskPath
                State = $Task.State
                Description = $Task.Description
                Author = $Task.Author
                LastRun = $Info.LastRunTime
                NextRun = $Info.NextRunTime
                LastResult = $Info.LastTaskResult
            }
        }
        
        return $Results
    }
    catch {
        Write-Error "Failed to get scheduled tasks: $_"
        return @()
    }
}
