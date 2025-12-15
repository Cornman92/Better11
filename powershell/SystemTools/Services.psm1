<#
.SYNOPSIS
    Windows services management and optimization.

.DESCRIPTION
    Provides functionality to manage Windows services, including
    disabling unnecessary services and optimizing service startup types.
#>

using module .\Base.psm1
using module .\Safety.psm1

# Service action enumeration
enum ServiceAction {
    Disable
    Manual
    Automatic
    AutomaticDelayed
}

# Service recommendation class
class ServiceRecommendation {
    [string]$Name
    [string]$DisplayName
    [string]$CurrentStartType
    [ServiceAction]$RecommendedAction
    [string]$Reason
    [string]$Category
    
    ServiceRecommendation(
        [string]$Name,
        [string]$DisplayName,
        [string]$CurrentStartType,
        [ServiceAction]$RecommendedAction,
        [string]$Reason
    ) {
        $this.Name = $Name
        $this.DisplayName = $DisplayName
        $this.CurrentStartType = $CurrentStartType
        $this.RecommendedAction = $RecommendedAction
        $this.Reason = $Reason
        $this.Category = "performance"
    }
}

# Services Manager class
class ServicesManager : SystemTool {
    [System.Collections.Generic.List[ServiceRecommendation]]$Recommendations
    
    ServicesManager([hashtable]$Config = @{}, [bool]$DryRun = $false) : base($Config, $DryRun) {
        $this.Recommendations = [System.Collections.Generic.List[ServiceRecommendation]]::new()
        $this.InitializeRecommendations()
    }
    
    [ToolMetadata] GetMetadata() {
        return [ToolMetadata]::new(
            "Services Manager",
            "Manage Windows services and optimize startup",
            "0.3.0"
        )
    }
    
    [void] ValidateEnvironment() {
        Test-WindowsPlatform
        Assert-AdminPrivileges "Services management requires administrator privileges"
    }
    
    [bool] Execute() {
        $this.Log("Services Manager executed")
        return $true
    }
    
    # Initialize service recommendations
    [void] InitializeRecommendations() {
        # Telemetry services
        $this.Recommendations.Add([ServiceRecommendation]::new(
            "DiagTrack",
            "Connected User Experiences and Telemetry",
            "Automatic",
            [ServiceAction]::Disable,
            "Telemetry service - privacy concern"
        ))
        
        $this.Recommendations.Add([ServiceRecommendation]::new(
            "dmwappushservice",
            "Device Management Wireless Application Protocol",
            "Manual",
            [ServiceAction]::Disable,
            "Telemetry push service - privacy concern"
        ))
        
        # Unnecessary services
        $this.Recommendations.Add([ServiceRecommendation]::new(
            "HomeGroupListener",
            "HomeGroup Listener",
            "Manual",
            [ServiceAction]::Disable,
            "HomeGroup is deprecated in Windows 10/11"
        ))
        
        $this.Recommendations.Add([ServiceRecommendation]::new(
            "HomeGroupProvider",
            "HomeGroup Provider",
            "Manual",
            [ServiceAction]::Disable,
            "HomeGroup is deprecated in Windows 10/11"
        ))
        
        # Print Spooler (if no printer)
        $this.Recommendations.Add([ServiceRecommendation]::new(
            "Spooler",
            "Print Spooler",
            "Automatic",
            [ServiceAction]::Manual,
            "Set to manual if no printer installed"
        ))
        
        # Fax (rarely used)
        $this.Recommendations.Add([ServiceRecommendation]::new(
            "Fax",
            "Fax",
            "Manual",
            [ServiceAction]::Disable,
            "Fax service rarely used"
        ))
        
        # Windows Search (optional)
        $this.Recommendations.Add([ServiceRecommendation]::new(
            "WSearch",
            "Windows Search",
            "Automatic",
            [ServiceAction]::Manual,
            "Optional: Reduces disk I/O, disables instant search"
        ))
        
        # Xbox services (if not gaming)
        $this.Recommendations.Add([ServiceRecommendation]::new(
            "XblAuthManager",
            "Xbox Live Auth Manager",
            "Manual",
            [ServiceAction]::Disable,
            "Xbox service - disable if not gaming"
        ))
        
        $this.Recommendations.Add([ServiceRecommendation]::new(
            "XblGameSave",
            "Xbox Live Game Save",
            "Manual",
            [ServiceAction]::Disable,
            "Xbox service - disable if not gaming"
        ))
        
        $this.Recommendations.Add([ServiceRecommendation]::new(
            "XboxNetApiSvc",
            "Xbox Live Networking Service",
            "Manual",
            [ServiceAction]::Disable,
            "Xbox service - disable if not gaming"
        ))
    }
    
    # List all services
    [object[]] ListServices([string]$Filter = $null) {
        $services = Get-Service
        
        if ($Filter) {
            $services = $services | Where-Object { 
                $_.Name -like "*$Filter*" -or 
                $_.DisplayName -like "*$Filter*" 
            }
        }
        
        return $services
    }
    
    # Get service recommendations
    [ServiceRecommendation[]] GetRecommendations() {
        $activeRecommendations = [System.Collections.Generic.List[ServiceRecommendation]]::new()
        
        foreach ($rec in $this.Recommendations) {
            try {
                $service = Get-Service -Name $rec.Name -ErrorAction SilentlyContinue
                
                if ($service) {
                    # Only recommend if service exists and current state differs
                    if ($service.StartType -ne $rec.RecommendedAction) {
                        $rec.CurrentStartType = $service.StartType
                        $activeRecommendations.Add($rec)
                    }
                }
            }
            catch {
                # Service doesn't exist, skip
            }
        }
        
        return $activeRecommendations.ToArray()
    }
    
