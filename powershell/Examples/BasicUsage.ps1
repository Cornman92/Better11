#Requires -Version 5.1
#Requires -RunAsAdministrator

<#
.SYNOPSIS
    Better11 Basic Usage Examples

.DESCRIPTION
    Demonstrates basic usage of Better11 PowerShell module for common tasks.
#>

# Import the Better11 module
$ModulePath = Join-Path $PSScriptRoot '..' 'Better11' 'Better11.psd1'
Import-Module $ModulePath -Force

Write-Host "Better11 Basic Usage Examples" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan
Write-Host ""

# Example 1: List Available Applications
Write-Host "Example 1: List Available Applications" -ForegroundColor Green
Write-Host "---------------------------------------" -ForegroundColor Green
$apps = Get-Better11Apps
Write-Host "Found $($apps.Count) applications in catalog:"
$apps | Select-Object AppId, Name, Version, Installed | Format-Table -AutoSize
Write-Host ""

# Example 2: Check for Installed Applications
Write-Host "Example 2: Check Installed Applications" -ForegroundColor Green
Write-Host "----------------------------------------" -ForegroundColor Green
$installedApps = Get-Better11Apps -Installed
if ($installedApps.Count -gt 0) {
    Write-Host "Currently installed applications:"
    $installedApps | Select-Object Name, Version, InstalledDate | Format-Table -AutoSize
} else {
    Write-Host "No applications currently installed via Better11"
}
Write-Host ""

# Example 3: Install Application (Dry Run)
Write-Host "Example 3: Install Application (Dry Run)" -ForegroundColor Green
Write-Host "----------------------------------------" -ForegroundColor Green
Write-Host "Simulating installation of demo-app-msi..."
$dryRunResult = Install-Better11App -AppId "demo-app-msi" -DryRun -Force
Write-Host "Dry run result: $($dryRunResult.Status)"
Write-Host ""

# Example 4: Apply Registry Tweak (with confirmation)
Write-Host "Example 4: Apply Registry Tweak" -ForegroundColor Green
Write-Host "-------------------------------" -ForegroundColor Green
$tweak = @{
    Hive = 'HKCU'
    Path = 'Software\Better11\Examples'
    Name = 'ExampleValue'
    Value = 'Hello from Better11'
    Type = 'String'
}

Write-Host "This would apply a registry tweak to create:"
Write-Host "  HKCU:\Software\Better11\Examples\ExampleValue = 'Hello from Better11'"
Write-Host "(Skipped in example mode)"
Write-Host ""

# Example 5: Verify File Hash
Write-Host "Example 5: Verify File Hash" -ForegroundColor Green
Write-Host "----------------------------" -ForegroundColor Green

# Create a test file
$testFile = Join-Path $env:TEMP 'better11-test.txt'
"Better11 Test Content" | Out-File -FilePath $testFile -Encoding UTF8

# Calculate and verify hash
$hash = (Get-FileHash -Path $testFile -Algorithm SHA256).Hash
Write-Host "Created test file: $testFile"
Write-Host "Calculated hash: $hash"

$verifyResult = Verify-Better11FileHash -FilePath $testFile -ExpectedHash $hash
Write-Host "Hash verification: $($verifyResult.IsMatch)"

# Cleanup
Remove-Item -Path $testFile -Force
Write-Host ""

# Example 6: Check Windows Updates
Write-Host "Example 6: Check Windows Updates" -ForegroundColor Green
Write-Host "--------------------------------" -ForegroundColor Green
Write-Host "Checking for available Windows updates..."
try {
    $updates = Get-Better11WindowsUpdate | Select-Object -First 5
    if ($updates.Count -gt 0) {
        Write-Host "Found $($updates.Count) updates (showing first 5):"
        $updates | Select-Object Title, Type, SizeMB | Format-Table -AutoSize
    } else {
        Write-Host "No updates available"
    }
}
catch {
    Write-Host "Could not check for updates (requires administrator privileges and Windows Update service)"
}
Write-Host ""

# Example 7: Privacy Settings (Dry Run)
Write-Host "Example 7: Privacy Settings" -ForegroundColor Green
Write-Host "---------------------------" -ForegroundColor Green
Write-Host "Privacy presets available:"
Write-Host "  - MaximumPrivacy: Disables telemetry, advertising ID, Cortana"
Write-Host "  - Balanced: Moderate privacy with some features enabled"
Write-Host "  - Default: Windows default settings"
Write-Host "(Use Set-Better11PrivacySetting -Preset MaximumPrivacy to apply)"
Write-Host ""

# Example 8: Create Restore Point
Write-Host "Example 8: Create Restore Point" -ForegroundColor Green
Write-Host "--------------------------------" -ForegroundColor Green
Write-Host "Creating a system restore point..."
try {
    $restoreResult = New-Better11RestorePoint -Description "Better11 Examples Session" -WhatIf
    Write-Host "Restore point would be created (WhatIf mode)"
}
catch {
    Write-Host "Could not create restore point (requires System Restore to be enabled)"
}
Write-Host ""

# Summary
Write-Host "Examples Complete!" -ForegroundColor Cyan
Write-Host "==================" -ForegroundColor Cyan
Write-Host ""
Write-Host "For more information, use:" -ForegroundColor Green
Write-Host "  Get-Help <command> -Full" -ForegroundColor White
Write-Host "  Get-Command -Module Better11" -ForegroundColor White
Write-Host ""
Write-Host "Available commands:" -ForegroundColor Green
Get-Command -Module Better11 | Select-Object Name | Format-Wide -Column 3
