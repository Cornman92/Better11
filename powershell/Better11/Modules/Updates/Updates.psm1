<#
.SYNOPSIS
    Better11 Updates Module - Windows Update management
.DESCRIPTION
    Comprehensive Windows Update management including checking, installing,
    pausing updates, and configuring update settings.
#>

$script:ModuleRoot = $PSScriptRoot
$script:UpdateSettingsPath = 'HKLM:\SOFTWARE\Microsoft\WindowsUpdate\UX\Settings'

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

Write-Verbose "Better11 Updates module loaded"
