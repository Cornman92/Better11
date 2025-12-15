<#
.SYNOPSIS
    Windows privacy settings management.

.DESCRIPTION
    Provides functionality to configure Windows privacy settings,
    disable telemetry, and control data collection.
#>

using module .\Base.psm1
using module .\Safety.psm1
using module .\Registry.psm1

# Privacy setting class
class PrivacySetting {
    [string]$Name
    [string]$Description
    [string]$Category
    [scriptblock]$Apply
    [scriptblock]$Revert
    [bool]$IsApplied
    
    PrivacySetting(
        [string]$Name,
        [string]$Description,
        [string]$Category,
        [scriptblock]$Apply,
        [scriptblock]$Revert
    ) {
        $this.Name = $Name
        $this.Description = $Description
        $this.Category = $Category
        $this.Apply = $Apply
        $this.Revert = $Revert
        $this.IsApplied = $false
    }
}

# Privacy Manager class
class PrivacyManager : RegistryTool {
    [System.Collections.Generic.List[PrivacySetting]]$Settings
    
    PrivacyManager([hashtable]$Config = @{}, [bool]$DryRun = $false) : base($Config, $DryRun) {
        $this.Settings = [System.Collections.Generic.List[PrivacySetting]]::new()
        $this.InitializeSettings()
    }
    
    [ToolMetadata] GetMetadata() {
        return [ToolMetadata]::new(
            "Privacy Manager",
            "Configure Windows privacy and telemetry settings",
            "0.3.0"
        )
    }
    
    [void] ValidateEnvironment() {
        Test-WindowsPlatform
    }
    
    [bool] Execute() {
        $this.Log("Privacy Manager executed")
        return $true
    }
    
