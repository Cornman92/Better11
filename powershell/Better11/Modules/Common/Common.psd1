@{
    RootModule = 'Common.psm1'
    ModuleVersion = '0.3.0'
    GUID = 'b9f6d4e3-2e5c-4d0b-9f3g-4b7c6d9e0f1a'
    Author = 'Better11 Development Team'
    CompanyName = 'Better11'
    Copyright = '(c) 2025 Better11. MIT License.'
    Description = 'Common utilities for Better11 module'
    PowerShellVersion = '5.1'
    
    FunctionsToExport = @(
        'Write-Better11Log',
        'Test-Better11Administrator',
        'Confirm-Better11Action',
        'New-Better11Backup'
    )
    
    CmdletsToExport = @()
    VariablesToExport = @()
    AliasesToExport = @()
}
