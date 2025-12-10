@{
    ModuleVersion = '0.4.0'
    GUID = 'a7b8c9d1-2e3f-4a5b-8c7d-6e5f4a3b2c1d'
    Author = 'Better11 Team'
    Description = 'Performance monitoring and optimization for Better11'
    PowerShellVersion = '5.1'
    
    FunctionsToExport = @(
        'Get-Better11SystemInfo',
        'Get-Better11PerformanceMetrics',
        'Optimize-Better11Performance',
        'Get-Better11StartupImpact',
        'Test-Better11SystemHealth'
    )
    
    CmdletsToExport = @()
    VariablesToExport = @()
    AliasesToExport = @()
}
