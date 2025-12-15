function Remove-Better11ScheduledTask {
    <#
    .SYNOPSIS
        Removes a scheduled task.
    .DESCRIPTION
        Deletes a scheduled task.
    .PARAMETER Name
        The task name.
    .PARAMETER Path
        The task path.
    .EXAMPLE
        Remove-Better11ScheduledTask -Name "MyTask" -Path "\Better11\"
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,
        
        [Parameter()]
        [string]$Path = "\Better11\"
    )

    try {
        if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
            throw "Administrator privileges required"
        }
        
        Unregister-ScheduledTask -TaskName $Name -TaskPath $Path -Confirm:$false -ErrorAction Stop
        
        return [PSCustomObject]@{
            Success = $true
            Task = "$Path$Name"
            Message = 'Removed'
        }
    }
    catch {
        Write-Error "Failed to remove task: $_"
        return [PSCustomObject]@{ Success = $false; Task = "$Path$Name"; Error = $_.Exception.Message }
    }
}
