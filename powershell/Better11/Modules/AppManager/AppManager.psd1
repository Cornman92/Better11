@{
    RootModule = 'AppManager.psm1'
    ModuleVersion = '0.1.0'
    GUID = '12345678-1234-1234-1234-123456789012'
    Author = 'Better11'
    CompanyName = 'Better11'
    Copyright = '(c) 2025 Better11'
    Description = 'App Manager Module'
    FunctionsToExport = @(
        'Get-Better11Apps',
        'Install-Better11App',
        'Uninstall-Better11App',
        'Get-Better11AppStatus'
    )
}
