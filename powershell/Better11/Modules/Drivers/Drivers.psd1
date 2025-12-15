@{
    RootModule = 'Drivers.psm1'
    ModuleVersion = '0.3.0'
    GUID = 'c8d9e0f1-2345-6789-klmn-012345678hij'
    Author = 'Better11 Development Team'
    Description = 'Driver management for Better11'
    PowerShellVersion = '5.1'
    FunctionsToExport = @(
        'Get-Better11Drivers',
        'Get-Better11DriverIssues',
        'Backup-Better11Drivers',
        'Update-Better11Driver',
        'Export-Better11DriverList'
    )
    PrivateData = @{
        PSData = @{
            Tags = @('Windows', 'Drivers', 'Hardware', 'Management')
        }
    }
}
