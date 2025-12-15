function Optimize-Better11Performance {
    <#
    .SYNOPSIS
        Applies a performance optimization preset.
    .DESCRIPTION
        Applies a collection of performance optimizations.
    .PARAMETER Preset
        Maximum, Balanced, or Default.
    .EXAMPLE
        Optimize-Better11Performance -Preset Maximum
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet('Maximum', 'Balanced', 'Default')]
        [string]$Preset
    )

    try {
        if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
            throw "Administrator privileges required"
        }
        
        $Results = @()
        
        switch ($Preset) {
            'Maximum' {
                $Results += Set-Better11VisualEffects -Preset BestPerformance
                $Results += Set-Better11ProcessorScheduling -Priority Programs
                $Results += Set-Better11SystemResponsiveness -ReservedPercent 10
                $Results += Enable-Better11FastStartup
                
                # Additional optimizations
                Set-ItemProperty -Path 'HKCU:\Control Panel\Desktop' -Name 'MenuShowDelay' -Value '0' -Type String
                Set-ItemProperty -Path 'HKCU:\Control Panel\Desktop' -Name 'WaitToKillAppTimeout' -Value '2000' -Type String
                Set-ItemProperty -Path 'HKCU:\Control Panel\Desktop' -Name 'HungAppTimeout' -Value '1000' -Type String
                Set-ItemProperty -Path 'HKCU:\Control Panel\Desktop' -Name 'AutoEndTasks' -Value '1' -Type String
            }
            'Balanced' {
                $Results += Set-Better11VisualEffects -Preset Balanced
                $Results += Set-Better11ProcessorScheduling -Priority Programs
                $Results += Set-Better11SystemResponsiveness -ReservedPercent 20
                $Results += Enable-Better11FastStartup
                
                Set-ItemProperty -Path 'HKCU:\Control Panel\Desktop' -Name 'MenuShowDelay' -Value '200' -Type String
                Set-ItemProperty -Path 'HKCU:\Control Panel\Desktop' -Name 'WaitToKillAppTimeout' -Value '5000' -Type String
                Set-ItemProperty -Path 'HKCU:\Control Panel\Desktop' -Name 'HungAppTimeout' -Value '5000' -Type String
                Set-ItemProperty -Path 'HKCU:\Control Panel\Desktop' -Name 'AutoEndTasks' -Value '0' -Type String
            }
            'Default' {
                $Results += Set-Better11VisualEffects -Preset BestAppearance
                $Results += Set-Better11ProcessorScheduling -Priority Programs
                $Results += Set-Better11SystemResponsiveness -ReservedPercent 20
                $Results += Enable-Better11FastStartup
                
                Set-ItemProperty -Path 'HKCU:\Control Panel\Desktop' -Name 'MenuShowDelay' -Value '400' -Type String
                Set-ItemProperty -Path 'HKCU:\Control Panel\Desktop' -Name 'WaitToKillAppTimeout' -Value '20000' -Type String
                Set-ItemProperty -Path 'HKCU:\Control Panel\Desktop' -Name 'HungAppTimeout' -Value '5000' -Type String
                Set-ItemProperty -Path 'HKCU:\Control Panel\Desktop' -Name 'AutoEndTasks' -Value '0' -Type String
            }
        }
        
        return [PSCustomObject]@{
            Success = $true
            Preset = $Preset
            AppliedSettings = $Results.Count
            Message = 'Performance optimization applied. Sign out and back in for full effect.'
        }
    }
    catch {
        Write-Error "Failed to optimize performance: $_"
        return [PSCustomObject]@{ Success = $false; Preset = $Preset; Error = $_.Exception.Message }
    }
}