    # Initialize privacy settings
    [void] InitializeSettings() {
        # Telemetry
        $this.Settings.Add([PrivacySetting]::new(
            "DisableTelemetry",
            "Disable Windows telemetry and diagnostic data collection",
            "telemetry",
            {
                Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection" -Name "AllowTelemetry" -Value 0 -Type DWord -Force
                Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection" -Name "AllowTelemetry" -Value 0 -Type DWord -Force
            },
            {
                Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection" -Name "AllowTelemetry" -Value 3 -Type DWord -Force
                Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection" -Name "AllowTelemetry" -Value 3 -Type DWord -Force
            }
        ))
        
        # Advertising ID
        $this.Settings.Add([PrivacySetting]::new(
            "DisableAdvertisingID",
            "Disable advertising ID for personalized ads",
            "privacy",
            {
                if (-not (Test-Path "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo")) {
                    New-Item -Path "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo" -Force | Out-Null
                }
                Set-ItemProperty -Path "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo" -Name "Enabled" -Value 0 -Type DWord
            },
            {
                Set-ItemProperty -Path "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo" -Name "Enabled" -Value 1 -Type DWord
            }
        ))
        
        # Location tracking
        $this.Settings.Add([PrivacySetting]::new(
            "DisableLocation",
            "Disable location tracking",
            "privacy",
            {
                if (-not (Test-Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\LocationAndSensors")) {
                    New-Item -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\LocationAndSensors" -Force | Out-Null
                }
                Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\LocationAndSensors" -Name "DisableLocation" -Value 1 -Type DWord
            },
            {
                Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\LocationAndSensors" -Name "DisableLocation" -Value 0 -Type DWord
            }
        ))
        
        # Activity history
        $this.Settings.Add([PrivacySetting]::new(
            "DisableActivityHistory",
            "Disable activity history and timeline",
            "privacy",
            {
                if (-not (Test-Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\System")) {
                    New-Item -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\System" -Force | Out-Null
                }
                Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\System" -Name "EnableActivityFeed" -Value 0 -Type DWord
                Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\System" -Name "PublishUserActivities" -Value 0 -Type DWord
                Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\System" -Name "UploadUserActivities" -Value 0 -Type DWord
            },
            {
                Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\System" -Name "EnableActivityFeed" -Value 1 -Type DWord
                Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\System" -Name "PublishUserActivities" -Value 1 -Type DWord
                Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\System" -Name "UploadUserActivities" -Value 1 -Type DWord
            }
        ))
        
        # Cortana
        $this.Settings.Add([PrivacySetting]::new(
            "DisableCortana",
            "Disable Cortana voice assistant",
            "cortana",
            {
                if (-not (Test-Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\Windows Search")) {
                    New-Item -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\Windows Search" -Force | Out-Null
                }
                Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\Windows Search" -Name "AllowCortana" -Value 0 -Type DWord
            },
            {
                Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\Windows Search" -Name "AllowCortana" -Value 1 -Type DWord
            }
        ))
        
        # Windows Tips
        $this.Settings.Add([PrivacySetting]::new(
            "DisableWindowsTips",
            "Disable Windows tips and suggestions",
            "ui",
            {
                Set-ItemProperty -Path "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" -Name "SubscribedContent-338389Enabled" -Value 0 -Type DWord
                Set-ItemProperty -Path "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" -Name "SubscribedContent-338393Enabled" -Value 0 -Type DWord
                Set-ItemProperty -Path "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" -Name "SubscribedContent-353694Enabled" -Value 0 -Type DWord
                Set-ItemProperty -Path "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" -Name "SubscribedContent-353696Enabled" -Value 0 -Type DWord
            },
            {
                Set-ItemProperty -Path "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" -Name "SubscribedContent-338389Enabled" -Value 1 -Type DWord
                Set-ItemProperty -Path "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" -Name "SubscribedContent-338393Enabled" -Value 1 -Type DWord
                Set-ItemProperty -Path "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" -Name "SubscribedContent-353694Enabled" -Value 1 -Type DWord
                Set-ItemProperty -Path "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" -Name "SubscribedContent-353696Enabled" -Value 1 -Type DWord
            }
        ))
        
        # Feedback
        $this.Settings.Add([PrivacySetting]::new(
            "DisableFeedback",
            "Disable Windows feedback requests",
            "telemetry",
            {
                if (-not (Test-Path "HKCU:\SOFTWARE\Microsoft\Siuf\Rules")) {
                    New-Item -Path "HKCU:\SOFTWARE\Microsoft\Siuf\Rules" -Force | Out-Null
                }
                Set-ItemProperty -Path "HKCU:\SOFTWARE\Microsoft\Siuf\Rules" -Name "NumberOfSIUFInPeriod" -Value 0 -Type DWord
                Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection" -Name "DoNotShowFeedbackNotifications" -Value 1 -Type DWord
            },
            {
                Remove-ItemProperty -Path "HKCU:\SOFTWARE\Microsoft\Siuf\Rules" -Name "NumberOfSIUFInPeriod" -ErrorAction SilentlyContinue
                Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection" -Name "DoNotShowFeedbackNotifications" -Value 0 -Type DWord
            }
        ))
        
        # WiFi Sense
        $this.Settings.Add([PrivacySetting]::new(
            "DisableWiFiSense",
            "Disable WiFi Sense (sharing WiFi passwords)",
            "privacy",
            {
                if (-not (Test-Path "HKLM:\SOFTWARE\Microsoft\PolicyManager\default\WiFi\AllowWiFiHotSpotReporting")) {
                    New-Item -Path "HKLM:\SOFTWARE\Microsoft\PolicyManager\default\WiFi\AllowWiFiHotSpotReporting" -Force | Out-Null
                }
                Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\PolicyManager\default\WiFi\AllowWiFiHotSpotReporting" -Name "Value" -Value 0 -Type DWord
                Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\PolicyManager\default\WiFi\AllowAutoConnectToWiFiSenseHotspots" -Name "Value" -Value 0 -Type DWord
            },
            {
                Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\PolicyManager\default\WiFi\AllowWiFiHotSpotReporting" -Name "Value" -Value 1 -Type DWord
                Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\PolicyManager\default\WiFi\AllowAutoConnectToWiFiSenseHotspots" -Name "Value" -Value 1 -Type DWord
            }
        ))
        
        # Web search in Start Menu
        $this.Settings.Add([PrivacySetting]::new(
            "DisableWebSearch",
            "Disable web search in Start Menu",
            "search",
            {
                Set-ItemProperty -Path "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Search" -Name "BingSearchEnabled" -Value 0 -Type DWord
                Set-ItemProperty -Path "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Search" -Name "CortanaConsent" -Value 0 -Type DWord
            },
            {
                Set-ItemProperty -Path "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Search" -Name "BingSearchEnabled" -Value 1 -Type DWord
                Set-ItemProperty -Path "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Search" -Name "CortanaConsent" -Value 1 -Type DWord
            }
        ))
    }
    
    # Apply a privacy setting
    [bool] ApplySetting([PrivacySetting]$Setting) {
        if ($this.DryRun) {
            $this.Log("DRY RUN: Would apply setting '$($Setting.Name)'")
            return $true
        }
        
        try {
            $this.Log("Applying privacy setting: $($Setting.Name)")
            
            # Backup registry if configured
            if ($this.Config.BackupRegistry) {
                try {
                    # Backup would happen here
                    # Implementation depends on which keys are affected
                }
                catch {
                    $this.LogWarning("Failed to backup registry: $_")
                }
            }
            
            # Apply the setting
            & $Setting.Apply
            
            $this.Log("Applied: $($Setting.Name)")
            return $true
        }
        catch {
            $this.LogError("Failed to apply '$($Setting.Name)': $_")
            throw [SafetyError]::new("Failed to apply privacy setting: $_")
        }
    }
    
    # Revert a privacy setting
    [bool] RevertSetting([PrivacySetting]$Setting) {
        if ($this.DryRun) {
            $this.Log("DRY RUN: Would revert setting '$($Setting.Name)'")
            return $true
        }
        
        try {
            $this.Log("Reverting privacy setting: $($Setting.Name)")
            
            & $Setting.Revert
            
            $this.Log("Reverted: $($Setting.Name)")
            return $true
        }
        catch {
            $this.LogError("Failed to revert '$($Setting.Name)': $_")
            return $false
        }
    }
    
    # Apply multiple settings
    [hashtable] ApplySettings([string[]]$SettingNames = $null, [string]$Category = $null) {
        $results = @{
            Success = [System.Collections.Generic.List[string]]::new()
            Failed = [System.Collections.Generic.List[string]]::new()
        }
        
        $settingsToApply = $this.Settings
        
        # Filter by names
        if ($SettingNames) {
            $settingsToApply = $settingsToApply | Where-Object { $_.Name -in $SettingNames }
        }
        
        # Filter by category
        if ($Category) {
            $settingsToApply = $settingsToApply | Where-Object { $_.Category -eq $Category }
        }
        
        foreach ($setting in $settingsToApply) {
            try {
                if ($this.ApplySetting($setting)) {
                    $results.Success.Add($setting.Name)
                }
                else {
                    $results.Failed.Add($setting.Name)
                }
            }
            catch {
                $results.Failed.Add($setting.Name)
            }
        }
        
        return $results
    }
    
    # Apply all privacy settings
    [hashtable] ApplyAllPrivacySettings() {
        return $this.ApplySettings()
    }
    
    # List available settings
    [PrivacySetting[]] ListSettings([string]$Category = $null) {
        if ($Category) {
            return $this.Settings | Where-Object { $_.Category -eq $Category }
        }
        return $this.Settings.ToArray()
    }
}

# Convenience functions
function Get-PrivacySettings {
    <#
    .SYNOPSIS
        List available privacy settings
    
    .PARAMETER Category
        Filter by category (telemetry, privacy, cortana, etc.)
    
    .EXAMPLE
        Get-PrivacySettings
        Get-PrivacySettings -Category telemetry
    #>
    [CmdletBinding()]
    param(
        [string]$Category
    )
    
    $manager = [PrivacyManager]::new()
    return $manager.ListSettings($Category)
}

function Set-PrivacyConfiguration {
    <#
    .SYNOPSIS
        Apply a privacy setting
    
    .PARAMETER Name
        Name of the setting to apply
    
    .EXAMPLE
        Set-PrivacyConfiguration -Name "DisableTelemetry"
    #>
    [CmdletBinding(SupportsShouldProcess=$true)]
    param(
        [Parameter(Mandatory=$true)]
        [string]$Name
    )
    
    $manager = [PrivacyManager]::new()
    $setting = $manager.Settings | Where-Object { $_.Name -eq $Name } | Select-Object -First 1
    
    if (-not $setting) {
        throw "Privacy setting not found: $Name"
    }
    
    if ($PSCmdlet.ShouldProcess($setting.Name, "Apply privacy setting")) {
        return $manager.ApplySetting($setting)
    }
}

function Set-AllPrivacySettings {
    <#
    .SYNOPSIS
        Apply all privacy settings
    
    .PARAMETER Category
        Only apply settings from specific category
    
    .EXAMPLE
        Set-AllPrivacySettings
        Set-AllPrivacySettings -Category telemetry
    #>
    [CmdletBinding(SupportsShouldProcess=$true, ConfirmImpact='High')]
    param(
        [string]$Category
    )
    
    if ($PSCmdlet.ShouldProcess("All privacy settings", "Apply")) {
        $manager = [PrivacyManager]::new()
        return $manager.ApplySettings($null, $Category)
    }
}

Export-ModuleMember -Function Get-PrivacySettings, Set-PrivacyConfiguration, Set-AllPrivacySettings
