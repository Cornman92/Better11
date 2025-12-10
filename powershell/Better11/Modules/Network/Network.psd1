@{
    ModuleVersion = '0.4.0'
    GUID = 'd9e8f7a6-5b4c-3d2e-a1b9-c8d7e6f5a4b3'
    Author = 'Better11 Team'
    Description = 'Network configuration and diagnostics for Better11'
    PowerShellVersion = '5.1'
    
    FunctionsToExport = @(
        'Get-Better11NetworkInfo',
        'Test-Better11NetworkSpeed',
        'Reset-Better11Network',
        'Optimize-Better11NetworkSettings',
        'Get-Better11ActiveConnections'
    )
    
    CmdletsToExport = @()
    VariablesToExport = @()
    AliasesToExport = @()
}
