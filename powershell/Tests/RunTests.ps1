<#
.SYNOPSIS
    Run all Pester tests for Better11 PowerShell modules

.DESCRIPTION
    This script runs all Pester tests and generates a report.
    Requires Pester 5.0 or later.

.EXAMPLE
    .\RunTests.ps1
    
.EXAMPLE
    .\RunTests.ps1 -Detailed
#>

[CmdletBinding()]
param(
    [switch]$Detailed,
    [string]$TestPath = $PSScriptRoot,
    [string]$OutputFile
)

# Check if Pester is installed
if (-not (Get-Module -ListAvailable -Name Pester)) {
    Write-Host "Pester is not installed. Installing..." -ForegroundColor Yellow
    try {
        Install-Module -Name Pester -Force -SkipPublisherCheck -Scope CurrentUser
        Write-Host "Pester installed successfully" -ForegroundColor Green
    }
    catch {
        Write-Error "Failed to install Pester: $_"
        exit 1
    }
}

# Import Pester
Import-Module Pester -MinimumVersion 5.0

Write-Host "`n===================================" -ForegroundColor Cyan
Write-Host "  Better11 PowerShell Test Suite" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan

# Configure Pester
$config = New-PesterConfiguration
$config.Run.Path = $TestPath
$config.Run.Exit = $false
$config.TestResult.Enabled = $true

if ($OutputFile) {
    $config.TestResult.OutputPath = $OutputFile
}

if ($Detailed) {
    $config.Output.Verbosity = 'Detailed'
}
else {
    $config.Output.Verbosity = 'Normal'
}

# Run tests
Write-Host "`nRunning tests from: $TestPath`n" -ForegroundColor Yellow
$result = Invoke-Pester -Configuration $config

# Display summary
Write-Host "`n===================================" -ForegroundColor Cyan
Write-Host "  Test Summary" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan

Write-Host "Total Tests:  " -NoNewline
Write-Host $result.Tests.Count -ForegroundColor White

Write-Host "Passed:       " -NoNewline
Write-Host $result.Passed.Count -ForegroundColor Green

if ($result.Failed.Count -gt 0) {
    Write-Host "Failed:       " -NoNewline
    Write-Host $result.Failed.Count -ForegroundColor Red
}

if ($result.Skipped.Count -gt 0) {
    Write-Host "Skipped:      " -NoNewline
    Write-Host $result.Skipped.Count -ForegroundColor Yellow
}

$duration = $result.Duration.TotalSeconds
Write-Host "Duration:     " -NoNewline
Write-Host ("{0:N2}s" -f $duration) -ForegroundColor White

Write-Host ""

# Exit code based on results
if ($result.Failed.Count -gt 0) {
    Write-Host "⚠ Some tests failed!" -ForegroundColor Red
    exit 1
}
else {
    Write-Host "✓ All tests passed!" -ForegroundColor Green
    exit 0
}
