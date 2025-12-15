@{
    RootModule = 'AppManager.psm1'
    ModuleVersion = '0.3.0'
    GUID = 'g4k1i9j8-7j0h-9i5g-4k8l-9g2h1i4j6f5e'
    Author = 'Better11 Development Team'
    CompanyName = 'Better11'
    Copyright = '(c) 2025 Better11. MIT License.'
    Description = 'Application management for Better11'
    PowerShellVersion = '5.1'
    
    RequiredModules = @(
        @{ModuleName='../Common/Common.psd1'; GUID='b9f6d4e3-2e5c-4d0b-9f3g-4b7c6d9e0f1a'; ModuleVersion='0.3.0'}
    )
    
    FunctionsToExport = @(
        'Get-Better11InstalledApps',
        'Install-Better11App',
        'Uninstall-Better11App'
    )
    
    CmdletsToExport = @()
    VariablesToExport = @()
    AliasesToExport = @()
}
