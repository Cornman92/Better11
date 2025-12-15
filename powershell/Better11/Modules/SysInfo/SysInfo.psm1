<#
.SYNOPSIS
    Better11 SysInfo Module - System information gathering
.DESCRIPTION
    Comprehensive system information including hardware, software,
    Windows version, and system health details.
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

Write-Verbose "Better11 SysInfo module loaded"
