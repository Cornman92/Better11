function Set-Better11PrivacySetting {
    <#
    .SYNOPSIS
        Configures Windows privacy settings.
    
    .DESCRIPTION
        Modifies Windows privacy and telemetry settings for enhanced privacy.
        Supports multiple privacy presets and individual setting configuration.
    
    .PARAMETER Preset
        Use a predefined privacy preset (MaximumPrivacy, Balanced, Default).
    
    .PARAMETER TelemetryLevel
        Set Windows telemetry level (Security, Basic, Enhanced, Full).
    
    .PARAMETER DisableAdvertisingID
        Disable advertising ID.
    
    .PARAMETER DisableCortana
        Disable Cortana.
    
    .PARAMETER Force
        Skip confirmation prompts.
    
    .EXAMPLE
        Set-Better11PrivacySetting -Preset MaximumPrivacy
    
    .EXAMPLE
        Set-Better11PrivacySetting -TelemetryLevel Basic -DisableAdvertisingID
    
    .OUTPUTS
        PSCustomObject
        Configuration results.
    #>
    
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(ParameterSetName = 'Preset')]
        [ValidateSet('MaximumPrivacy', 'Balanced', 'Default')]
        [string]$Preset,
        
        [Parameter(ParameterSetName = 'Custom')]
        [ValidateSet('Security', 'Basic', 'Enhanced', 'Full')]
        [string]$TelemetryLevel,
        
        [Parameter(ParameterSetName = 'Custom')]
        [switch]$DisableAdvertisingID,
        
        [Parameter(ParameterSetName = 'Custom')]
        [switch]$DisableCortana,
        
        [Parameter()]
        [switch]$Force
    )
    
    begin {
        Write-Better11Log -Message "Configuring privacy settings" -Level Info
        
        if (-not (Test-Better11Administrator)) {
            throw "Privacy configuration requires administrator privileges"
        }
    }
    
    process {
        try {
            # Confirm
            if (-not $Force) {
                $message = if ($Preset) { "Apply $Preset preset?" } else { "Apply custom privacy settings?" }
                $confirmed = Confirm-Better11Action -Prompt $message
                if (-not $confirmed) {
                    throw "Privacy configuration cancelled by user"
                }
            }
            
            # Create restore point
            if ($PSCmdlet.ShouldProcess("System", "Create restore point")) {
                New-Better11RestorePoint -Description "Before privacy settings change" | Out-Null
            }
            
            $results = @()
            
            # Apply preset or custom settings
            if ($Preset -eq 'MaximumPrivacy' -or $TelemetryLevel -eq 'Basic' -or $TelemetryLevel -eq 'Security') {
                # Set telemetry to basic/security
                $tweaks = @(
                    @{
                        Hive = 'HKLM'
                        Path = 'SOFTWARE\Policies\Microsoft\Windows\DataCollection'
                        Name = 'AllowTelemetry'
                        Value = if ($TelemetryLevel -eq 'Security') { 0 } else { 1 }
                        Type = 'DWord'
                    }
                )
                
                $result = Set-Better11RegistryTweak -Tweaks $tweaks -Force -NoRestorePoint
                $results += $result.Details
            }
            
            if ($DisableAdvertisingID -or $Preset -eq 'MaximumPrivacy') {
                # Disable advertising ID
                $tweaks = @(
                    @{
                        Hive = 'HKCU'
                        Path = 'SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo'
                        Name = 'Enabled'
                        Value = 0
                        Type = 'DWord'
                    }
                )
                
                $result = Set-Better11RegistryTweak -Tweaks $tweaks -Force -NoRestorePoint
                $results += $result.Details
            }
            
            if ($DisableCortana -or $Preset -eq 'MaximumPrivacy') {
                # Disable Cortana
                $tweaks = @(
                    @{
                        Hive = 'HKLM'
                        Path = 'SOFTWARE\Policies\Microsoft\Windows\Windows Search'
                        Name = 'AllowCortana'
                        Value = 0
                        Type = 'DWord'
                    }
                )
                
                $result = Set-Better11RegistryTweak -Tweaks $tweaks -Force -NoRestorePoint
                $results += $result.Details
            }
            
            Write-Better11Log -Message "Privacy settings applied successfully" -Level Info
            
            return [PSCustomObject]@{
                Preset = $Preset
                SettingsApplied = $results.Count
                Success = $true
                Details = $results
            }
        }
        catch {
            Write-Better11Log -Message "Failed to apply privacy settings: $_" -Level Error
            throw
        }
    }
}
