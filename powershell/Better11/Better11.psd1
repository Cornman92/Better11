@{
    # Module manifest for Better11
    RootModule = 'Better11.psm1'
    ModuleVersion = '0.3.0'
    GUID = 'a1b2c3d4-e5f6-4a5b-8c9d-0e1f2a3b4c5d'
    Author = 'Better11 Development Team'
    CompanyName = 'Better11'
    Copyright = '(c) 2025 Better11. MIT License.'
    Description = 'PowerShell backend for Better11 Windows 11 enhancement toolkit. Provides system management, application installation, and security features.'
    
    PowerShellVersion = '5.1'
    DotNetFrameworkVersion = '4.7.2'
    
    # Nested modules to load
    NestedModules = @(
        'Modules\Common\Common.psd1',
        'Modules\Security\Security.psd1',
        'Modules\AppManager\AppManager.psd1',
        'Modules\SystemTools\SystemTools.psd1',
        'Modules\Updates\Updates.psd1',
        'Modules\Backup\Backup.psd1',
        'Modules\Performance\Performance.psd1',
        'Modules\Network\Network.psd1'
    )
    
    # Functions to export
    FunctionsToExport = @(
        # Common
        'Confirm-Better11Action',
        'New-Better11RestorePoint',
        'Backup-Better11Registry',
        'Write-Better11Log',
        'Test-Better11Administrator',
        'Get-Better11Config',
        'Set-Better11Config',
        
        # Security
        'Test-Better11CodeSignature',
        'Get-Better11CertificateInfo',
        'Verify-Better11FileHash',
        
        # AppManager
        'Get-Better11Apps',
        'Install-Better11App',
        'Uninstall-Better11App',
        'Update-Better11App',
        'Get-Better11AppStatus',
        
        # SystemTools
        'Set-Better11RegistryTweak',
        'Remove-Better11Bloatware',
        'Set-Better11Service',
        'Set-Better11PerformancePreset',
        'Set-Better11PrivacySetting',
        'Set-Better11TelemetryLevel',
        'Get-Better11StartupItems',
        'Set-Better11StartupItem',
        'Get-Better11WindowsFeatures',
        'Set-Better11WindowsFeature',
        
        # Updates
        'Get-Better11WindowsUpdate',
        'Install-Better11WindowsUpdate',
        'Set-Better11UpdatePolicy',
        'Suspend-Better11Updates',
        'Resume-Better11Updates',
        
        # Backup
        'New-Better11Backup',
        'Restore-Better11Backup',
        'Get-Better11BackupList',
        'Remove-Better11Backup',
        'Export-Better11Configuration',
        'Import-Better11Configuration',
        
        # Performance
        'Get-Better11SystemInfo',
        'Get-Better11PerformanceMetrics',
        'Optimize-Better11Performance',
        'Get-Better11StartupImpact',
        'Test-Better11SystemHealth',
        
        # Network
        'Get-Better11NetworkInfo',
        'Test-Better11NetworkSpeed',
        'Reset-Better11Network',
        'Optimize-Better11NetworkSettings',
        'Get-Better11ActiveConnections'
    )
    
    CmdletsToExport = @()
    VariablesToExport = @()
    AliasesToExport = @()
    
    PrivateData = @{
        PSData = @{
            Tags = @('Windows11', 'SystemManagement', 'Optimization', 'Security', 'Privacy')
            LicenseUri = 'https://github.com/yourusername/better11/blob/main/LICENSE'
            ProjectUri = 'https://github.com/yourusername/better11'
            ReleaseNotes = 'Initial PowerShell backend release for Better11 v0.3.0'
        }
    }
}
