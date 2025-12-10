<#
.SYNOPSIS
    Windows performance optimization and tuning.

.DESCRIPTION
    Provides functionality to optimize Windows performance through visual effects,
    power settings, system responsiveness, and other performance-related tweaks.
#>

using module .\Base.psm1
using module .\Safety.psm1

# Performance preset enumeration
enum PerformancePreset {
    Maximum          # Maximum performance (disable all visual effects)
    Balanced         # Balance between performance and appearance
    Quality          # Best appearance (all visual effects enabled)
    Custom           # Custom configuration
}

# Power plan enumeration
enum PowerPlan {
    HighPerformance
    Balanced
    PowerSaver
    Ultimate         # Ultimate Performance (if available)
}

# Performance optimization class
class PerformanceOptimization {
    [string]$Name
    [string]$Description
    [string]$Category
    [scriptblock]$Apply
    [scriptblock]$Revert
    [int]$ExpectedImprovement  # Percentage
    
    PerformanceOptimization(
        [string]$Name,
        [string]$Description,
        [string]$Category,
        [scriptblock]$Apply,
        [scriptblock]$Revert,
        [int]$ExpectedImprovement
    ) {
        $this.Name = $Name
        $this.Description = $Description
        $this.Category = $Category
        $this.Apply = $Apply
        $this.Revert = $Revert
        $this.ExpectedImprovement = $ExpectedImprovement
    }
}

# Performance Manager class
class PerformanceManager : SystemTool {
    [System.Collections.Generic.List[PerformanceOptimization]]$Optimizations
    
    PerformanceManager([hashtable]$Config = @{}, [bool]$DryRun = $false) : base($Config, $DryRun) {
        $this.Optimizations = [System.Collections.Generic.List[PerformanceOptimization]]::new()
        $this.InitializeOptimizations()
    }
    
    [ToolMetadata] GetMetadata() {
        return [ToolMetadata]::new(
            "Performance Manager",
            "Optimize Windows performance and system responsiveness",
            "0.3.0"
        )
    }
    
    [void] ValidateEnvironment() {
        Test-WindowsPlatform
    }
    
    [bool] Execute() {
        $this.Log("Performance Manager executed")
        return $true
    }
    
