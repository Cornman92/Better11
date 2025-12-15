<#
.SYNOPSIS
    Better11 Shell Module - Windows 11 shell customization
.DESCRIPTION
    Comprehensive customization options for the Windows 11 taskbar,
    Start menu, context menus, and other shell elements.
#>

$script:ModuleRoot = $PSScriptRoot
$script:ExplorerAdvanced = 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced'
$script:ExplorerSearch = 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Search'

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

Write-Verbose "Better11 Shell module loaded"
