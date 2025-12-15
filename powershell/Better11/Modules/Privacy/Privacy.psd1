@{
    RootModule = 'Privacy.psm1'
    ModuleVersion = '0.3.0'
    GUID = 'c2d3e4f5-a6b7-8901-cdef-234567890abc'
    Author = 'Better11 Development Team'
    Description = 'Privacy and telemetry control for Windows 11'
    PowerShellVersion = '5.1'
    FunctionsToExport = @(
        'Get-Better11TelemetryLevel',
        'Set-Better11TelemetryLevel',
        'Get-Better11AppPermission',
        'Set-Better11AppPermission',
        'Get-Better11AllPermissions',
        'Disable-Better11AdvertisingId',
        'Enable-Better11AdvertisingId',
        'Disable-Better11Cortana',
        'Enable-Better11Cortana',
        'Set-Better11PrivacyPreset'
    )
    PrivateData = @{
        PSData = @{
            Tags = @('Windows', 'Privacy', 'Telemetry', 'Security')
        }
    }
}
