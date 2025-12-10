<#
.SYNOPSIS
    Configuration management for Better11 PowerShell module.

.DESCRIPTION
    This module handles loading, saving, and validating Better11 configuration
    from JSON, TOML, or PSD1 files. Configuration can be loaded from:
    1. System-wide location (C:\ProgramData\Better11\config.json)
    2. User directory ($env:USERPROFILE\.better11\config.json)
    3. Environment variables (for overrides)
    4. Programmatic defaults
#>

# Configuration data structures
class Better11Config {
    [string]$Version = "0.3.0"
    [bool]$AutoUpdate = $true
    [bool]$CheckUpdatesOnStart = $true
    [bool]$TelemetryEnabled = $false
}

class ApplicationsConfig {
    [string]$CatalogUrl = "default"
    [bool]$AutoInstallDependencies = $true
    [bool]$VerifySignatures = $true
    [bool]$RequireCodeSigning = $false
    [bool]$CheckRevocation = $false
}

class SystemToolsConfig {
    [bool]$AlwaysCreateRestorePoint = $true
    [bool]$ConfirmDestructiveActions = $true
    [bool]$BackupRegistry = $true
    [ValidateSet('low', 'medium', 'high', 'paranoid')]
    [string]$SafetyLevel = "high"
}

class GUIConfig {
    [ValidateSet('system', 'light', 'dark')]
    [string]$Theme = "system"
    [bool]$ShowAdvancedOptions = $false
    [bool]$RememberWindowSize = $true
    [string]$DefaultTab = "applications"
}

class LoggingConfig {
    [ValidateSet('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')]
    [string]$Level = "INFO"
    [bool]$FileEnabled = $true
    [bool]$ConsoleEnabled = $true
    [int]$MaxLogSizeMB = 10
    [int]$BackupCount = 5
}

class Config {
    [Better11Config]$Better11 = [Better11Config]::new()
    [ApplicationsConfig]$Applications = [ApplicationsConfig]::new()
    [SystemToolsConfig]$SystemTools = [SystemToolsConfig]::new()
    [GUIConfig]$GUI = [GUIConfig]::new()
    [LoggingConfig]$Logging = [LoggingConfig]::new()
    
    # Static method to get default config path
    static [string] GetDefaultPath() {
        return Join-Path $env:USERPROFILE ".better11\config.json"
    }
    
    # Static method to get system config path
    static [string] GetSystemPath() {
        $programData = if ($env:PROGRAMDATA) { $env:PROGRAMDATA } else { "C:\ProgramData" }
        return Join-Path $programData "Better11\config.json"
    }
    
    # Load configuration from file
    static [Config] Load([string]$Path = $null) {
        if (-not $Path) {
            $Path = [Config]::GetDefaultPath()
        }
        
        $config = [Config]::new()
        
        # Load from file if exists
        if (Test-Path $Path) {
            $config = [Config]::LoadFromFile($Path)
        }
        
        # Apply environment variable overrides
        $config = [Config]::ApplyEnvOverrides($config)
        
        return $config
    }
    
    # Load from specific file
    static [Config] LoadFromFile([string]$Path) {
        $extension = [System.IO.Path]::GetExtension($Path).ToLower()
        
        try {
            $data = $null
            
            switch ($extension) {
                '.json' {
                    $data = Get-Content $Path -Raw | ConvertFrom-Json
                }
                '.psd1' {
                    $data = Import-PowerShellDataFile $Path
                }
                '.toml' {
                    # Basic TOML parsing (could use module for full support)
                    Write-Warning "TOML parsing limited. Consider using JSON or PSD1."
                    $content = Get-Content $Path -Raw
                    # Simple TOML to hashtable conversion
                    $data = [PSCustomObject]@{}
                }
                default {
                    throw "Unsupported configuration format: $extension"
                }
            }
            
            return [Config]::FromObject($data)
        }
        catch {
            throw "Failed to load configuration from ${Path}: $_"
        }
    }
    
    # Create Config from object
    static [Config] FromObject([PSObject]$Data) {
        $config = [Config]::new()
        
        if ($Data.Better11) {
            $config.Better11 = [Better11Config]$Data.Better11
        }
        if ($Data.Applications) {
            $config.Applications = [ApplicationsConfig]$Data.Applications
        }
        if ($Data.SystemTools) {
            $config.SystemTools = [SystemToolsConfig]$Data.SystemTools
        }
        if ($Data.GUI) {
            $config.GUI = [GUIConfig]$Data.GUI
        }
        if ($Data.Logging) {
            $config.Logging = [LoggingConfig]$Data.Logging
        }
        
        return $config
    }
    
    # Apply environment variable overrides
    static [Config] ApplyEnvOverrides([Config]$Config) {
        if ($env:BETTER11_AUTO_UPDATE) {
            $Config.Better11.AutoUpdate = $env:BETTER11_AUTO_UPDATE -eq 'true'
        }
        if ($env:BETTER11_LOG_LEVEL) {
            $Config.Logging.Level = $env:BETTER11_LOG_LEVEL
        }
        if ($env:BETTER11_SAFETY_LEVEL) {
            $Config.SystemTools.SafetyLevel = $env:BETTER11_SAFETY_LEVEL
        }
        
        return $Config
    }
    
