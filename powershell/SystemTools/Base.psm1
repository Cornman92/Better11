<#
.SYNOPSIS
    Base classes for system tools.

.DESCRIPTION
    Provides base classes and utilities that all system tools should inherit
    from for consistency, safety, and testability.
#>

using module .\Safety.psm1

# Tool metadata class
class ToolMetadata {
    [string]$Name
    [string]$Description
    [string]$Version
    [bool]$RequiresAdmin = $true
    [bool]$RequiresRestart = $false
    [string]$Category = "general"
    
    ToolMetadata(
        [string]$Name,
        [string]$Description,
        [string]$Version
    ) {
        $this.Name = $Name
        $this.Description = $Description
        $this.Version = $Version
    }
}

# Base class for all system tools
class SystemTool {
    [hashtable]$Config
    [bool]$DryRun
    [ToolMetadata]$Metadata
    hidden [System.Collections.Generic.List[string]]$LogMessages
    
    SystemTool([hashtable]$Config = @{}, [bool]$DryRun = $false) {
        $this.Config = $Config
        $this.DryRun = $DryRun
        $this.Metadata = $this.GetMetadata()
        $this.LogMessages = [System.Collections.Generic.List[string]]::new()
    }
    
    # Abstract method - must be overridden
    [ToolMetadata] GetMetadata() {
        throw "GetMetadata() must be implemented by derived class"
    }
    
    # Abstract method - must be overridden
    [void] ValidateEnvironment() {
        throw "ValidateEnvironment() must be implemented by derived class"
    }
    
    # Abstract method - must be overridden
    [bool] Execute() {
        throw "Execute() must be implemented by derived class"
    }
    
    # Pre-execution safety checks
    [bool] PreExecuteChecks([bool]$SkipConfirmation = $false) {
        try {
            # Ensure Windows platform
            Test-WindowsPlatform
            
            # Validate tool-specific environment
            $this.ValidateEnvironment()
            
            # Create restore point if configured
            if ($this.ShouldCreateRestorePoint()) {
                if (-not $this.DryRun) {
                    try {
                        New-SystemRestorePoint -Description "Before $($this.Metadata.Name)"
                        $this.Log("Restore point created")
                    }
                    catch {
                        $this.LogWarning("Failed to create restore point: $_")
                        # Don't fail - just warn
                    }
                }
            }
            
            # Check admin privileges if required
            if ($this.Metadata.RequiresAdmin -and -not $this.DryRun) {
                if (-not (Test-AdminPrivileges)) {
                    throw [SafetyError]::new(
                        "$($this.Metadata.Name) requires administrator privileges. " +
                        "Please run as administrator."
                    )
                }
            }
            
            # User confirmation
            if (-not $SkipConfirmation -and $this.ShouldConfirm()) {
                $warning = $this.GetConfirmationMessage()
                if (-not (Confirm-Action $warning)) {
                    $this.Log("User cancelled operation")
                    return $false
                }
            }
            
            $this.Log("Pre-execution checks passed")
            return $true
        }
        catch {
            $this.LogError("Pre-execution check failed: $_")
            throw
        }
    }
    
    # Post-execution cleanup (optional override)
    [void] PostExecute() {
        # Default: do nothing
        # Override in derived classes if needed
    }
    
    # Main run method
    [bool] Run([bool]$SkipConfirmation = $false) {
        $this.Log("Starting $($this.Metadata.Name) (dry_run=$($this.DryRun))")
        
        try {
            # Pre-execution checks
            if (-not $this.PreExecuteChecks($SkipConfirmation)) {
                return $false
            }
            
            # Execute
            if ($this.DryRun) {
                $this.Log("DRY RUN: Would execute $($this.Metadata.Name)")
                return $true
            }
            
            $result = $this.Execute()
            
            # Post-execution
            if ($result) {
                $this.PostExecute()
                $this.Log("$($this.Metadata.Name) completed successfully")
            }
            else {
                $this.LogWarning("$($this.Metadata.Name) completed with warnings")
            }
            
            return $result
        }
        catch [SafetyError] {
            $this.LogError("Safety check failed: $_")
            throw
        }
        catch {
            $this.LogError("Unexpected error during execution: $_")
            throw [SafetyError]::new("Execution failed: $_")
        }
    }
    
    # Helper methods
    [bool] ShouldCreateRestorePoint() {
        return $this.Config.ContainsKey('AlwaysCreateRestorePoint') -and 
               $this.Config.AlwaysCreateRestorePoint
    }
    
    [bool] ShouldConfirm() {
        return $this.Config.ContainsKey('ConfirmDestructiveActions') -and 
               $this.Config.ConfirmDestructiveActions
    }
    
    [string] GetConfirmationMessage() {
        $message = "Execute $($this.Metadata.Name)?"
        if ($this.Metadata.RequiresRestart) {
            $message += " (System restart may be required)"
        }
        return $message
    }
    
    # Logging methods
    [void] Log([string]$Message) {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        $logMessage = "[$timestamp] [INFO] $Message"
        $this.LogMessages.Add($logMessage)
        Write-Verbose $Message
    }
    
    [void] LogWarning([string]$Message) {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        $logMessage = "[$timestamp] [WARNING] $Message"
        $this.LogMessages.Add($logMessage)
        Write-Warning $Message
    }
    
    [void] LogError([string]$Message) {
        $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        $logMessage = "[$timestamp] [ERROR] $Message"
        $this.LogMessages.Add($logMessage)
        Write-Error $Message
    }
    
    [array] GetLogs() {
        return $this.LogMessages.ToArray()
    }
}

# Base class for registry tools
class RegistryTool : SystemTool {
    [string]$BackupPath
    
    RegistryTool([hashtable]$Config = @{}, [bool]$DryRun = $false) : base($Config, $DryRun) {
        $this.BackupPath = $null
    }
    
    [void] ValidateEnvironment() {
        Test-WindowsPlatform
        # Additional registry-specific checks could go here
    }
    
    [bool] PreExecuteChecks([bool]$SkipConfirmation = $false) {
        if (-not ([SystemTool]$this).PreExecuteChecks($SkipConfirmation)) {
            return $false
        }
        
        # Backup registry keys before modification
        if ($this.Config.ContainsKey('BackupRegistry') -and 
            $this.Config.BackupRegistry -and 
            -not $this.DryRun) {
            $this.Log("Registry backup recommended - handled by individual tools")
        }
        
        return $true
    }
}

# Export classes and functions
Export-ModuleMember -Function * -Cmdlet *
