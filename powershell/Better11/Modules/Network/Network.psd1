@{
    RootModule = 'Network.psm1'
    ModuleVersion = '0.3.0'
    GUID = 'd1h8f6g5-4g7e-6f2d-1h5i-6d9e8f1g3c2b'
    Author = 'Better11 Development Team'
    CompanyName = 'Better11'
    Copyright = '(c) 2025 Better11. MIT License.'
    Description = 'Network configuration and diagnostics for Better11'
    PowerShellVersion = '5.1'
    
    RequiredModules = @(
        @{ModuleName='../Common/Common.psd1'; GUID='b9f6d4e3-2e5c-4d0b-9f3g-4b7c6d9e0f1a'; ModuleVersion='0.3.0'}
    )
    
    FunctionsToExport = @(
        'Get-Better11NetworkAdapters',
        'Set-Better11DNS',
        'Clear-Better11DNSCache',
        'Reset-Better11TcpIp',
        'Reset-Better11Winsock',
        'Test-Better11NetworkConnectivity'
    )
    
    CmdletsToExport = @()
    VariablesToExport = @()
    AliasesToExport = @()
}
