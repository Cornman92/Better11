<#
.SYNOPSIS
    Registry tweaks and modifications

.DESCRIPTION
    Provides safe registry modification functions for system optimization
#>

using module .\Base.psm1
using module .\Safety.psm1

# Registry tweak class
class RegistryTweak {
    [string]$Name
    [string]$Description
    [string]$Path
    [string]$ValueName
    [object]$Value
    [Microsoft.Win32.RegistryValueKind]$Type
    [string]$Category
    
    RegistryTweak(
        [string]$Name,
        [string]$Description,
        [string]$Path,
        [string]$ValueName,
        [object]$Value
    ) {
        $this.Name = $Name
        $this.Description = $Description
        $this.Path = $Path
        $this.ValueName = $ValueName
        $this.Value = $Value
        $this.Type = [Microsoft.Win32.RegistryValueKind]::DWord
        $this.Category = "general"
    }
}

# Registry Manager class
class RegistryManager : RegistryTool {
    [System.Collections.Generic.List[RegistryTweak]]$Tweaks
    
    RegistryManager([hashtable]$Config = @{}, [bool]$DryRun = $false) : base($Config, $DryRun) {
        $this.Tweaks = [System.Collections.Generic.List[RegistryTweak]]::new()
        $this.InitializeTweaks()
    }
    
    [ToolMetadata] GetMetadata() {
        return [ToolMetadata]::new(
            "Registry Manager",
            "Apply registry tweaks and optimizations",
            "0.3.0"
        )
    }
    
    [void] ValidateEnvironment() {
        Test-WindowsPlatform
    }
    
    [bool] Execute() {
        $this.Log("Registry Manager executed")
        return $true
    }
    
    # Initialize common tweaks
    [void] InitializeTweaks() {
        # Disable Windows telemetry
        $this.Tweaks.Add([RegistryTweak]::new(
            "DisableTelemetry",
            "Disable Windows telemetry data collection",
            "HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection",
            "AllowTelemetry",
            0
        ))
        
        # Disable Cortana
        $this.Tweaks.Add([RegistryTweak]::new(
            "DisableCortana",
            "Disable Cortana voice assistant",
            "HKLM:\SOFTWARE\Policies\Microsoft\Windows\Windows Search",
            "AllowCortana",
            0
        ))
        
        # Disable Windows Tips
        $this.Tweaks.Add([RegistryTweak]::new(
            "DisableWindowsTips",
            "Disable Windows tips and suggestions",
            "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager",
            "SubscribedContent-338389Enabled",
            0
        ))
        
        # Show file extensions
        $this.Tweaks.Add([RegistryTweak]::new(
            "ShowFileExtensions",
            "Show file extensions in Explorer",
            "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
            "HideFileExt",
            0
        ))
    }
    
    # Apply a single tweak
    [bool] ApplyTweak([RegistryTweak]$Tweak) {
        if ($this.DryRun) {
            $this.Log("DRY RUN: Would apply tweak '$($Tweak.Name)'")
            return $true
        }
        
        try {
            $this.Log("Applying tweak: $($Tweak.Name)")
            
            # Backup first
            if ($this.Config.BackupRegistry) {
                try {
                    Backup-RegistryKey -KeyPath $Tweak.Path -ErrorAction SilentlyContinue
                }
                catch {
                    $this.LogWarning("Failed to backup registry: $_")
                }
            }
            
            # Ensure path exists
            if (-not (Test-Path $Tweak.Path)) {
                New-Item -Path $Tweak.Path -Force | Out-Null
            }
            
            # Set the value
            Set-ItemProperty -Path $Tweak.Path `
                           -Name $Tweak.ValueName `
                           -Value $Tweak.Value `
                           -Type $Tweak.Type `
                           -ErrorAction Stop
            
            $this.Log("Applied tweak: $($Tweak.Name)")
            return $true
        }
        catch {
            $this.LogError("Failed to apply tweak '$($Tweak.Name)': $_")
            throw [SafetyError]::new("Failed to apply registry tweak: $_")
        }
    }
    
    # Apply multiple tweaks
    [hashtable] ApplyTweaks([string[]]$TweakNames) {
        $results = @{
            Success = [System.Collections.Generic.List[string]]::new()
            Failed = [System.Collections.Generic.List[string]]::new()
        }
        
        foreach ($name in $TweakNames) {
            $tweak = $this.Tweaks | Where-Object { $_.Name -eq $name } | Select-Object -First 1
            
            if (-not $tweak) {
                $this.LogWarning("Tweak not found: $name")
                $results.Failed.Add($name)
                continue
            }
            
            try {
                if ($this.ApplyTweak($tweak)) {
                    $results.Success.Add($name)
                }
                else {
                    $results.Failed.Add($name)
                }
            }
            catch {
                $results.Failed.Add($name)
            }
        }
        
        return $results
    }
    
    # List available tweaks
    [RegistryTweak[]] ListTweaks([string]$Category = $null) {
        if ($Category) {
            return $this.Tweaks | Where-Object { $_.Category -eq $Category }
        }
        return $this.Tweaks.ToArray()
    }
}

# Convenience functions
function Get-RegistryTweaks {
    <#
    .SYNOPSIS
        Get available registry tweaks
    
    .PARAMETER Category
        Filter by category
    
    .EXAMPLE
        Get-RegistryTweaks
        Get-RegistryTweaks -Category "privacy"
    #>
    [CmdletBinding()]
    param(
        [string]$Category
    )
    
    $manager = [RegistryManager]::new()
    return $manager.ListTweaks($Category)
}

function Set-RegistryTweak {
    <#
    .SYNOPSIS
        Apply a registry tweak
    
    .PARAMETER Name
        Name of the tweak to apply
    
    .PARAMETER DryRun
        Simulate the operation
    
    .EXAMPLE
        Set-RegistryTweak -Name "DisableTelemetry"
    #>
    [CmdletBinding(SupportsShouldProcess=$true)]
    param(
        [Parameter(Mandatory=$true)]
        [string]$Name,
        
        [switch]$DryRun
    )
    
    $manager = [RegistryManager]::new(@{}, $DryRun)
    $tweak = $manager.Tweaks | Where-Object { $_.Name -eq $Name } | Select-Object -First 1
    
    if (-not $tweak) {
        throw "Tweak not found: $Name"
    }
    
    if ($PSCmdlet.ShouldProcess($tweak.Name, "Apply registry tweak")) {
        return $manager.ApplyTweak($tweak)
    }
}

Export-ModuleMember -Function Get-RegistryTweaks, Set-RegistryTweak
