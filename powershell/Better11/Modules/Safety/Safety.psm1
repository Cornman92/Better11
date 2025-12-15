<#
.SYNOPSIS
    Better11 Safety Module - System protection utilities
.DESCRIPTION
    Provides safety features including restore point management, registry backup,
    administrator checks, and user confirmations.
#>

$script:ModuleRoot = $PSScriptRoot

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

Write-Verbose "Better11 Safety module loaded"
