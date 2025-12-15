@{
    RootModule = 'Backup.psm1'
    ModuleVersion = '0.3.0'
    GUID = 'f3j0h8i7-6i9g-8h4f-3j7k-8f1g0h3i5e4d'
    Author = 'Better11 Development Team'
    CompanyName = 'Better11'
    Copyright = '(c) 2025 Better11. MIT License.'
    Description = 'Backup and restore operations for Better11'
    PowerShellVersion = '5.1'
    
    RequiredModules = @(
        @{ModuleName='../Common/Common.psd1'; GUID='b9f6d4e3-2e5c-4d0b-9f3g-4b7c6d9e0f1a'; ModuleVersion='0.3.0'}
    )
    
    FunctionsToExport = @(
        'New-Better11RestorePoint',
        'Get-Better11RestorePoints',
        'Backup-Better11RegistryHive'
    )
    
    CmdletsToExport = @()
    VariablesToExport = @()
    AliasesToExport = @()
}
