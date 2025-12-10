<#
.SYNOPSIS
    Installs the Better11 PowerShell module.

.DESCRIPTION
    Installs the Better11 module to the user's PowerShell modules directory,
    making it available for import in all PowerShell sessions.

.PARAMETER Scope
    Installation scope: CurrentUser or AllUsers. Default is CurrentUser.

.PARAMETER Force
    Overwrite existing installation if present.

.EXAMPLE
    .\Install-Better11Module.ps1
    Installs Better11 for current user.

.EXAMPLE
    .\Install-Better11Module.ps1 -Scope AllUsers
    Installs Better11 for all users (requires administrator).
#>

[CmdletBinding()]
param(
    [Parameter()]
    [ValidateSet('CurrentUser', 'AllUsers')]
    [string]$Scope = 'CurrentUser',
    
    [Parameter()]
    [switch]$Force
)

$ErrorActionPreference = 'Stop'

Write-Host "Better11 Module Installer" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan
Write-Host ""

# Check administrator privileges for AllUsers scope
if ($Scope -eq 'AllUsers') {
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    
    if (-not $isAdmin) {
        Write-Error "Installing for AllUsers requires administrator privileges. Please run PowerShell as Administrator or use -Scope CurrentUser"
        exit 1
    }
}

# Get module paths
$modulePath = if ($Scope -eq 'AllUsers') {
    "$env:ProgramFiles\WindowsPowerShell\Modules"
} else {
    "$HOME\Documents\WindowsPowerShell\Modules"
}

$destinationPath = Join-Path $modulePath 'Better11'

# Check if module already exists
if (Test-Path $destinationPath) {
    if ($Force) {
        Write-Host "Removing existing installation..." -ForegroundColor Yellow
        Remove-Item -Path $destinationPath -Recurse -Force
    } else {
        Write-Error "Better11 module already exists at $destinationPath. Use -Force to overwrite."
        exit 1
    }
}

# Copy module files
Write-Host "Installing Better11 module to: $destinationPath" -ForegroundColor Green

$sourcePath = Join-Path $PSScriptRoot 'Better11'

try {
    # Create destination directory
    New-Item -Path $destinationPath -ItemType Directory -Force | Out-Null
    
    # Copy all files
    Copy-Item -Path "$sourcePath\*" -Destination $destinationPath -Recurse -Force
    
    Write-Host "✓ Module files copied successfully" -ForegroundColor Green
    
    # Verify installation
    Import-Module $destinationPath -Force
    $module = Get-Module Better11
    
    if ($module) {
        Write-Host "✓ Module imported successfully" -ForegroundColor Green
        Write-Host ""
        Write-Host "Module Version: $($module.Version)" -ForegroundColor Cyan
        Write-Host "Module Path: $destinationPath" -ForegroundColor Cyan
        Write-Host "Exported Functions: $($module.ExportedFunctions.Count)" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Installation complete! You can now use:" -ForegroundColor Green
        Write-Host "  Import-Module Better11" -ForegroundColor White
        Write-Host "  Get-Command -Module Better11" -ForegroundColor White
        Write-Host ""
    } else {
        Write-Error "Module installation completed but module could not be imported. Please check for errors."
    }
}
catch {
    Write-Error "Failed to install module: $_"
    
    # Cleanup on failure
    if (Test-Path $destinationPath) {
        Remove-Item -Path $destinationPath -Recurse -Force -ErrorAction SilentlyContinue
    }
    
    exit 1
}
