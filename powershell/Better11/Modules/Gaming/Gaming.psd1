@{
    RootModule = 'Gaming.psm1'
    ModuleVersion = '0.3.0'
    GUID = 'f5a6b7c8-d9e0-1234-ghij-567890123def'
    Author = 'Better11 Development Team'
    Description = 'Gaming optimization for Windows 11'
    PowerShellVersion = '5.1'
    FunctionsToExport = @(
        'Get-Better11GamingSettings',
        'Set-Better11GameMode',
        'Set-Better11GameBar',
        'Set-Better11GPUScheduling',
        'Set-Better11MouseAcceleration',
        'Disable-Better11NagleAlgorithm',
        'Enable-Better11NagleAlgorithm',
        'Set-Better11HighPerformancePower',
        'Set-Better11GamingPreset'
    )
    PrivateData = @{
        PSData = @{
            Tags = @('Windows', 'Gaming', 'Performance', 'Optimization')
        }
    }
}
