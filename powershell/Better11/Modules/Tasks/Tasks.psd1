@{
    RootModule = 'Tasks.psm1'
    ModuleVersion = '0.3.0'
    GUID = 'd9e0f123-4567-89ab-lmno-345678901ijk'
    Author = 'Better11 Development Team'
    Description = 'Scheduled Tasks management for Better11'
    PowerShellVersion = '5.1'
    FunctionsToExport = @(
        'Get-Better11ScheduledTasks',
        'Enable-Better11ScheduledTask',
        'Disable-Better11ScheduledTask',
        'Get-Better11TelemetryTasks',
        'Disable-Better11TelemetryTasks',
        'New-Better11ScheduledTask',
        'Remove-Better11ScheduledTask'
    )
    PrivateData = @{
        PSData = @{
            Tags = @('Windows', 'Tasks', 'ScheduledTasks', 'Automation')
        }
    }
}