    # Initialize performance optimizations
    [void] InitializeOptimizations() {
        # Disable animations
        $this.Optimizations.Add([PerformanceOptimization]::new(
            "DisableAnimations",
            "Disable window animations",
            "visual",
            {
                Set-ItemProperty -Path "HKCU:\Control Panel\Desktop\WindowMetrics" -Name "MinAnimate" -Value "0" -Type String
                Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "TaskbarAnimations" -Value 0 -Type DWord
            },
            {
                Set-ItemProperty -Path "HKCU:\Control Panel\Desktop\WindowMetrics" -Name "MinAnimate" -Value "1" -Type String
                Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" -Name "TaskbarAnimations" -Value 1 -Type DWord
            },
            5
        ))
        
        # Disable transparency
        $this.Optimizations.Add([PerformanceOptimization]::new(
            "DisableTransparency",
            "Disable window transparency effects",
            "visual",
            {
                Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize" -Name "EnableTransparency" -Value 0 -Type DWord
            },
            {
                Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize" -Name "EnableTransparency" -Value 1 -Type DWord
            },
            3
        ))
        
        # Disable visual effects
        $this.Optimizations.Add([PerformanceOptimization]::new(
            "DisableVisualEffects",
            "Disable visual effects for best performance",
            "visual",
            {
                Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects" -Name "VisualFXSetting" -Value 2 -Type DWord
                Set-ItemProperty -Path "HKCU:\Control Panel\Desktop" -Name "DragFullWindows" -Value "0" -Type String
                Set-ItemProperty -Path "HKCU:\Control Panel\Desktop" -Name "UserPreferencesMask" -Value ([byte[]](0x90,0x12,0x03,0x80,0x10,0x00,0x00,0x00)) -Type Binary
            },
            {
                Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects" -Name "VisualFXSetting" -Value 3 -Type DWord
                Set-ItemProperty -Path "HKCU:\Control Panel\Desktop" -Name "DragFullWindows" -Value "1" -Type String
            },
            10
        ))
        
        # Disable search indexing
        $this.Optimizations.Add([PerformanceOptimization]::new(
            "DisableSearchIndexing",
            "Disable Windows Search indexing (reduces disk I/O)",
            "disk",
            {
                Stop-Service -Name "WSearch" -Force -ErrorAction SilentlyContinue
                Set-Service -Name "WSearch" -StartupType Disabled -ErrorAction SilentlyContinue
            },
            {
                Set-Service -Name "WSearch" -StartupType Automatic -ErrorAction SilentlyContinue
                Start-Service -Name "WSearch" -ErrorAction SilentlyContinue
            },
            8
        ))
        
        # Disable SuperFetch/SysMain
        $this.Optimizations.Add([PerformanceOptimization]::new(
            "DisableSuperFetch",
            "Disable SuperFetch/SysMain (good for SSDs)",
            "disk",
            {
                Stop-Service -Name "SysMain" -Force -ErrorAction SilentlyContinue
                Set-Service -Name "SysMain" -StartupType Disabled -ErrorAction SilentlyContinue
            },
            {
                Set-Service -Name "SysMain" -StartupType Automatic -ErrorAction SilentlyContinue
                Start-Service -Name "SysMain" -ErrorAction SilentlyContinue
            },
            5
        ))
        
        # Disable hibernation
        $this.Optimizations.Add([PerformanceOptimization]::new(
            "DisableHibernation",
            "Disable hibernation (frees disk space)",
            "disk",
            {
                powercfg /hibernate off
            },
            {
                powercfg /hibernate on
            },
            0
        ))
        
        # Increase system responsiveness
        $this.Optimizations.Add([PerformanceOptimization]::new(
            "IncreaseSystemResponsiveness",
            "Prioritize foreground applications",
            "system",
            {
                Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\PriorityControl" -Name "Win32PrioritySeparation" -Value 38 -Type DWord
            },
            {
                Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\PriorityControl" -Name "Win32PrioritySeparation" -Value 2 -Type DWord
            },
            5
        ))
        
        # Disable Game Bar
        $this.Optimizations.Add([PerformanceOptimization]::new(
            "DisableGameBar",
            "Disable Xbox Game Bar",
            "gaming",
            {
                Set-ItemProperty -Path "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR" -Name "AppCaptureEnabled" -Value 0 -Type DWord
                Set-ItemProperty -Path "HKCU:\System\GameConfigStore" -Name "GameDVR_Enabled" -Value 0 -Type DWord
            },
            {
                Set-ItemProperty -Path "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR" -Name "AppCaptureEnabled" -Value 1 -Type DWord
                Set-ItemProperty -Path "HKCU:\System\GameConfigStore" -Name "GameDVR_Enabled" -Value 1 -Type DWord
            },
            3
        ))
        
        # Disable Windows Tips
        $this.Optimizations.Add([PerformanceOptimization]::new(
            "DisableWindowsTips",
            "Disable Windows tips and suggestions",
            "ui",
            {
                Set-ItemProperty -Path "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" -Name "SubscribedContent-338389Enabled" -Value 0 -Type DWord
            },
            {
                Set-ItemProperty -Path "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" -Name "SubscribedContent-338389Enabled" -Value 1 -Type DWord
            },
            2
        ))
    }
    
