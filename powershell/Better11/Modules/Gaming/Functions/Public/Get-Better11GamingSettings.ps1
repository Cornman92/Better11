function Get-Better11GamingSettings {
    <#
    .SYNOPSIS
        Gets current gaming settings.
    .DESCRIPTION
        Retrieves the current gaming-related configuration.
    .EXAMPLE
        Get-Better11GamingSettings
    #>
    [CmdletBinding()]
    param()

    try {
        # Game Mode
        $GameBarPath = 'HKCU:\SOFTWARE\Microsoft\GameBar'
        $GameModeValue = Get-ItemProperty -Path $GameBarPath -Name 'AutoGameModeEnabled' -ErrorAction SilentlyContinue
        $GameMode = if ($GameModeValue) { $GameModeValue.AutoGameModeEnabled -eq 1 } else { $true }
        
        # Game Bar
        $GameDVRPath = 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR'
        $GameBarValue = Get-ItemProperty -Path $GameDVRPath -Name 'AppCaptureEnabled' -ErrorAction SilentlyContinue
        $GameBar = if ($GameBarValue) { $GameBarValue.AppCaptureEnabled -eq 1 } else { $true }
        
        # GPU Scheduling
        $GPUPath = 'HKLM:\SYSTEM\CurrentControlSet\Control\GraphicsDrivers'
        $GPUValue = Get-ItemProperty -Path $GPUPath -Name 'HwSchMode' -ErrorAction SilentlyContinue
        $GPUScheduling = if ($GPUValue) { $GPUValue.HwSchMode -eq 2 } else { $false }
        
        # Mouse Acceleration
        $MousePath = 'HKCU:\Control Panel\Mouse'
        $MouseValue = Get-ItemProperty -Path $MousePath -Name 'MouseSpeed' -ErrorAction SilentlyContinue
        $MouseAcceleration = if ($MouseValue) { $MouseValue.MouseSpeed -ne "0" } else { $true }
        
        # Power Plan
        $PowerPlan = "Unknown"
        try {
            $ActiveScheme = powercfg /getactivescheme 2>&1
            if ($ActiveScheme -match "High performance") { $PowerPlan = "High Performance" }
            elseif ($ActiveScheme -match "Balanced") { $PowerPlan = "Balanced" }
            elseif ($ActiveScheme -match "Power saver") { $PowerPlan = "Power Saver" }
            elseif ($ActiveScheme -match "Ultimate") { $PowerPlan = "Ultimate Performance" }
        } catch { }
        
        return [PSCustomObject]@{
            GameModeEnabled = $GameMode
            GameBarEnabled = $GameBar
            GPUSchedulingEnabled = $GPUScheduling
            MouseAccelerationEnabled = $MouseAcceleration
            PowerPlan = $PowerPlan
        }
    }
    catch {
        Write-Error "Failed to get gaming settings: $_"
        return $null
    }
}
