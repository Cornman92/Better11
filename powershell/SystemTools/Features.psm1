<#
.SYNOPSIS
    Windows features and capabilities management.

.DESCRIPTION
    Provides functionality to enable, disable, and manage Windows optional features
    and capabilities. Includes recommendations for unnecessary features.
#>

using module .\Base.psm1
using module .\Safety.psm1

# Feature recommendation class
class FeatureRecommendation {
    [string]$Name
    [string]$DisplayName
    [string]$State
    [string]$RecommendedAction
    [string]$Reason
    [string]$Category
    [bool]$RequiresRestart
    
    FeatureRecommendation(
        [string]$Name,
        [string]$DisplayName,
        [string]$State,
        [string]$RecommendedAction,
        [string]$Reason
    ) {
        $this.Name = $Name
        $this.DisplayName = $DisplayName
        $this.State = $State
        $this.RecommendedAction = $RecommendedAction
        $this.Reason = $Reason
        $this.Category = "performance"
        $this.RequiresRestart = $true
    }
}

# Windows capability class
class WindowsCapability {
    [string]$Name
    [string]$State
    [string]$Description
    [bool]$IsRecommendedRemoval
    
    WindowsCapability(
        [string]$Name,
        [string]$State,
        [string]$Description,
        [bool]$IsRecommendedRemoval
    ) {
        $this.Name = $Name
        $this.State = $State
        $this.Description = $Description
        $this.IsRecommendedRemoval = $IsRecommendedRemoval
    }
}

# Features Manager class
class FeaturesManager : SystemTool {
    [System.Collections.Generic.List[FeatureRecommendation]]$Recommendations
    [System.Collections.Generic.List[string]]$UnnecessaryCapabilities
    
    FeaturesManager([hashtable]$Config = @{}, [bool]$DryRun = $false) : base($Config, $DryRun) {
        $this.Recommendations = [System.Collections.Generic.List[FeatureRecommendation]]::new()
        $this.UnnecessaryCapabilities = [System.Collections.Generic.List[string]]::new()
        $this.InitializeRecommendations()
        $this.InitializeUnnecessaryCapabilities()
    }
    
    [ToolMetadata] GetMetadata() {
        return [ToolMetadata]::new(
            "Features Manager",
            "Manage Windows optional features and capabilities",
            "0.3.0"
        )
    }
    
    [void] ValidateEnvironment() {
        Test-WindowsPlatform
        Assert-AdminPrivileges "Features management requires administrator privileges"
    }
    
    [bool] Execute() {
        $features = $this.ListWindowsFeatures()
        $this.Log("Found $($features.Count) Windows features")
        return $true
    }
    
    # Initialize feature recommendations
    [void] InitializeRecommendations() {
        # Internet Explorer 11 (deprecated)
        $this.Recommendations.Add([FeatureRecommendation]::new(
            "Internet-Explorer-Optional-amd64",
            "Internet Explorer 11",
            "Unknown",
            "Disable",
            "IE11 is deprecated - use Edge instead"
        ))
        
        # Windows Media Player (rarely used)
        $this.Recommendations.Add([FeatureRecommendation]::new(
            "WindowsMediaPlayer",
            "Windows Media Player",
            "Unknown",
            "Disable",
            "Rarely used - modern media players recommended"
        ))
        
        # Work Folders Client (enterprise only)
        $this.Recommendations.Add([FeatureRecommendation]::new(
            "WorkFolders-Client",
            "Work Folders Client",
            "Unknown",
            "Disable",
            "Enterprise feature - disable if not used"
        ))
        
        # XPS Services (rarely used document format)
        $this.Recommendations.Add([FeatureRecommendation]::new(
            "Printing-XPSServices-Features",
            "XPS Services",
            "Unknown",
            "Disable",
            "XPS format rarely used"
        ))
        
        # SMB 1.0 (security risk)
        $this.Recommendations.Add([FeatureRecommendation]::new(
            "SMB1Protocol",
            "SMB 1.0/CIFS File Sharing Support",
            "Unknown",
            "Disable",
            "SECURITY RISK - Use SMB 2.0+ instead"
        ))
        
        # Windows Fax and Scan
        $this.Recommendations.Add([FeatureRecommendation]::new(
            "FaxServicesClientPackage",
            "Windows Fax and Scan",
            "Unknown",
            "Disable",
            "Fax rarely used on modern systems"
        ))
    }
    
