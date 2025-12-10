<#
.SYNOPSIS
    Better11 PowerShell Module - Windows Enhancement Toolkit

.DESCRIPTION
    Main module file for Better11 PowerShell backend.
    This module provides comprehensive Windows system management and optimization functionality.

.NOTES
    Name: Better11
    Author: Better11 Development Team
    Version: 0.3.0
    License: MIT
#>

# Module variables
$script:ModuleRoot = $PSScriptRoot
$script:LogPath = Join-Path $env:USERPROFILE ".better11\logs"
$script:ConfigPath = Join-Path $env:USERPROFILE ".better11\config.json"

# Create directories if they don't exist
if (-not (Test-Path $script:LogPath)) {
    New-Item -Path $script:LogPath -ItemType Directory -Force | Out-Null
}

# Module initialization
Write-Verbose "Better11 module loading from: $script:ModuleRoot"

# Export module-level variables
Export-ModuleMember -Variable ModuleRoot, LogPath, ConfigPath

# Module cleanup
$MyInvocation.MyCommand.ScriptBlock.Module.OnRemove = {
    Write-Verbose "Better11 module unloading"
}

Write-Verbose "Better11 module loaded successfully (v0.3.0)"
