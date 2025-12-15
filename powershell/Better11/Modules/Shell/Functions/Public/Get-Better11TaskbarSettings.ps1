function Get-Better11TaskbarSettings {
    <#
    .SYNOPSIS
        Gets current taskbar settings.
    .DESCRIPTION
        Retrieves the current Windows 11 taskbar configuration.
    .EXAMPLE
        Get-Better11TaskbarSettings
    #>
    [CmdletBinding()]
    param()

    try {
        $Path = 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced'
        $Props = Get-ItemProperty -Path $Path -ErrorAction SilentlyContinue
        
        $Alignment = switch ($Props.TaskbarAl) {
            0 { 'Left' }
            1 { 'Center' }
            default { 'Center' }
        }
        
        $SearchMode = switch ($Props.SearchboxTaskbarMode) {
            0 { 'Hidden' }
            1 { 'IconOnly' }
            2 { 'SearchBox' }
            3 { 'IconAndLabel' }
            default { 'SearchBox' }
        }
        
        return [PSCustomObject]@{
            Alignment = $Alignment
            SearchMode = $SearchMode
            ShowTaskView = ($Props.ShowTaskViewButton -ne 0)
            ShowWidgets = ($Props.TaskbarDa -ne 0)
            ShowChat = ($Props.TaskbarMn -ne 0)
            ShowCopilot = ($Props.ShowCopilotButton -ne 0)
            AutoHide = ($Props.TaskbarAutoHide -eq 1)
            SmallIcons = ($Props.TaskbarSmallIcons -eq 1)
            CombineButtons = $Props.TaskbarGlomLevel
        }
    }
    catch {
        Write-Error "Failed to get taskbar settings: $_"
        return $null
    }
}
