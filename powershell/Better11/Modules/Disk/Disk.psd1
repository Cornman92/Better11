@{
    RootModule = 'Disk.psm1'
    ModuleVersion = '0.3.0'
    GUID = 'c0g7e5f4-3f6d-5e1c-0g4h-5c8d7e0f2b1a'
    Author = 'Better11 Development Team'
    CompanyName = 'Better11'
    Copyright = '(c) 2025 Better11. MIT License.'
    Description = 'Disk and storage management for Better11'
    PowerShellVersion = '5.1'
    
    RequiredModules = @(
        @{ModuleName='../Common/Common.psd1'; GUID='b9f6d4e3-2e5c-4d0b-9f3g-4b7c6d9e0f1a'; ModuleVersion='0.3.0'}
    )
    
    FunctionsToExport = @(
        'Get-Better11DiskSpace',
        'Clear-Better11TempFiles',
        'Get-Better11DiskUsage'
    )
    
    CmdletsToExport = @()
    VariablesToExport = @()
    AliasesToExport = @()
}
