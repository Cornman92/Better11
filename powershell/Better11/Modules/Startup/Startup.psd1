@{
    RootModule = 'Startup.psm1'
    ModuleVersion = '0.3.0'
    GUID = 'e0f12345-6789-abcd-mnop-456789012klm'
    Author = 'Better11 Development Team'
    Description = 'Startup program management for Better11'
    PowerShellVersion = '5.1'
    FunctionsToExport = @(
        'Get-Better11StartupPrograms',
        'Enable-Better11StartupProgram',
        'Disable-Better11StartupProgram',
        'Add-Better11StartupProgram',
        'Remove-Better11StartupProgram',
        'Get-Better11StartupImpact'
    )
    PrivateData = @{
        PSData = @{
            Tags = @('Windows', 'Startup', 'Boot', 'Performance')
        }
    }
}
