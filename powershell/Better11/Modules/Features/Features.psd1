@{
    RootModule = 'Features.psm1'
    ModuleVersion = '0.3.0'
    GUID = 'b7c8d9e0-f123-4567-ijkl-890123456fgh'
    Author = 'Better11 Development Team'
    Description = 'Windows Optional Features management for Better11'
    PowerShellVersion = '5.1'
    FunctionsToExport = @(
        'Get-Better11OptionalFeatures',
        'Enable-Better11OptionalFeature',
        'Disable-Better11OptionalFeature',
        'Get-Better11InstalledCapabilities',
        'Add-Better11Capability',
        'Remove-Better11Capability'
    )
    PrivateData = @{
        PSData = @{
            Tags = @('Windows', 'Features', 'OptionalFeatures', 'Capabilities')
        }
    }
}