    # Apply service configuration
    [bool] ConfigureService(
        [string]$ServiceName,
        [ServiceAction]$Action
    ) {
        if ($this.DryRun) {
            $this.Log("DRY RUN: Would configure service '$ServiceName' to $Action")
            return $true
        }
        
        try {
            $service = Get-Service -Name $ServiceName -ErrorAction Stop
            
            $this.Log("Configuring service: $ServiceName -> $Action")
            
            # Stop service first if running and action is Disable
            if ($Action -eq [ServiceAction]::Disable -and $service.Status -eq 'Running') {
                Stop-Service -Name $ServiceName -Force -ErrorAction Stop
                $this.Log("Stopped service: $ServiceName")
            }
            
            # Set startup type
            switch ($Action) {
                Disable {
                    Set-Service -Name $ServiceName -StartupType Disabled -ErrorAction Stop
                }
                Manual {
                    Set-Service -Name $ServiceName -StartupType Manual -ErrorAction Stop
                }
                Automatic {
                    Set-Service -Name $ServiceName -StartupType Automatic -ErrorAction Stop
                }
                AutomaticDelayed {
                    # Use sc.exe for delayed auto start
                    $process = Start-Process -FilePath "sc.exe" `
                                            -ArgumentList "config `"$ServiceName`" start=delayed-auto" `
                                            -Wait `
                                            -NoNewWindow `
                                            -PassThru
                    
                    if ($process.ExitCode -ne 0) {
                        throw "sc.exe returned exit code $($process.ExitCode)"
                    }
                }
            }
            
            $this.Log("Configured service $ServiceName to $Action")
            return $true
        }
        catch {
            $this.LogError("Failed to configure service ${ServiceName}: $_")
            throw [SafetyError]::new("Failed to configure service: $_")
        }
    }
    
    # Apply multiple recommendations
    [hashtable] ApplyRecommendations([string[]]$ServiceNames = $null) {
        $results = @{
            Success = [System.Collections.Generic.List[string]]::new()
            Failed = [System.Collections.Generic.List[string]]::new()
            Skipped = [System.Collections.Generic.List[string]]::new()
        }
        
        $recommendations = $this.GetRecommendations()
        
        foreach ($rec in $recommendations) {
            # If service names specified, only apply those
            if ($ServiceNames -and $rec.Name -notin $ServiceNames) {
                $results.Skipped.Add($rec.Name)
                continue
            }
            
            try {
                if ($this.ConfigureService($rec.Name, $rec.RecommendedAction)) {
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
    
    # Get services by startup type
    [object[]] GetServicesByStartupType([string]$StartupType) {
        return Get-Service | Where-Object { $_.StartType -eq $StartupType }
    }
    
    # Analyze service dependencies
    [hashtable] GetServiceDependencies([string]$ServiceName) {
        $service = Get-Service -Name $ServiceName -ErrorAction Stop
        
        return @{
            Name = $service.Name
            DisplayName = $service.DisplayName
            DependsOn = $service.ServicesDependedOn
            DependentServices = $service.DependentServices
        }
    }
}

# Convenience functions
function Get-ServiceRecommendations {
    <#
    .SYNOPSIS
        Get service optimization recommendations
    
    .EXAMPLE
        Get-ServiceRecommendations | Format-Table
    #>
    [CmdletBinding()]
    param()
    
    $manager = [ServicesManager]::new()
    return $manager.GetRecommendations()
}

function Set-ServiceConfiguration {
    <#
    .SYNOPSIS
        Configure a Windows service
    
    .PARAMETER ServiceName
        Name of the service
    
    .PARAMETER Action
        Action to perform (Disable, Manual, Automatic, AutomaticDelayed)
    
    .EXAMPLE
        Set-ServiceConfiguration -ServiceName "DiagTrack" -Action Disable
    #>
    [CmdletBinding(SupportsShouldProcess=$true)]
    param(
        [Parameter(Mandatory=$true)]
        [string]$ServiceName,
        
        [Parameter(Mandatory=$true)]
        [ServiceAction]$Action
    )
    
    if ($PSCmdlet.ShouldProcess($ServiceName, "Configure service to $Action")) {
        $manager = [ServicesManager]::new()
        return $manager.ConfigureService($ServiceName, $Action)
    }
}

function Optimize-Services {
    <#
    .SYNOPSIS
        Apply all service optimization recommendations
    
    .PARAMETER ServiceNames
        Specific services to optimize (optional)
    
    .EXAMPLE
        Optimize-Services
        Optimize-Services -ServiceNames @("DiagTrack", "dmwappushservice")
    #>
    [CmdletBinding(SupportsShouldProcess=$true, ConfirmImpact='High')]
    param(
        [string[]]$ServiceNames
    )
    
    if ($PSCmdlet.ShouldProcess("Windows Services", "Apply optimization recommendations")) {
        $manager = [ServicesManager]::new()
        return $manager.ApplyRecommendations($ServiceNames)
    }
}

Export-ModuleMember -Function Get-ServiceRecommendations, Set-ServiceConfiguration, Optimize-Services