    # Save configuration to file
    [void] Save([string]$Path = $null) {
        if (-not $Path) {
            $Path = [Config]::GetDefaultPath()
        }
        
        # Ensure directory exists
        $directory = Split-Path $Path -Parent
        if (-not (Test-Path $directory)) {
            New-Item -ItemType Directory -Path $directory -Force | Out-Null
        }
        
        # Convert to hashtable
        $data = $this.ToHashtable()
        
        # Save based on extension
        $extension = [System.IO.Path]::GetExtension($Path).ToLower()
        
        switch ($extension) {
            { $_ -in '.json', '' } {
                $data | ConvertTo-Json -Depth 10 | Set-Content $Path -Encoding UTF8
            }
            '.psd1' {
                # PowerShell Data File format
                $this.SaveAsPSD1($Path, $data)
            }
            default {
                throw "Unsupported configuration format: $extension"
            }
        }
    }
    
    # Convert to hashtable
    [hashtable] ToHashtable() {
        return @{
            Better11 = @{
                Version = $this.Better11.Version
                AutoUpdate = $this.Better11.AutoUpdate
                CheckUpdatesOnStart = $this.Better11.CheckUpdatesOnStart
                TelemetryEnabled = $this.Better11.TelemetryEnabled
            }
            Applications = @{
                CatalogUrl = $this.Applications.CatalogUrl
                AutoInstallDependencies = $this.Applications.AutoInstallDependencies
                VerifySignatures = $this.Applications.VerifySignatures
                RequireCodeSigning = $this.Applications.RequireCodeSigning
                CheckRevocation = $this.Applications.CheckRevocation
            }
            SystemTools = @{
                AlwaysCreateRestorePoint = $this.SystemTools.AlwaysCreateRestorePoint
                ConfirmDestructiveActions = $this.SystemTools.ConfirmDestructiveActions
                BackupRegistry = $this.SystemTools.BackupRegistry
                SafetyLevel = $this.SystemTools.SafetyLevel
            }
            GUI = @{
                Theme = $this.GUI.Theme
                ShowAdvancedOptions = $this.GUI.ShowAdvancedOptions
                RememberWindowSize = $this.GUI.RememberWindowSize
                DefaultTab = $this.GUI.DefaultTab
            }
            Logging = @{
                Level = $this.Logging.Level
                FileEnabled = $this.Logging.FileEnabled
                ConsoleEnabled = $this.Logging.ConsoleEnabled
                MaxLogSizeMB = $this.Logging.MaxLogSizeMB
                BackupCount = $this.Logging.BackupCount
            }
        }
    }
    
    # Save as PSD1 format
    [void] SaveAsPSD1([string]$Path, [hashtable]$Data) {
        $content = "@{`n"
        foreach ($section in $Data.Keys) {
            $content += "    $section = @{`n"
            foreach ($key in $Data[$section].Keys) {
                $value = $Data[$section][$key]
                if ($value -is [string]) {
                    $content += "        $key = '$value'`n"
                }
                else {
                    $content += "        $key = `$$value`n"
                }
            }
            $content += "    }`n"
        }
        $content += "}`n"
        
        Set-Content $Path $content -Encoding UTF8
    }
    
    # Validate configuration
    [bool] Validate() {
        # Validate safety level
        $validSafetyLevels = @('low', 'medium', 'high', 'paranoid')
        if ($this.SystemTools.SafetyLevel -notin $validSafetyLevels) {
            throw "Invalid safety_level: $($this.SystemTools.SafetyLevel). Must be one of: $($validSafetyLevels -join ', ')"
        }
        
        # Validate theme
        $validThemes = @('system', 'light', 'dark')
        if ($this.GUI.Theme -notin $validThemes) {
            throw "Invalid theme: $($this.GUI.Theme). Must be one of: $($validThemes -join ', ')"
        }
        
        # Validate log level
        $validLogLevels = @('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        if ($this.Logging.Level.ToUpper() -notin $validLogLevels) {
            throw "Invalid log level: $($this.Logging.Level). Must be one of: $($validLogLevels -join ', ')"
        }
        
        return $true
    }
}

# Convenience function
function Load-Better11Config {
    <#
    .SYNOPSIS
        Load Better11 configuration
    
    .PARAMETER Path
        Path to configuration file (optional)
    
    .EXAMPLE
        $config = Load-Better11Config
        
    .EXAMPLE
        $config = Load-Better11Config -Path "C:\custom\config.json"
    #>
    [CmdletBinding()]
    param(
        [string]$Path = $null
    )
    
    return [Config]::Load($Path)
}

# Export functions
Export-ModuleMember -Function Load-Better11Config
Export-ModuleMember -Cmdlet *
