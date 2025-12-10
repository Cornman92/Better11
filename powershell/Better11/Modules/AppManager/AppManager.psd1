@{
    RootModule = 'AppManager.psm1'
    ModuleVersion = '0.3.0'
    GUID = 'd4e5f6a7-b8c9-4d5e-0f1a-2b3c4d5e6f7a'
    Author = 'Better11 Development Team'
    Description = 'Application management functions for Better11'
    PowerShellVersion = '5.1'
    
    FunctionsToExport = @(
        'Get-Better11Apps',
        'Install-Better11App',
        'Uninstall-Better11App',
        'Update-Better11App',
        'Get-Better11AppStatus'
    )
}