    # Initialize unnecessary capabilities
    [void] InitializeUnnecessaryCapabilities() {
        # Math Recognizer (handwriting math)
        $this.UnnecessaryCapabilities.Add("MathRecognizer")
        
        # Quick Assist (remote assistance)
        $this.UnnecessaryCapabilities.Add("App.Support.QuickAssist")
        
        # Windows Hello Face (if no camera)
        $this.UnnecessaryCapabilities.Add("Hello.Face")
        
        # Steps Recorder
        $this.UnnecessaryCapabilities.Add("App.StepsRecorder")
    }
    
    # List all Windows optional features
    [object[]] ListWindowsFeatures() {
        try {
            $features = Get-WindowsOptionalFeature -Online -ErrorAction Stop
            return $features
        }
        catch {
            $this.LogError("Failed to list Windows features: $_")
            return @()
        }
    }
    
    # List Windows capabilities
    [WindowsCapability[]] ListWindowsCapabilities() {
        $capabilities = [System.Collections.Generic.List[WindowsCapability]]::new()
        
        try {
            $caps = Get-WindowsCapability -Online -ErrorAction Stop
            
            foreach ($cap in $caps) {
                $isUnnecessary = $this.UnnecessaryCapabilities -contains $cap.Name
                
                $capability = [WindowsCapability]::new(
                    $cap.Name,
                    $cap.State,
                    $cap.Description,
                    $isUnnecessary
                )
                
                $capabilities.Add($capability)
            }
        }
        catch {
            $this.LogError("Failed to list Windows capabilities: $_")
        }
        
        return $capabilities.ToArray()
    }
    
    # Get feature recommendations
    [FeatureRecommendation[]] GetRecommendations() {
        $activeRecommendations = [System.Collections.Generic.List[FeatureRecommendation]]::new()
        
        try {
            $features = Get-WindowsOptionalFeature -Online -ErrorAction Stop
            
            foreach ($rec in $this.Recommendations) {
                $feature = $features | Where-Object { $_.FeatureName -eq $rec.Name } | Select-Object -First 1
                
                if ($feature) {
                    $rec.State = $feature.State
                    
                    # Only recommend if feature is enabled and action is to disable
                    if ($feature.State -eq "Enabled" -and $rec.RecommendedAction -eq "Disable") {
                        $activeRecommendations.Add($rec)
                    }
                    # Or if feature is disabled and action is to enable
                    elseif ($feature.State -eq "Disabled" -and $rec.RecommendedAction -eq "Enable") {
                        $activeRecommendations.Add($rec)
                    }
                }
            }
        }
        catch {
            $this.LogError("Failed to get recommendations: $_")
        }
        
        return $activeRecommendations.ToArray()
    }
    
    # Enable a Windows feature
    [bool] EnableFeature([string]$FeatureName) {
        if ($this.DryRun) {
            $this.Log("DRY RUN: Would enable feature '$FeatureName'")
            return $true
        }
        
        try {
            $this.Log("Enabling Windows feature: $FeatureName")
            
            Enable-WindowsOptionalFeature -Online `
                                         -FeatureName $FeatureName `
                                         -NoRestart `
                                         -ErrorAction Stop | Out-Null
            
            $this.Log("Enabled feature: $FeatureName (restart required)")
            return $true
        }
        catch {
            $this.LogError("Failed to enable feature ${FeatureName}: $_")
            throw [SafetyError]::new("Failed to enable Windows feature: $_")
        }
    }
    
    # Disable a Windows feature
    [bool] DisableFeature([string]$FeatureName) {
        if ($this.DryRun) {
            $this.Log("DRY RUN: Would disable feature '$FeatureName'")
            return $true
        }
        
        try {
            $this.Log("Disabling Windows feature: $FeatureName")
            
            Disable-WindowsOptionalFeature -Online `
                                          -FeatureName $FeatureName `
                                          -NoRestart `
                                          -ErrorAction Stop | Out-Null
            
            $this.Log("Disabled feature: $FeatureName (restart required)")
            return $true
        }
        catch {
            $this.LogError("Failed to disable feature ${FeatureName}: $_")
            throw [SafetyError]::new("Failed to disable Windows feature: $_")
        }
    }
    
