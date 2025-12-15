function Get-Better11UpdateSettings {
    <#
    .SYNOPSIS
        Gets Windows Update settings.
    .DESCRIPTION
        Retrieves the current Windows Update configuration.
    .EXAMPLE
        Get-Better11UpdateSettings
    #>
    [CmdletBinding()]
    param()

    try {
        $RegPath = 'HKLM:\SOFTWARE\Microsoft\WindowsUpdate\UX\Settings'
        
        $Settings = @{
            ActiveHoursStart = 8
            ActiveHoursEnd = 17
            PauseUntil = $null
            RestartRequired = $false
        }
        
        try {
            $Props = Get-ItemProperty -Path $RegPath -ErrorAction SilentlyContinue
            if ($Props.ActiveHoursStart) { $Settings.ActiveHoursStart = $Props.ActiveHoursStart }
            if ($Props.ActiveHoursEnd) { $Settings.ActiveHoursEnd = $Props.ActiveHoursEnd }
            if ($Props.PauseUpdatesExpiryTime) { 
                $Settings.PauseUntil = [datetime]::Parse($Props.PauseUpdatesExpiryTime)
            }
        } catch { }
        
        # Check for pending reboot
        $RebootPending = Test-Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\RebootRequired"
        $Settings.RestartRequired = $RebootPending
        
        return [PSCustomObject]$Settings
    }
    catch {
        Write-Error "Failed to get update settings: $_"
        return $null
    }
}
