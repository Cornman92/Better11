<#
.SYNOPSIS
    Better11 Drivers Module - Driver management
.DESCRIPTION
    Manages hardware drivers: list, backup, update, and troubleshoot.
#>

$script:ModuleRoot = $PSScriptRoot

# Default backup location
$script:DefaultBackupPath = Join-Path $env:USERPROFILE 'Better11\DriverBackups'

# Import public functions
$PublicFunctions = @(Get-ChildItem -Path "$PSScriptRoot\Functions\Public\*.ps1" -ErrorAction SilentlyContinue)
foreach ($Function in $PublicFunctions) {
    try {
        . $Function.FullName
        Export-ModuleMember -Function $Function.BaseName
    } catch {
        Write-Error "Failed to import function $($Function.FullName): $_"
    }
}

Write-Verbose "Better11 Drivers module loaded"
