@{
    RootModule = 'Safety.psm1'
    ModuleVersion = '0.3.0'
    GUID = 'b1c2d3e4-f5a6-7890-abcd-ef1234567890'
    Author = 'Better11 Development Team'
    Description = 'Safety utilities for Better11 - restore points, backups, and confirmations'
    PowerShellVersion = '5.1'
    FunctionsToExport = @(
        'New-Better11RestorePoint',
        'Get-Better11RestorePoints',
        'Test-Better11Administrator',
        'Confirm-Better11Action',
        'Backup-Better11RegistryKey',
        'Restore-Better11RegistryKey'
    )
    PrivateData = @{
        PSData = @{
            Tags = @('Windows', 'Safety', 'Backup', 'RestorePoint')
        }
    }
}
