function Enable-Better11ScheduledTask {
    <#
    .SYNOPSIS
        Enables a scheduled task.
    .DESCRIPTION
        Enables a disabled scheduled task.
    .PARAMETER Name
        The task name.
    .PARAMETER Path
        The task path (default: root).
    .EXAMPLE
        Enable-Better11ScheduledTask -Name "MyTask" -Path "\MyFolder\"
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
        
        Enable-ScheduledTask -TaskName $Name -TaskPath $Path -ErrorAction Stop
        
        return [PSCustomObject]@{
            Success = $true
            Task = "$Path$Name"
            State = 'Enabled'
        }
    }
    catch {
        Write-Error "Failed to enable task: $_"
        return [PSCustomObject]@{ Success = $false; Task = "$Path$Name"; Error = $_.Exception.Message }
    }
}
