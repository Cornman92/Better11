<#
.SYNOPSIS
    Windows Update management and optimization.

.DESCRIPTION
    Provides functionality to manage Windows Update settings, including
    automatic updates, defer updates, and update policies.
#>

using module .\Base.psm1
using module .\Safety.psm1

# Update policy enumeration
enum UpdatePolicy {
    Automatic          # Automatic updates (default)
    NotifyDownload     # Notify before download
    NotifyInstall      # Notify before install
    Disabled           # Updates disabled (not recommended)
    Metered            # Treat connection as metered
}

# Update deferral class
class UpdateDeferral {
    [int]$FeatureUpdatesDays
    [int]$QualityUpdatesDays
    [bool]$PauseFeatureUpdates
    [bool]$PauseQualityUpdates
    
    UpdateDeferral() {
        $this.FeatureUpdatesDays = 0
        $this.QualityUpdatesDays = 0
        $this.PauseFeatureUpdates = $false
        $this.PauseQualityUpdates = $false
    }
}

# Updates Manager class
class UpdatesManager : SystemTool {
    
    UpdatesManager([hashtable]$Config = @{}, [bool]$DryRun = $false) : base($Config, $DryRun) {
    }
    
    [ToolMetadata] GetMetadata() {
        return [ToolMetadata]::new(
            "Updates Manager",
            "Manage Windows Update settings and policies",
            "0.3.0"
        )
    }
    
    [void] ValidateEnvironment() {
        Test-WindowsPlatform
        Assert-AdminPrivileges "Updates management requires administrator privileges"
    }
    
    [bool] Execute() {
        $this.Log("Updates Manager executed")
        return $true
    }
    
    # Set update policy
    [bool] SetUpdatePolicy([UpdatePolicy]$Policy) {
        if ($this.DryRun) {
            $this.Log("DRY RUN: Would set update policy to $Policy")
            return $true
        }
        
        try {
            $this.Log("Setting update policy to: $Policy")
            
            $policyPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU"
            
            # Ensure path exists
            if (-not (Test-Path $policyPath)) {
                New-Item -Path $policyPath -Force | Out-Null
            }
            
            switch ($Policy) {
                Automatic {
                    # Automatic updates
                    Set-ItemProperty -Path $policyPath -Name "NoAutoUpdate" -Value 0 -Type DWord
                    Set-ItemProperty -Path $policyPath -Name "AUOptions" -Value 4 -Type DWord
                }
                NotifyDownload {
                    # Notify before download
                    Set-ItemProperty -Path $policyPath -Name "NoAutoUpdate" -Value 0 -Type DWord
                    Set-ItemProperty -Path $policyPath -Name "AUOptions" -Value 2 -Type DWord
                }
                NotifyInstall {
                    # Notify before install
                    Set-ItemProperty -Path $policyPath -Name "NoAutoUpdate" -Value 0 -Type DWord
                    Set-ItemProperty -Path $policyPath -Name "AUOptions" -Value 3 -Type DWord
                }
                Disabled {
                    # Disabled (NOT RECOMMENDED)
                    Set-ItemProperty -Path $policyPath -Name "NoAutoUpdate" -Value 1 -Type DWord
                    $this.LogWarning("Windows Update has been disabled. This is a security risk!")
                }
                Metered {
                    # Set connection as metered to limit updates
                    $this.SetMeteredConnection($true)
                }
            }
            
            $this.Log("Update policy set to: $Policy")
            return $true
        }
        catch {
            $this.LogError("Failed to set update policy: $_")
            throw [SafetyError]::new("Failed to set update policy: $_")
        }
    }
    
