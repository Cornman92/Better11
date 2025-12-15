function Get-Better11ActiveHours {
    <#
    .SYNOPSIS
        Gets Windows Update active hours.
    .DESCRIPTION
        Retrieves the currently configured active hours.
    .EXAMPLE
        Get-Better11ActiveHours
    #>
    [CmdletBinding()]
    param()

    try {
        $RegPath = 'HKLM:\SOFTWARE\Microsoft\WindowsUpdate\UX\Settings'
        
        $StartHour = 8
        $EndHour = 17
        $Enabled = $true
        
        try {
            $Props = Get-ItemProperty -Path $RegPath -ErrorAction SilentlyContinue
            if ($Props.ActiveHoursStart) { $StartHour = $Props.ActiveHoursStart }
            if ($Props.ActiveHoursEnd) { $EndHour = $Props.ActiveHoursEnd }
            if ($null -ne $Props.IsActiveHoursEnabled) { $Enabled = $Props.IsActiveHoursEnabled -eq 1 }
        } catch { }
        
        return [PSCustomObject]@{
            StartHour = $StartHour
            EndHour = $EndHour
            Enabled = $Enabled
            Display = "$StartHour`:00 - $EndHour`:00"
        }
    }
    catch {
        Write-Warning "Failed to get active hours: $_"
        return [PSCustomObject]@{ StartHour = 8; EndHour = 17; Enabled = $true }
    }
}
