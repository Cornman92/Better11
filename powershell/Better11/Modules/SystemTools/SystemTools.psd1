@{
    RootModule = 'SystemTools.psm1'
    ModuleVersion = '0.3.0'
    GUID = 'h5l2j0k9-8k1i-0j6h-5l9m-0h3i2j5k7g6f'
    Author = 'Better11 Development Team'
    CompanyName = 'Better11'
    Copyright = '(c) 2025 Better11. MIT License.'
    Description = 'System tools and optimization for Better11'
    PowerShellVersion = '5.1'
    
    RequiredModules = @(
        @{ModuleName='../Common/Common.psd1'; GUID='b9f6d4e3-2e5c-4d0b-9f3g-4b7c6d9e0f1a'; ModuleVersion='0.3.0'}
    )
    
    FunctionsToExport = @(
        'Set-Better11RegistryValue',
        'Get-Better11RegistryValue',
        'Set-Better11ServiceStartMode',
        'Remove-Better11Bloatware'
    )
    
    CmdletsToExport = @()
    VariablesToExport = @()
    AliasesToExport = @()
}
