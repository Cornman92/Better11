@{
    ModuleVersion = '0.4.0'
    GUID = 'e8f5c3d2-9a4b-4d1e-b7c6-3f2a1d8e9b5c'
    Author = 'Better11 Team'
    Description = 'Backup and restore functionality for Better11'
    PowerShellVersion = '5.1'
    
    FunctionsToExport = @(
        'New-Better11Backup',
        'Restore-Better11Backup',
        'Get-Better11BackupList',
        'Remove-Better11Backup',
        'Export-Better11Configuration',
        'Import-Better11Configuration'
    )
    
    CmdletsToExport = @()
    VariablesToExport = @()
    AliasesToExport = @()
}
