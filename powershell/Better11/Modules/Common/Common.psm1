<#
.SYNOPSIS
    Common utilities module for Better11

.DESCRIPTION
    Provides shared functionality used across all Better11 modules including
    logging, administrator checks, user confirmation, and backup utilities.
#>

# Import public functions
$Public = @(Get-ChildItem -Path $PSScriptRoot\Functions\Public\*.ps1 -ErrorAction SilentlyContinue)
$Private = @(Get-ChildItem -Path $PSScriptRoot\Functions\Private\*.ps1 -ErrorAction SilentlyContinue)

# Dot source the files
foreach ($import in @($Public + $Private)) {
    try {
        . $import.FullName
    }
    catch {
        Write-Error "Failed to import function $($import.FullName): $_"
    }
}

# Export public functions
Export-ModuleMember -Function $Public.BaseName
