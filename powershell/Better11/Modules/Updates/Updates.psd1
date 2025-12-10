@{
    RootModule = 'Updates.psm1'
    ModuleVersion = '0.3.0'
    GUID = 'f6a7b8c9-d0e1-4f5a-2b3c-4d5e6f7a8b9c'
    Author = 'Better11 Development Team'
    Description = 'Windows Update management for Better11'
    PowerShellVersion = '5.1'
    
    FunctionsToExport = @(
        'Get-Better11WindowsUpdate',
        'Install-Better11WindowsUpdate',
        'Set-Better11UpdatePolicy',
        'Suspend-Better11Updates',
        'Resume-Better11Updates'
    )
}
