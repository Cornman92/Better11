<#
.SYNOPSIS
    Common interfaces and base classes for Better11 components.

.DESCRIPTION
    This module defines the core interfaces (as PowerShell classes) that
    components implement for consistency and extensibility.
#>

# Version class with comparison operators
class Version {
    [int]$Major
    [int]$Minor
    [int]$Patch
    
    Version([int]$Major, [int]$Minor, [int]$Patch) {
        $this.Major = $Major
        $this.Minor = $Minor
        $this.Patch = $Patch
    }
    
    [string] ToString() {
        return "$($this.Major).$($this.Minor).$($this.Patch)"
    }
    
    [bool] Equals([object]$Other) {
        if ($Other -isnot [Version]) {
            return $false
        }
        return ($this.Major -eq $Other.Major) -and 
               ($this.Minor -eq $Other.Minor) -and 
               ($this.Patch -eq $Other.Patch)
    }
    
    [bool] IsLessThan([Version]$Other) {
        if ($this.Major -ne $Other.Major) {
            return $this.Major -lt $Other.Major
        }
        if ($this.Minor -ne $Other.Minor) {
            return $this.Minor -lt $Other.Minor
        }
        return $this.Patch -lt $Other.Patch
    }
    
    [bool] IsGreaterThan([Version]$Other) {
        return -not ($this.Equals($Other) -or $this.IsLessThan($Other))
    }
    
    static [Version] Parse([string]$VersionString) {
        <#
        .SYNOPSIS
            Parse version string like '1.2.3'
        #>
        try {
            $parts = $VersionString.Trim().Split('.')
            if ($parts.Count -ne 3) {
                throw "Version must have 3 parts (major.minor.patch), got: $VersionString"
            }
            
            $major = [int]$parts[0]
            $minor = [int]$parts[1]
            $patch = [int]$parts[2]
            
            return [Version]::new($major, $minor, $patch)
        }
        catch {
            throw "Invalid version string: $VersionString - $_"
        }
    }
}

# Base interface for updatable components
class IUpdatable {
    # Get the currently installed version
    [Version] GetCurrentVersion() {
        throw "GetCurrentVersion() must be implemented"
    }
    
    # Check if updates are available
    [Version] CheckForUpdates() {
        throw "CheckForUpdates() must be implemented"
    }
    
    # Download the update package
    [string] DownloadUpdate([Version]$Version) {
        throw "DownloadUpdate() must be implemented"
    }
    
    # Install the downloaded update
    [bool] InstallUpdate([string]$PackagePath) {
        throw "InstallUpdate() must be implemented"
    }
    
    # Rollback to previous version
    [bool] RollbackUpdate() {
        throw "RollbackUpdate() must be implemented"
    }
}

# Base interface for configurable components
class IConfigurable {
    # Load configuration from hashtable
    [void] LoadConfig([hashtable]$Config) {
        throw "LoadConfig() must be implemented"
    }
    
    # Get configuration schema
    [hashtable] GetConfigSchema() {
        throw "GetConfigSchema() must be implemented"
    }
    
    # Validate configuration
    [bool] ValidateConfig([hashtable]$Config) {
        throw "ValidateConfig() must be implemented"
    }
}

# Base interface for monitorable components
class IMonitorable {
    # Get current status and metrics
    [hashtable] GetStatus() {
        throw "GetStatus() must be implemented"
    }
    
    # Get health status
    [string] GetHealth() {
        throw "GetHealth() must be implemented"
    }
}

# Base interface for backupable components
class IBackupable {
    # Create a backup of current state
    [string] CreateBackup([string]$Destination) {
        throw "CreateBackup() must be implemented"
    }
    
    # Restore state from backup
    [bool] RestoreBackup([string]$BackupPath) {
        throw "RestoreBackup() must be implemented"
    }
    
    # Verify backup integrity
    [bool] VerifyBackup([string]$BackupPath) {
        throw "VerifyBackup() must be implemented"
    }
}

# Export classes
Export-ModuleMember -Function * -Variable * -Alias *
