<#
.SYNOPSIS
    Better11 Gaming Module - Gaming optimization
.DESCRIPTION
    Gaming-related optimizations including Game Mode, GPU scheduling,
    network optimization, and performance tweaks.
#>

$script:ModuleRoot = $PSScriptRoot
$script:GameBarPath = 'HKCU:\SOFTWARE\Microsoft\GameBar'
$script:GameDVRPath = 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR'
$script:GPUSchedulingPath = 'HKLM:\SYSTEM\CurrentControlSet\Control\GraphicsDrivers'
$script:MousePath = 'HKCU:\Control Panel\Mouse'
$script:NetworkPath = 'HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces'

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

Write-Verbose "Better11 Gaming module loaded"
