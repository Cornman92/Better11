@{
    RootModule = 'Performance.psm1'
    ModuleVersion = '0.3.0'
    GUID = 'f1234567-89ab-cdef-nopq-567890123lmn'
    Author = 'Better11 Development Team'
    Description = 'System performance optimization for Better11'
    PowerShellVersion = '5.1'
    FunctionsToExport = @(
        'Get-Better11PerformanceSettings',
        'Set-Better11VisualEffects',
        'Set-Better11ProcessorScheduling',
        'Set-Better11VirtualMemory',
        'Enable-Better11FastStartup',
        'Disable-Better11FastStartup',
        'Set-Better11SystemResponsiveness',
        'Optimize-Better11Performance',
        'Get-Better11ResourceUsage'
    )
    PrivateData = @{
        PSData = @{
            Tags = @('Windows', 'Performance', 'Optimization', 'Tweaks')
        }
    }
}
