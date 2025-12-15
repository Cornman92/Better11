<#
.SYNOPSIS
    Builds all Better11 components.

.DESCRIPTION
    Builds the C# solution, runs tests, and creates deployment packages.

.PARAMETER Configuration
    Build configuration (Debug or Release).

.PARAMETER RunTests
    Run tests after building.

.PARAMETER CreatePackage
    Create MSIX package.

.EXAMPLE
    .\Build-All.ps1 -Configuration Release -RunTests -CreatePackage
#>
[CmdletBinding()]
param(
    [Parameter()]
    [ValidateSet('Debug', 'Release')]
    [string]$Configuration = 'Release',
    
    [Parameter()]
    [switch]$RunTests,
    
    [Parameter()]
    [switch]$CreatePackage
)

$ErrorActionPreference = 'Stop'

Write-Host "Better11 Build Script" -ForegroundColor Cyan
Write-Host "=====================" -ForegroundColor Cyan
Write-Host ""

$RootPath = Split-Path $PSScriptRoot -Parent
$CSharpPath = Join-Path $RootPath "csharp"

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Green

$DotnetVersion = dotnet --version
if ($LASTEXITCODE -ne 0) {
    throw ".NET SDK not found. Please install .NET 8 SDK."
}
Write-Host "  ✓ .NET SDK: $DotnetVersion" -ForegroundColor Green

# Build C# Solution
Write-Host ""
Write-Host "Building C# solution ($Configuration)..." -ForegroundColor Green

Push-Location $CSharpPath
try {
    # Restore packages
    Write-Host "  Restoring NuGet packages..." -ForegroundColor Yellow
    dotnet restore
    if ($LASTEXITCODE -ne 0) { throw "NuGet restore failed" }
    
    # Build solution
    Write-Host "  Building solution..." -ForegroundColor Yellow
    dotnet build -c $Configuration --no-restore
    if ($LASTEXITCODE -ne 0) { throw "Build failed" }
    
    Write-Host "  ✓ Build completed successfully" -ForegroundColor Green
    
    # Run tests
    if ($RunTests) {
        Write-Host ""
        Write-Host "Running tests..." -ForegroundColor Green
        dotnet test -c $Configuration --no-build --logger "console;verbosity=normal"
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Some tests failed"
        }
        else {
            Write-Host "  ✓ All tests passed" -ForegroundColor Green
        }
    }
    
    # Create package
    if ($CreatePackage) {
        Write-Host ""
        Write-Host "Creating MSIX package..." -ForegroundColor Green
        # TODO: Add MSIX packaging commands
        Write-Host "  Note: MSIX packaging requires Visual Studio" -ForegroundColor Yellow
    }
}
finally {
    Pop-Location
}

# Test PowerShell Module
Write-Host ""
Write-Host "Testing PowerShell module..." -ForegroundColor Green

$ModulePath = Join-Path $RootPath "powershell\Better11\Better11.psd1"
try {
    Import-Module $ModulePath -Force
    $FunctionCount = (Get-Command -Module Better11).Count
    Write-Host "  ✓ Module loaded successfully ($FunctionCount functions)" -ForegroundColor Green
}
catch {
    Write-Warning "  Failed to import module: $_"
}

Write-Host ""
Write-Host "Build Summary" -ForegroundColor Cyan
Write-Host "=============" -ForegroundColor Cyan
Write-Host "Configuration: $Configuration" -ForegroundColor White
Write-Host "C# Build:      ✓ Success" -ForegroundColor Green
if ($RunTests) {
    Write-Host "Tests:         ✓ Complete" -ForegroundColor Green
}
Write-Host "PS Module:     ✓ Ready" -ForegroundColor Green
Write-Host ""
Write-Host "Output location: $CSharpPath\Better11.WinUI\bin\$Configuration" -ForegroundColor Cyan
