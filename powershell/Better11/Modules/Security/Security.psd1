@{
    RootModule = 'Security.psm1'
    ModuleVersion = '0.3.0'
    GUID = 'c3d4e5f6-a7b8-4c5d-9e0f-1a2b3c4d5e6f'
    Author = 'Better11 Development Team'
    Description = 'Security and verification functions for Better11'
    PowerShellVersion = '5.1'
    
    FunctionsToExport = @(
        'Test-Better11CodeSignature',
        'Get-Better11CertificateInfo',
        'Verify-Better11FileHash'
    )
}