    # Remove a Windows capability
    [bool] RemoveCapability([string]$CapabilityName) {
        if ($this.DryRun) {
            $this.Log("DRY RUN: Would remove capability '$CapabilityName'")
            return $true
        }
        
        try {
            $this.Log("Removing Windows capability: $CapabilityName")
            
            # Find the full capability name
            $caps = Get-WindowsCapability -Online | Where-Object { $_.Name -like "*$CapabilityName*" }
            
            foreach ($cap in $caps) {
                if ($cap.State -eq "Installed") {
                    Remove-WindowsCapability -Online `
                                           -Name $cap.Name `
                                           -ErrorAction Stop | Out-Null
                    
                    $this.Log("Removed capability: $($cap.Name)")
                }
            }
            
            return $true
        }
        catch {
            $this.LogError("Failed to remove capability ${CapabilityName}: $_")
            throw [SafetyError]::new("Failed to remove Windows capability: $_")
        }
    }
    
    # Apply feature recommendations
    [hashtable] ApplyRecommendations([string[]]$FeatureNames = $null) {
        $results = @{
            Success = [System.Collections.Generic.List[string]]::new()
            Failed = [System.Collections.Generic.List[string]]::new()
            Skipped = [System.Collections.Generic.List[string]]::new()
        }
        
        $recommendations = $this.GetRecommendations()
        
        foreach ($rec in $recommendations) {
            # If feature names specified, only apply those
            if ($FeatureNames -and $rec.Name -notin $FeatureNames) {
                $results.Skipped.Add($rec.Name)
                continue
            }
            
            try {
                $success = $false
                
                if ($rec.RecommendedAction -eq "Disable") {
                    $success = $this.DisableFeature($rec.Name)
                }
                elseif ($rec.RecommendedAction -eq "Enable") {
                    $success = $this.EnableFeature($rec.Name)
                }
                
                if ($success) {
                    $results.Success.Add($rec.Name)
                }
                else {
                    $results.Failed.Add($rec.Name)
                }
            }
            catch {
                $results.Failed.Add($rec.Name)
            }
        }
        
        return $results
    }
    
    # Remove unnecessary capabilities
    [hashtable] RemoveUnnecessaryCapabilities() {
        $results = @{
            Success = [System.Collections.Generic.List[string]]::new()
            Failed = [System.Collections.Generic.List[string]]::new()
        }
        
        foreach ($capName in $this.UnnecessaryCapabilities) {
            try {
                if ($this.RemoveCapability($capName)) {
                    $results.Success.Add($capName)
                }
                else {
                    $results.Failed.Add($capName)
                }
            }
            catch {
                $results.Failed.Add($capName)
            }
        }
        
        return $results
    }
    
    # Get feature by name
    [object] GetFeature([string]$FeatureName) {
        try {
            $features = Get-WindowsOptionalFeature -Online
            return $features | Where-Object { $_.FeatureName -eq $FeatureName } | Select-Object -First 1
        }
        catch {
            $this.LogError("Failed to get feature ${FeatureName}: $_")
            return $null
        }
    }
    
    # Check if restart is required
    [bool] IsRestartRequired() {
        try {
            # Check registry for pending restart
            $reboot = $false
            
            if (Test-Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing\RebootPending") {
                $reboot = $true
            }
            if (Test-Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsUpdate\Auto Update\RebootRequired") {
                $reboot = $true
            }
            
            return $reboot
        }
        catch {
            return $false
        }
    }
}

# Convenience functions
function Get-WindowsFeaturesRecommendations {
    <#
    .SYNOPSIS
        Get Windows features optimization recommendations
    
    .EXAMPLE
        Get-WindowsFeaturesRecommendations | Format-Table
    #>
    [CmdletBinding()]
    param()
    
    $manager = [FeaturesManager]::new()
    return $manager.GetRecommendations()
}

