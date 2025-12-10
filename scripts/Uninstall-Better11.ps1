<#
.SYNOPSIS
    Uninstallation script for Better11.

.DESCRIPTION
    Removes the Better11 PowerShell module and WinUI application.

.EXAMPLE
    .\Uninstall-Better11.ps1
#>
[CmdletBinding()]
param(
    [Parameter()]
    [switch]$Force
)

$ErrorActionPreference = 'Stop'

Write-Host "Better11 Uninstallation Script" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan
Write-Host ""

if (-not $Force) {
    $Confirm = Read-Host "Are you sure you want to uninstall Better11? (yes/no)"
    if ($Confirm -ne 'yes') {
        Write-Host "Uninstallation cancelled." -ForegroundColor Yellow
        exit
    }
}

# Uninstall PowerShell Module
Write-Host "Removing PowerShell module..." -ForegroundColor Green

$ModulePath = "$env:USERPROFILE\Documents\PowerShell\Modules\Better11"
if (Test-Path $ModulePath) {
    Remove-Module Better11 -Force -ErrorAction SilentlyContinue
    Remove-Item $ModulePath -Recurse -Force
    Write-Host "  ✓ PowerShell module removed" -ForegroundColor Green
}
else {
    Write-Host "  Module not found" -ForegroundColor Yellow
}

# Uninstall GUI Application
Write-Host "Removing WinUI application..." -ForegroundColor Green

$App = Get-AppxPackage | Where-Object { $_.Name -like "*Better11*" }
if ($App) {
    Remove-AppxPackage -Package $App.PackageFullName
    Write-Host "  ✓ WinUI application removed" -ForegroundColor Green
}
else {
    Write-Host "  Application not found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Uninstallation complete!" -ForegroundColor Cyan
