function Set-Better11VisualEffects {
    <#
    .SYNOPSIS
        Sets visual effects preset.
    .DESCRIPTION
        Configures Windows visual effects for appearance or performance.
    .PARAMETER Preset
        BestPerformance, BestAppearance, or Balanced.
    .EXAMPLE
        Set-Better11VisualEffects -Preset BestPerformance
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet('BestPerformance', 'BestAppearance', 'Balanced')]
        [string]$Preset
    )

    try {
        $RegPath = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects'
        $AdvancedPath = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced'
        
        if (-not (Test-Path $RegPath)) {
            New-Item -Path $RegPath -Force | Out-Null
        }
        
        switch ($Preset) {
            'BestPerformance' {
                Set-ItemProperty -Path $RegPath -Name 'VisualFXSetting' -Value 2 -Type DWord
                
                # Disable individual visual effects
                $UserPreference = [byte[]](0x90, 0x12, 0x01, 0x80, 0x10, 0x00, 0x00, 0x00)
                Set-ItemProperty -Path 'HKCU:\Control Panel\Desktop' -Name 'UserPreferencesMask' -Value $UserPreference -Type Binary
                Set-ItemProperty -Path 'HKCU:\Control Panel\Desktop' -Name 'MenuShowDelay' -Value '0' -Type String
                Set-ItemProperty -Path 'HKCU:\Control Panel\Desktop\WindowMetrics' -Name 'MinAnimate' -Value '0' -Type String
                Set-ItemProperty -Path $AdvancedPath -Name 'TaskbarAnimations' -Value 0 -Type DWord -ErrorAction SilentlyContinue
            }
            'BestAppearance' {
                Set-ItemProperty -Path $RegPath -Name 'VisualFXSetting' -Value 1 -Type DWord
                
                # Enable all visual effects
                $UserPreference = [byte[]](0x9E, 0x3E, 0x07, 0x80, 0x12, 0x00, 0x00, 0x00)
                Set-ItemProperty -Path 'HKCU:\Control Panel\Desktop' -Name 'UserPreferencesMask' -Value $UserPreference -Type Binary
                Set-ItemProperty -Path 'HKCU:\Control Panel\Desktop' -Name 'MenuShowDelay' -Value '400' -Type String
                Set-ItemProperty -Path 'HKCU:\Control Panel\Desktop\WindowMetrics' -Name 'MinAnimate' -Value '1' -Type String
                Set-ItemProperty -Path $AdvancedPath -Name 'TaskbarAnimations' -Value 1 -Type DWord -ErrorAction SilentlyContinue
            }
            'Balanced' {
                Set-ItemProperty -Path $RegPath -Name 'VisualFXSetting' -Value 0 -Type DWord
                
                # Enable essential effects only
                $UserPreference = [byte[]](0x90, 0x32, 0x07, 0x80, 0x10, 0x00, 0x00, 0x00)
                Set-ItemProperty -Path 'HKCU:\Control Panel\Desktop' -Name 'UserPreferencesMask' -Value $UserPreference -Type Binary
                Set-ItemProperty -Path 'HKCU:\Control Panel\Desktop' -Name 'MenuShowDelay' -Value '200' -Type String
                Set-ItemProperty -Path 'HKCU:\Control Panel\Desktop\WindowMetrics' -Name 'MinAnimate' -Value '1' -Type String
            }
        }
        
        return [PSCustomObject]@{
            Success = $true
            Preset = $Preset
            Message = 'Visual effects updated. Sign out and back in for full effect.'
        }
    }
    catch {
        Write-Error "Failed to set visual effects: $_"
        return [PSCustomObject]@{ Success = $false; Error = $_.Exception.Message }
    }
}
