@{
    RootModule = 'Updates.psm1'
    ModuleVersion = '0.3.0'
    GUID = 'd3e4f5a6-b7c8-9012-defg-345678901bcd'
    Author = 'Better11 Development Team'
    Description = 'Windows Update management for Better11'
    PowerShellVersion = '5.1'
    FunctionsToExport = @(
        'Get-Better11AvailableUpdates',
        'Install-Better11Updates',
        'Suspend-Better11Updates',
        'Resume-Better11Updates',
        'Set-Better11ActiveHours',
        'Get-Better11ActiveHours',
        'Get-Better11UpdateHistory',
        'Uninstall-Better11Update',
        'Get-Better11UpdateSettings'
    )
    PrivateData = @{
        PSData = @{
            Tags = @('Windows', 'Updates', 'WindowsUpdate', 'Patches')
        }
    }
}
