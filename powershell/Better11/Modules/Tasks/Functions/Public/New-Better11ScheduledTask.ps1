function New-Better11ScheduledTask {
    <#
    .SYNOPSIS
        Creates a new scheduled task.
    .DESCRIPTION
        Creates a scheduled task with common settings.
    .PARAMETER Name
        The task name.
    .PARAMETER Path
        The task folder path.
    .PARAMETER Execute
        The program to execute.
    .PARAMETER Arguments
        Arguments for the program.
    .PARAMETER Description
        Task description.
    .PARAMETER TriggerType
        Trigger type: Daily, Weekly, AtStartup, AtLogon.
    .PARAMETER Time
        Time for Daily/Weekly triggers (HH:mm).
    .EXAMPLE
        New-Better11ScheduledTask -Name "MyCleanup" -Execute "cleanmgr.exe" -TriggerType Daily -Time "02:00"
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,
        
        [Parameter()]
        [string]$Path = "\Better11\",
        
        [Parameter(Mandatory = $true)]
        [string]$Execute,
        
        [Parameter()]
        [string]$Arguments,
        
        [Parameter()]
        [string]$Description = "Created by Better11",
        
        [Parameter(Mandatory = $true)]
        [ValidateSet('Daily', 'Weekly', 'AtStartup', 'AtLogon')]
        [string]$TriggerType,
        
        [Parameter()]
        [string]$Time = "03:00"
    )

    try {
        if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
            throw "Administrator privileges required"
        }
        
        # Create action
        $ActionParams = @{
            Execute = $Execute
        }
        if ($Arguments) {
            $ActionParams['Argument'] = $Arguments
        }
        $Action = New-ScheduledTaskAction @ActionParams
        
        # Create trigger
        $Trigger = switch ($TriggerType) {
            'Daily' {
                New-ScheduledTaskTrigger -Daily -At $Time
            }
            'Weekly' {
                New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At $Time
            }
            'AtStartup' {
                New-ScheduledTaskTrigger -AtStartup
            }
            'AtLogon' {
                New-ScheduledTaskTrigger -AtLogon
            }
        }
        
        # Create settings
        $Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
        
        # Register task
        Register-ScheduledTask -TaskName $Name -TaskPath $Path -Action $Action -Trigger $Trigger -Settings $Settings -Description $Description -Force
        
        return [PSCustomObject]@{
            Success = $true
            Task = "$Path$Name"
            TriggerType = $TriggerType
        }
    }
    catch {
        Write-Error "Failed to create task: $_"
        return [PSCustomObject]@{ Success = $false; Task = "$Path$Name"; Error = $_.Exception.Message }
    }
}
