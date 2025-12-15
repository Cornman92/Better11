@{
    RootModule = 'Shell.psm1'
    ModuleVersion = '0.3.0'
    GUID = 'e4f5a6b7-c8d9-0123-efgh-456789012cde'
    Author = 'Better11 Development Team'
    Description = 'Windows 11 Shell customization for Better11'
    PowerShellVersion = '5.1'
    FunctionsToExport = @(
        'Get-Better11TaskbarSettings',
        'Set-Better11TaskbarAlignment',
        'Set-Better11SearchMode',
        'Set-Better11TaskViewVisible',
        'Set-Better11WidgetsVisible',
        'Set-Better11CopilotVisible',
        'Enable-Better11ClassicContextMenu',
        'Disable-Better11ClassicContextMenu',
        'Set-Better11ShellPreset',
        'Restart-Better11Explorer'
    )
    PrivateData = @{
        PSData = @{
            Tags = @('Windows', 'Shell', 'Taskbar', 'StartMenu', 'Customization')
        }
    }
}