    # Apply performance preset
    [hashtable] ApplyPreset([PerformancePreset]$Preset) {
        $results = @{
            Success = [System.Collections.Generic.List[string]]::new()
            Failed = [System.Collections.Generic.List[string]]::new()
        }
        
        $optimizationsToApply = @()
        
        switch ($Preset) {
            Maximum {
                # Apply all optimizations
                $optimizationsToApply = $this.Optimizations
            }
            Balanced {
                # Apply only high-impact optimizations
                $optimizationsToApply = $this.Optimizations | Where-Object { $_.ExpectedImprovement -ge 5 }
            }
            Quality {
                # Don't apply visual optimizations
                $optimizationsToApply = $this.Optimizations | Where-Object { $_.Category -ne "visual" }
            }
        }
        
        foreach ($opt in $optimizationsToApply) {
            try {
                if ($this.ApplyOptimization($opt)) {
                    $results.Success.Add($opt.Name)
                }
                else {
                    $results.Failed.Add($opt.Name)
                }
            }
            catch {
                $results.Failed.Add($opt.Name)
            }
        }
        
        return $results
    }
    
    # Apply single optimization
    [bool] ApplyOptimization([PerformanceOptimization]$Optimization) {
        if ($this.DryRun) {
            $this.Log("DRY RUN: Would apply optimization '$($Optimization.Name)'")
            return $true
        }
        
        try {
            $this.Log("Applying optimization: $($Optimization.Name)")
            
            & $Optimization.Apply
            
            $this.Log("Applied: $($Optimization.Name)")
            return $true
        }
        catch {
            $this.LogError("Failed to apply '$($Optimization.Name)': $_")
            throw [SafetyError]::new("Failed to apply performance optimization: $_")
        }
    }
    
    # Revert optimization
    [bool] RevertOptimization([PerformanceOptimization]$Optimization) {
        if ($this.DryRun) {
            $this.Log("DRY RUN: Would revert optimization '$($Optimization.Name)'")
            return $true
        }
        
        try {
            $this.Log("Reverting optimization: $($Optimization.Name)")
            
            & $Optimization.Revert
            
            $this.Log("Reverted: $($Optimization.Name)")
            return $true
        }
        catch {
            $this.LogError("Failed to revert '$($Optimization.Name)': $_")
            return $false
        }
    }
    
    # Set power plan
    [bool] SetPowerPlan([PowerPlan]$Plan) {
        if ($this.DryRun) {
            $this.Log("DRY RUN: Would set power plan to $Plan")
            return $true
        }
        
        try {
            $this.Log("Setting power plan to: $Plan")
            
            $guid = switch ($Plan) {
                HighPerformance { "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c" }
                Balanced { "381b4222-f694-41f0-9685-ff5bb260df2e" }
                PowerSaver { "a1841308-3541-4fab-bc81-f71556f20b4a" }
                Ultimate { "e9a42b02-d5df-448d-aa00-03f14749eb61" }
            }
            
            # Check if plan exists
            $planExists = powercfg /list | Select-String $guid
            
            if ($planExists) {
                powercfg /setactive $guid
                $this.Log("Power plan set to: $Plan")
                return $true
            }
            else {
                $this.LogWarning("Power plan $Plan not available on this system")
                return $false
            }
        }
        catch {
            $this.LogError("Failed to set power plan: $_")
            throw [SafetyError]::new("Failed to set power plan: $_")
        }
    }
    
    # Get current power plan
    [string] GetCurrentPowerPlan() {
        try {
            $output = powercfg /getactivescheme
            
            if ($output -match '\((.*?)\)') {
                return $matches[1]
            }
            
            return "Unknown"
        }
        catch {
            return "Unknown"
        }
    }
    
    # Optimize for SSD
    [hashtable] OptimizeForSSD() {
        $results = @{
            Success = [System.Collections.Generic.List[string]]::new()
            Failed = [System.Collections.Generic.List[string]]::new()
        }
        
        try {
            # Disable SuperFetch/SysMain
            $opt = $this.Optimizations | Where-Object { $_.Name -eq "DisableSuperFetch" } | Select-Object -First 1
            if ($opt -and $this.ApplyOptimization($opt)) {
                $results.Success.Add("DisableSuperFetch")
            }
            
            # Disable hibernation to free space
            $opt = $this.Optimizations | Where-Object { $_.Name -eq "DisableHibernation" } | Select-Object -First 1
            if ($opt -and $this.ApplyOptimization($opt)) {
                $results.Success.Add("DisableHibernation")
            }
            
            # Disable search indexing
            $opt = $this.Optimizations | Where-Object { $_.Name -eq "DisableSearchIndexing" } | Select-Object -First 1
            if ($opt -and $this.ApplyOptimization($opt)) {
                $results.Success.Add("DisableSearchIndexing")
            }
        }
        catch {
            $this.LogError("SSD optimization failed: $_")
        }
        
        return $results
    }
    
