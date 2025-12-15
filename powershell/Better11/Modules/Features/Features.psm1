<#
.SYNOPSIS
    Better11 Features Module - Windows Optional Features and Capabilities management
.DESCRIPTION
    Enables, disables, and queries Windows optional features and capabilities.
#>

$script:ModuleRoot = $PSScriptRoot

# Common optional features
$script:CommonFeatures = @{
    'WSL' = 'Microsoft-Windows-Subsystem-Linux'
    'HyperV' = 'Microsoft-Hyper-V-All'
    'Sandbox' = 'Containers-DisposableClientVM'
    'NetFramework35' = 'NetFx3'
    'TelnetClient' = 'TelnetClient'
    'TFTP' = 'TFTP'
    'SMB1' = 'SMB1Protocol'
    'MediaPlayback' = 'MediaPlayback'
    'VirtualMachinePlatform' = 'VirtualMachinePlatform'
}

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

Write-Verbose "Better11 Features module loaded"