function Get-WindowsCapabilitiesList {
    <#
    .SYNOPSIS
        List Windows capabilities
    
    .EXAMPLE
        Get-WindowsCapabilitiesList | Where-Object { $_.IsRecommendedRemoval }
    #>
    [CmdletBinding()]
    param()
    
    $manager = [FeaturesManager]::new()
    return $manager.ListWindowsCapabilities()
}

function Disable-WindowsFeature {
    <#
    .SYNOPSIS
        Disable a Windows optional feature
    
    .PARAMETER FeatureName
        Name of the feature to disable
    
    .EXAMPLE
        Disable-WindowsFeature -FeatureName "Internet-Explorer-Optional-amd64"
    
    .NOTES
        Requires administrator privileges and system restart
    #>
    [CmdletBinding(SupportsShouldProcess=$true, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory=$true)]
        [string]$FeatureName
    )
    
    if ($PSCmdlet.ShouldProcess($FeatureName, "Disable Windows feature (requires restart)")) {
        $manager = [FeaturesManager]::new()
        $result = $manager.DisableFeature($FeatureName)
        
        if ($result) {
            Write-Warning "Feature disabled. System restart required."
        }
        
        return $result
    }
}

function Enable-WindowsFeature {
    <#
    .SYNOPSIS
        Enable a Windows optional feature
    
    .PARAMETER FeatureName
        Name of the feature to enable
    
    .EXAMPLE
        Enable-WindowsFeature -FeatureName "WindowsMediaPlayer"
    
    .NOTES
        Requires administrator privileges and system restart
    #>
    [CmdletBinding(SupportsShouldProcess=$true, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory=$true)]
        [string]$FeatureName
    )
    
    if ($PSCmdlet.ShouldProcess($FeatureName, "Enable Windows feature (requires restart)")) {
        $manager = [FeaturesManager]::new()
        $result = $manager.EnableFeature($FeatureName)
        
        if ($result) {
            Write-Warning "Feature enabled. System restart required."
        }
        
        return $result
    }
}

function Optimize-WindowsFeatures {
    <#
    .SYNOPSIS
        Apply all Windows features optimization recommendations
    
    .PARAMETER FeatureNames
        Specific features to optimize (optional)
    
    .EXAMPLE
        Optimize-WindowsFeatures
        Optimize-WindowsFeatures -FeatureNames @("SMB1Protocol")
    
    .NOTES
        Requires administrator privileges and system restart
    #>
    [CmdletBinding(SupportsShouldProcess=$true, ConfirmImpact='High')]
    param(
        [string[]]$FeatureNames
    )
    
    if ($PSCmdlet.ShouldProcess("Windows features", "Apply optimization recommendations (requires restart)")) {
        $manager = [FeaturesManager]::new()
        $results = $manager.ApplyRecommendations($FeatureNames)
        
        Write-Host "`nResults:"
        Write-Host "Success: $($results.Success.Count)" -ForegroundColor Green
        Write-Host "Failed: $($results.Failed.Count)" -ForegroundColor Red
        Write-Host "Skipped: $($results.Skipped.Count)" -ForegroundColor Yellow
        
        if ($results.Success.Count -gt 0) {
            Write-Warning "`nSystem restart required to apply changes."
        }
        
        return $results
    }
}

function Remove-UnnecessaryCapabilities {
    <#
    .SYNOPSIS
        Remove unnecessary Windows capabilities
    
    .EXAMPLE
        Remove-UnnecessaryCapabilities
    
    .NOTES
        Requires administrator privileges
    #>
    [CmdletBinding(SupportsShouldProcess=$true, ConfirmImpact='High')]
    param()
    
    if ($PSCmdlet.ShouldProcess("Unnecessary Windows capabilities", "Remove")) {
        $manager = [FeaturesManager]::new()
        return $manager.RemoveUnnecessaryCapabilities()
    }
}

Export-ModuleMember -Function Get-WindowsFeaturesRecommendations, Get-WindowsCapabilitiesList, `
                              Disable-WindowsFeature, Enable-WindowsFeature, `
                              Optimize-WindowsFeatures, Remove-UnnecessaryCapabilities