    # List available optimizations
    [PerformanceOptimization[]] ListOptimizations([string]$Category = $null) {
        if ($Category) {
            return $this.Optimizations | Where-Object { $_.Category -eq $Category }
        }
        return $this.Optimizations.ToArray()
    }
}

# Convenience functions
function Get-PerformanceOptimizations {
    <#
    .SYNOPSIS
        List available performance optimizations
    
    .PARAMETER Category
        Filter by category (visual, disk, system, gaming, ui)
    
    .EXAMPLE
        Get-PerformanceOptimizations
        Get-PerformanceOptimizations -Category visual
    #>
    [CmdletBinding()]
    param(
        [string]$Category
    )
    
    $manager = [PerformanceManager]::new()
    return $manager.ListOptimizations($Category)
}

function Set-PerformancePreset {
    <#
    .SYNOPSIS
        Apply a performance preset
    
    .PARAMETER Preset
        Preset to apply (Maximum, Balanced, Quality)
    
    .EXAMPLE
        Set-PerformancePreset -Preset Maximum
    #>
    [CmdletBinding(SupportsShouldProcess=$true, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory=$true)]
        [PerformancePreset]$Preset
    )
    
    if ($PSCmdlet.ShouldProcess("Performance settings", "Apply $Preset preset")) {
        $manager = [PerformanceManager]::new()
        $results = $manager.ApplyPreset($Preset)
        
        Write-Host "`nResults:"
        Write-Host "Success: $($results.Success.Count)" -ForegroundColor Green
        Write-Host "Failed: $($results.Failed.Count)" -ForegroundColor Red
        
        return $results
    }
}

function Set-PowerConfiguration {
    <#
    .SYNOPSIS
        Set Windows power plan
    
    .PARAMETER Plan
        Power plan to activate
    
    .EXAMPLE
        Set-PowerConfiguration -Plan HighPerformance
    #>
    [CmdletBinding(SupportsShouldProcess=$true)]
    param(
        [Parameter(Mandatory=$true)]
        [PowerPlan]$Plan
    )
    
    if ($PSCmdlet.ShouldProcess("Power plan", "Set to $Plan")) {
        $manager = [PerformanceManager]::new()
        return $manager.SetPowerPlan($Plan)
    }
}

function Optimize-SSD {
    <#
    .SYNOPSIS
        Apply SSD-specific optimizations
    
    .DESCRIPTION
        Disables services that cause unnecessary SSD wear:
        - SuperFetch/SysMain
        - Hibernation
        - Search indexing
    
    .EXAMPLE
        Optimize-SSD
    #>
    [CmdletBinding(SupportsShouldProcess=$true, ConfirmImpact='High')]
    param()
    
    if ($PSCmdlet.ShouldProcess("SSD optimizations", "Apply")) {
        $manager = [PerformanceManager]::new()
        return $manager.OptimizeForSSD()
    }
}

function Get-CurrentPowerPlan {
    <#
    .SYNOPSIS
        Get the current active power plan
    
    .EXAMPLE
        Get-CurrentPowerPlan
    #>
    [CmdletBinding()]
    param()
    
    $manager = [PerformanceManager]::new()
    return $manager.GetCurrentPowerPlan()
}

Export-ModuleMember -Function Get-PerformanceOptimizations, Set-PerformancePreset, `
                              Set-PowerConfiguration, Optimize-SSD, Get-CurrentPowerPlan