    # Set metered connection
    [bool] SetMeteredConnection([bool]$Enabled) {
        if ($this.DryRun) {
            $this.Log("DRY RUN: Would set metered connection to $Enabled")
            return $true
        }
        
        try {
            $this.Log("Setting metered connection: $Enabled")
            
            $interfacePath = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\NetworkList\DefaultMediaCost"
            
            if (-not (Test-Path $interfacePath)) {
                New-Item -Path $interfacePath -Force | Out-Null
            }
            
            # Set metered for all network types
            $value = if ($Enabled) { 2 } else { 1 }
            Set-ItemProperty -Path $interfacePath -Name "Ethernet" -Value $value -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $interfacePath -Name "WiFi" -Value $value -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $interfacePath -Name "Default" -Value $value -Type DWord -ErrorAction SilentlyContinue
            
            $this.Log("Metered connection set to: $Enabled")
            return $true
        }
        catch {
            $this.LogError("Failed to set metered connection: $_")
            return $false
        }
    }
    
    # Defer updates
    [bool] DeferUpdates([int]$FeatureDays, [int]$QualityDays) {
        if ($this.DryRun) {
            $this.Log("DRY RUN: Would defer feature updates $FeatureDays days, quality updates $QualityDays days")
            return $true
        }
        
        try {
            $this.Log("Deferring updates: Feature=$FeatureDays days, Quality=$QualityDays days")
            
            $deferPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate"
            
            if (-not (Test-Path $deferPath)) {
                New-Item -Path $deferPath -Force | Out-Null
            }
            
            # Set deferral periods (0-365 days)
            if ($FeatureDays -ge 0 -and $FeatureDays -le 365) {
                Set-ItemProperty -Path $deferPath -Name "DeferFeatureUpdates" -Value 1 -Type DWord
                Set-ItemProperty -Path $deferPath -Name "DeferFeatureUpdatesPeriodInDays" -Value $FeatureDays -Type DWord
            }
            
            if ($QualityDays -ge 0 -and $QualityDays -le 30) {
                Set-ItemProperty -Path $deferPath -Name "DeferQualityUpdates" -Value 1 -Type DWord
                Set-ItemProperty -Path $deferPath -Name "DeferQualityUpdatesPeriodInDays" -Value $QualityDays -Type DWord
            }
            
            $this.Log("Updates deferred successfully")
            return $true
        }
        catch {
            $this.LogError("Failed to defer updates: $_")
            throw [SafetyError]::new("Failed to defer updates: $_")
        }
    }
    
    # Pause updates
    [bool] PauseUpdates([int]$Days) {
        if ($this.DryRun) {
            $this.Log("DRY RUN: Would pause updates for $Days days")
            return $true
        }
        
        try {
            $this.Log("Pausing updates for $Days days")
            
            $pausePath = "HKLM:\SOFTWARE\Microsoft\WindowsUpdate\UX\Settings"
            
            if (-not (Test-Path $pausePath)) {
                New-Item -Path $pausePath -Force | Out-Null
            }
            
            # Calculate pause end date
            $pauseEnd = (Get-Date).AddDays($Days).ToString("yyyy-MM-ddTHH:mm:ssZ")
            
            Set-ItemProperty -Path $pausePath -Name "PauseUpdatesExpiryTime" -Value $pauseEnd -Type String
            Set-ItemProperty -Path $pausePath -Name "PauseFeatureUpdatesEndTime" -Value $pauseEnd -Type String
            Set-ItemProperty -Path $pausePath -Name "PauseQualityUpdatesEndTime" -Value $pauseEnd -Type String
            
            $this.Log("Updates paused until: $pauseEnd")
            return $true
        }
        catch {
            $this.LogError("Failed to pause updates: $_")
            throw [SafetyError]::new("Failed to pause updates: $_")
        }
    }
    
    # Resume updates
    [bool] ResumeUpdates() {
        if ($this.DryRun) {
            $this.Log("DRY RUN: Would resume updates")
            return $true
        }
        
        try {
            $this.Log("Resuming updates")
            
            $pausePath = "HKLM:\SOFTWARE\Microsoft\WindowsUpdate\UX\Settings"
            
            if (Test-Path $pausePath) {
                Remove-ItemProperty -Path $pausePath -Name "PauseUpdatesExpiryTime" -ErrorAction SilentlyContinue
                Remove-ItemProperty -Path $pausePath -Name "PauseFeatureUpdatesEndTime" -ErrorAction SilentlyContinue
                Remove-ItemProperty -Path $pausePath -Name "PauseQualityUpdatesEndTime" -ErrorAction SilentlyContinue
            }
            
            $this.Log("Updates resumed")
            return $true
        }
        catch {
            $this.LogError("Failed to resume updates: $_")
            return $false
        }
    }
    
