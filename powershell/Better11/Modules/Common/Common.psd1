@{
    RootModule = 'Common.psm1'
    ModuleVersion = '0.3.0'
    GUID = 'b2c3d4e5-f6a7-4b5c-9d0e-1f2a3b4c5d6e'
    Author = 'Better11 Development Team'
    Description = 'Common utilities for Better11 module'
    PowerShellVersion = '5.1'
    
    FunctionsToExport = @(
        'Confirm-Better11Action',
        'New-Better11RestorePoint',
        'Backup-Better11Registry',
        'Write-Better11Log',
        'Test-Better11Administrator',
        'Get-Better11Config',
        'Set-Better11Config'
    )
}
