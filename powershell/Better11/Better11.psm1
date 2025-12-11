#Requires -Version 5.1

<#
.SYNOPSIS
    Better11 PowerShell Module - Main module file
    
.DESCRIPTION
    Better11 provides comprehensive Windows 11 system management, application
    installation, security features, and privacy controls through PowerShell.
    
.NOTES
    Name: Better11
    Author: Better11 Development Team
    Version: 0.3.0
    License: MIT
#>

# Module variables
$script:ModuleRoot = $PSScriptRoot
$script:DataPath = Join-Path $ModuleRoot 'Data'
$script:LogPath = Join-Path $env:USERPROFILE '.better11\logs'
$script:ConfigPath = Join-Path $env:USERPROFILE '.better11\config.json'

# Ensure log directory exists
if (-not (Test-Path $script:LogPath)) {
    New-Item -Path $script:LogPath -ItemType Directory -Force | Out-Null
}

# Module initialization
Write-Verbose "Better11 module loaded from: $ModuleRoot"
Write-Verbose "Data path: $script:DataPath"
Write-Verbose "Log path: $script:LogPath"

# Export module variables
$ExecutionContext.SessionState.Module.PrivateData = @{
    ModuleRoot = $script:ModuleRoot
    DataPath = $script:DataPath
    LogPath = $script:LogPath
    ConfigPath = $script:ConfigPath
}

# Module cleanup
$MyInvocation.MyCommand.ScriptBlock.Module.OnRemove = {
    Write-Verbose "Better11 module unloaded"
}