    # Disable automatic restart
    [bool] DisableAutomaticRestart() {
        if ($this.DryRun) {
            $this.Log("DRY RUN: Would disable automatic restart")
            return $true
        }
        
        try {
            $this.Log("Disabling automatic restart after updates")
            
            $restartPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU"
            
            if (-not (Test-Path $restartPath)) {
                New-Item -Path $restartPath -Force | Out-Null
            }
            
            Set-ItemProperty -Path $restartPath -Name "NoAutoRebootWithLoggedOnUsers" -Value 1 -Type DWord
            Set-ItemProperty -Path $restartPath -Name "AUOptions" -Value 3 -Type DWord
            
            $this.Log("Automatic restart disabled")
            return $true
        }
        catch {
            $this.LogError("Failed to disable automatic restart: $_")
            return $false
        }
    }
    
    # Enable automatic restart
    [bool] EnableAutomaticRestart() {
        if ($this.DryRun) {
            $this.Log("DRY RUN: Would enable automatic restart")
            return $true
        }
        
        try {
            $this.Log("Enabling automatic restart after updates")
            
            $restartPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU"
            
            if (Test-Path $restartPath) {
                Remove-ItemProperty -Path $restartPath -Name "NoAutoRebootWithLoggedOnUsers" -ErrorAction SilentlyContinue
            }
            
            $this.Log("Automatic restart enabled")
            return $true
        }
        catch {
            $this.LogError("Failed to enable automatic restart: $_")
            return $false
        }
    }
    
    # Disable driver updates
    [bool] DisableDriverUpdates() {
        if ($this.DryRun) {
            $this.Log("DRY RUN: Would disable driver updates")
            return $true
        }
        
        try {
            $this.Log("Disabling automatic driver updates")
            
            $driverPath = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\DriverSearching"
            
            if (-not (Test-Path $driverPath)) {
                New-Item -Path $driverPath -Force | Out-Null
            }
            
            Set-ItemProperty -Path $driverPath -Name "SearchOrderConfig" -Value 0 -Type DWord
            
            $this.Log("Driver updates disabled")
            return $true
        }
        catch {
            $this.LogError("Failed to disable driver updates: $_")
            return $false
        }
    }
    
    # Get current deferral settings
    [UpdateDeferral] GetDeferralSettings() {
        $deferral = [UpdateDeferral]::new()
        
        try {
            $deferPath = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate"
            
            if (Test-Path $deferPath) {
                $featureDays = Get-ItemProperty -Path $deferPath -Name "DeferFeatureUpdatesPeriodInDays" -ErrorAction SilentlyContinue
                $qualityDays = Get-ItemProperty -Path $deferPath -Name "DeferQualityUpdatesPeriodInDays" -ErrorAction SilentlyContinue
                
                if ($featureDays) {
                    $deferral.FeatureUpdatesDays = $featureDays.DeferFeatureUpdatesPeriodInDays
                }
                if ($qualityDays) {
                    $deferral.QualityUpdatesDays = $qualityDays.DeferQualityUpdatesPeriodInDays
                }
            }
        }
        catch {
            $this.LogWarning("Could not read deferral settings: $_")
        }
        
        return $deferral
    }
    
    # Check for updates
    [bool] CheckForUpdates() {
        try {
            $this.Log("Checking for Windows updates...")
            
            # Use Windows Update COM object
            $updateSession = New-Object -ComObject Microsoft.Update.Session
            $updateSearcher = $updateSession.CreateUpdateSearcher()
            
            $searchResult = $updateSearcher.Search("IsInstalled=0")
            
            $this.Log("Found $($searchResult.Updates.Count) available updates")
            
            return $true
        }
        catch {
            $this.LogError("Failed to check for updates: $_")
            return $false
        }
    }
}

