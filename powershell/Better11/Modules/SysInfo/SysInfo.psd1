@{
    RootModule = 'SysInfo.psm1'
    ModuleVersion = '0.3.0'
    GUID = 'a6b7c8d9-e0f1-2345-ijkl-678901234efg'
    Author = 'Better11 Development Team'
    Description = 'System information gathering for Better11'
    PowerShellVersion = '5.1'
    FunctionsToExport = @(
        'Get-Better11SystemSummary',
        'Get-Better11WindowsInfo',
        'Get-Better11CPUInfo',
        'Get-Better11MemoryInfo',
        'Get-Better11GPUInfo',
        'Get-Better11StorageInfo',
        'Get-Better11NetworkInfo',
        'Get-Better11BIOSInfo',
        'Export-Better11SystemInfo'
    )
    PrivateData = @{
        PSData = @{
            Tags = @('Windows', 'SystemInfo', 'Hardware', 'Diagnostics')
        }
    }
}
