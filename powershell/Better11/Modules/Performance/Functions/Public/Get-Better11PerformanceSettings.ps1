function Get-Better11PerformanceSettings {
    <#
    .SYNOPSIS
        Gets current performance settings.
    .DESCRIPTION
        Retrieves Windows performance-related settings.
    .EXAMPLE
        Get-Better11PerformanceSettings
    #>
    [CmdletBinding()]
    param()

    try {
        # Visual effects
        $VisualFX = Get-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects' -ErrorAction SilentlyContinue
        $VisualFXSetting = switch ($VisualFX.VisualFXSetting) {
            0 { 'Custom' }
            1 { 'BestAppearance' }
            2 { 'BestPerformance' }
            3 { 'LetWindowsChoose' }
            default { 'Unknown' }
        }
        
        # Desktop settings
        $Desktop = Get-ItemProperty -Path 'HKCU:\Control Panel\Desktop' -ErrorAction SilentlyContinue
        
        # Memory management
        $Memory = Get-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management' -ErrorAction SilentlyContinue
        
        # Priority control
        $Priority = Get-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\PriorityControl' -ErrorAction SilentlyContinue
        
        # Fast startup
        $Power = Get-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Power' -ErrorAction SilentlyContinue
        
        return [PSCustomObject]@{
            VisualEffects = $VisualFXSetting
            MenuShowDelay = $Desktop.MenuShowDelay
            MouseHoverTime = $Desktop.MouseHoverTime
            PagingFileManaged = if ($Memory.PagingFiles -eq '@%SystemRoot%\pagefile.sys') { 'SystemManaged' } else { 'Custom' }
            Win32PrioritySeparation = $Priority.Win32PrioritySeparation
            FastStartupEnabled = $Power.HiberbootEnabled -eq 1
        }
    }
    catch {
        Write-Error "Failed to get performance settings: $_"
        return $null
    }
}
