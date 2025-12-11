@{
    RootModule = 'Power.psm1'
    ModuleVersion = '0.3.0'
    GUID = 'e2i9g7h6-5h8f-7g3e-2i6j-7e0f9g2h4d3c'
    Author = 'Better11 Development Team'
    CompanyName = 'Better11'
    Copyright = '(c) 2025 Better11. MIT License.'
    Description = 'Power management for Better11'
    PowerShellVersion = '5.1'
    
    RequiredModules = @(
        @{ModuleName='../Common/Common.psd1'; GUID='b9f6d4e3-2e5c-4d0b-9f3g-4b7c6d9e0f1a'; ModuleVersion='0.3.0'}
    )
    
    FunctionsToExport = @(
        'Get-Better11PowerPlans',
        'Set-Better11PowerPlan',
        'Enable-Better11Hibernation',
        'Disable-Better11Hibernation',
        'New-Better11BatteryReport'
    )
    
    CmdletsToExport = @()
    VariablesToExport = @()
    AliasesToExport = @()
}
