<#
.SYNOPSIS
    Installation script for Better11 PowerShell module and WinUI application.

.DESCRIPTION
    This script installs the Better11 PowerShell module to the user's PowerShell modules
    directory and optionally installs the WinUI application.

.PARAMETER InstallModule
    Install the PowerShell module (default: true).

.PARAMETER InstallGUI
    Install the WinUI GUI application (default: false).

.PARAMETER Force
    Force installation, overwriting existing files.

.EXAMPLE
    .\Install-Better11.ps1 -InstallModule -InstallGUI
#>
[CmdletBinding()]
param(
    [Parameter()]
    [switch]$InstallModule = $true,
    
    [Parameter()]
    [switch]$InstallGUI = $false,
    
    [Parameter()]
    [switch]$Force
)

$ErrorActionPreference = 'Stop'

Write-Host "Better11 Installation Script" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan
Write-Host ""

# Check if running as administrator
$IsAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $IsAdmin -and $InstallGUI) {
    Write-Warning "Administrator privileges required for GUI installation."
    Write-Host "Please run this script as Administrator to install the GUI." -ForegroundColor Yellow
    $InstallGUI = $false
}

# Install PowerShell Module
if ($InstallModule) {
    Write-Host "[1/3] Installing PowerShell Module..." -ForegroundColor Green
    
    $ModuleSource = Join-Path $PSScriptRoot "..\powershell\Better11"
    $ModuleDest = "$env:USERPROFILE\Documents\PowerShell\Modules\Better11"
    
    if (Test-Path $ModuleDest) {
        if ($Force) {
            Write-Host "  Removing existing module..." -ForegroundColor Yellow
            Remove-Item $ModuleDest -Recurse -Force
        }
        else {
            Write-Warning "  Module already exists. Use -Force to overwrite."
            Write-Host "  Skipping module installation." -ForegroundColor Yellow
            $InstallModule = $false
        }
    }
    
    if ($InstallModule) {
        # Create destination directory
        if (-not (Test-Path (Split-Path $ModuleDest))) {
            New-Item -Path (Split-Path $ModuleDest) -ItemType Directory -Force | Out-Null
        }
        
        # Copy module files
        Copy-Item -Path $ModuleSource -Destination $ModuleDest -Recurse -Force
        
        Write-Host "  ✓ PowerShell module installed to: $ModuleDest" -ForegroundColor Green
        
        # Test import
        try {
            Import-Module Better11 -Force
            $FunctionCount = (Get-Command -Module Better11).Count
            Write-Host "  ✓ Module loaded successfully ($FunctionCount functions available)" -ForegroundColor Green
        }
        catch {
            Write-Warning "  Failed to import module: $_"
        }
    }
}

# Install GUI Application
if ($InstallGUI) {
    Write-Host ""
    Write-Host "[2/3] Installing WinUI Application..." -ForegroundColor Green
    
    $MSIXPath = Join-Path $PSScriptRoot "..\csharp\Better11.WinUI\bin\Release\Better11.msix"
    
    if (Test-Path $MSIXPath) {
        Write-Host "  Installing MSIX package..." -ForegroundColor Yellow
        Add-AppxPackage -Path $MSIXPath -ForceApplicationShutdown
        Write-Host "  ✓ WinUI application installed" -ForegroundColor Green
    }
    else {
        Write-Warning "  MSIX package not found at: $MSIXPath"
        Write-Host "  Please build the WinUI project first:" -ForegroundColor Yellow
        Write-Host "    cd csharp" -ForegroundColor Yellow
        Write-Host "    dotnet build -c Release" -ForegroundColor Yellow
    }
}

# Verify Installation
Write-Host ""
Write-Host "[3/3] Verifying Installation..." -ForegroundColor Green

if ($InstallModule) {
    $Module = Get-Module -ListAvailable Better11
    if ($Module) {
        Write-Host "  ✓ PowerShell module: Installed (v$($Module.Version))" -ForegroundColor Green
    }
    else {
        Write-Warning "  PowerShell module: Not found"
    }
}

if ($InstallGUI) {
    $App = Get-AppxPackage | Where-Object { $_.Name -like "*Better11*" }
    if ($App) {
        Write-Host "  ✓ WinUI application: Installed (v$($App.Version))" -ForegroundColor Green
    }
    else {
        Write-Warning "  WinUI application: Not found"
    }
}

Write-Host ""
Write-Host "Installation Complete!" -ForegroundColor Cyan
Write-Host ""
Write-Host "Quick Start:" -ForegroundColor Cyan
Write-Host "  PowerShell: Import-Module Better11" -ForegroundColor White
Write-Host "              Get-Better11Apps" -ForegroundColor White
if ($InstallGUI) {
    Write-Host "  GUI:        Search for 'Better11' in Start Menu" -ForegroundColor White
}
Write-Host ""
Write-Host "Documentation: See README.md for more information" -ForegroundColor Cyan
