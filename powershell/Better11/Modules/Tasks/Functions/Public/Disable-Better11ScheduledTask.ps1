function Disable-Better11ScheduledTask {
    <#
    .SYNOPSIS
        Disables a scheduled task.
    .DESCRIPTION
        Disables a scheduled task to prevent it from running.
    .PARAMETER Name
        The task name.
    .PARAMETER Path
        The task path (default: root).
    .EXAMPLE
        Disable-Better11ScheduledTask -Name "MyTask" -Path "\MyFolder\"
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,
        
        [Parameter()]
        [string]$Path = "\"
    )

    try {
        if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
            throw "Administrator privileges required"
        }
        
        Disable-ScheduledTask -TaskName $Name -TaskPath $Path -ErrorAction Stop
        
        return [PSCustomObject]@{
            Success = $true
            Task = "$Path$Name"
            State = 'Disabled'
        }
    }
    catch {
        Write-Error "Failed to disable task: $_"
        return [PSCustomObject]@{ Success = $false; Task = "$Path$Name"; Error = $_.Exception.Message }
    }
}