# Convenience functions
function Set-WindowsUpdatePolicy {
    <#
    .SYNOPSIS
        Set Windows Update policy
    
    .PARAMETER Policy
        Update policy to apply
    
    .EXAMPLE
        Set-WindowsUpdatePolicy -Policy NotifyInstall
    #>
    [CmdletBinding(SupportsShouldProcess=$true)]
    param(
        [Parameter(Mandatory=$true)]
        [UpdatePolicy]$Policy
    )
    
    if ($PSCmdlet.ShouldProcess("Windows Update policy", "Set to $Policy")) {
        $manager = [UpdatesManager]::new()
        return $manager.SetUpdatePolicy($Policy)
    }
}

function Set-UpdateDeferral {
    <#
    .SYNOPSIS
        Defer Windows updates
    
    .PARAMETER FeatureDays
        Days to defer feature updates (0-365)
    
    .PARAMETER QualityDays
        Days to defer quality updates (0-30)
    
    .EXAMPLE
        Set-UpdateDeferral -FeatureDays 30 -QualityDays 7
    #>
    [CmdletBinding(SupportsShouldProcess=$true)]
    param(
        [Parameter(Mandatory=$true)]
        [ValidateRange(0, 365)]
        [int]$FeatureDays,
        
        [Parameter(Mandatory=$true)]
        [ValidateRange(0, 30)]
        [int]$QualityDays
    )
    
    if ($PSCmdlet.ShouldProcess("Windows updates", "Defer Feature=$FeatureDays days, Quality=$QualityDays days")) {
        $manager = [UpdatesManager]::new()
        return $manager.DeferUpdates($FeatureDays, $QualityDays)
    }
}

function Suspend-WindowsUpdates {
    <#
    .SYNOPSIS
        Pause Windows updates for specified days
    
    .PARAMETER Days
        Number of days to pause (1-35)
    
    .EXAMPLE
        Suspend-WindowsUpdates -Days 7
    #>
    [CmdletBinding(SupportsShouldProcess=$true)]
    param(
        [Parameter(Mandatory=$true)]
        [ValidateRange(1, 35)]
        [int]$Days
    )
    
    if ($PSCmdlet.ShouldProcess("Windows updates", "Pause for $Days days")) {
        $manager = [UpdatesManager]::new()
        return $manager.PauseUpdates($Days)
    }
}

function Resume-WindowsUpdates {
    <#
    .SYNOPSIS
        Resume Windows updates
    
    .EXAMPLE
        Resume-WindowsUpdates
    #>
    [CmdletBinding(SupportsShouldProcess=$true)]
    param()
    
    if ($PSCmdlet.ShouldProcess("Windows updates", "Resume")) {
        $manager = [UpdatesManager]::new()
        return $manager.ResumeUpdates()
    }
}

function Disable-UpdateAutoRestart {
    <#
    .SYNOPSIS
        Disable automatic restart after updates
    
    .EXAMPLE
        Disable-UpdateAutoRestart
    #>
    [CmdletBinding(SupportsShouldProcess=$true)]
    param()
    
    if ($PSCmdlet.ShouldProcess("Automatic restart", "Disable")) {
        $manager = [UpdatesManager]::new()
        return $manager.DisableAutomaticRestart()
    }
}

function Get-UpdateDeferralSettings {
    <#
    .SYNOPSIS
        Get current update deferral settings
    
    .EXAMPLE
        Get-UpdateDeferralSettings
    #>
    [CmdletBinding()]
    param()
    
    $manager = [UpdatesManager]::new()
    return $manager.GetDeferralSettings()
}

Export-ModuleMember -Function Set-WindowsUpdatePolicy, Set-UpdateDeferral, `
                              Suspend-WindowsUpdates, Resume-WindowsUpdates, `
                              Disable-UpdateAutoRestart, Get-UpdateDeferralSettings
