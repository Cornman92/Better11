@{
    RootModule = 'SystemTools.psm1'
    ModuleVersion = '0.3.0'
    GUID = 'e5f6a7b8-c9d0-4e5f-1a2b-3c4d5e6f7a8b'
    Author = 'Better11 Development Team'
    Description = 'System management tools for Better11'
    PowerShellVersion = '5.1'
    
    FunctionsToExport = @(
        'Set-Better11RegistryTweak',
        'Remove-Better11Bloatware',
        'Set-Better11Service',
        'Set-Better11PerformancePreset',
        'Set-Better11PrivacySetting',
        'Set-Better11TelemetryLevel',
        'Get-Better11StartupItems',
        'Set-Better11StartupItem',
        'Get-Better11WindowsFeatures',
        'Set-Better11WindowsFeature'
    )
}
