<#
.SYNOPSIS
    Better11 Performance Module - System performance optimization
.DESCRIPTION
    Optimizes Windows performance through visual effects, processor scheduling,
    memory management, and system responsiveness settings.
#>

$script:ModuleRoot = $PSScriptRoot

# Registry paths for performance settings
$script:PerformancePaths = @{
    VisualEffects = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects'
    Desktop = 'HKCU:\Control Panel\Desktop'
    WindowMetrics = 'HKCU:\Control Panel\Desktop\WindowMetrics'
    SystemProfile = 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile'
    MemoryManagement = 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management'
    PriorityControl = 'HKLM:\SYSTEM\CurrentControlSet\Control\PriorityControl'
    Power = 'HKLM:\SYSTEM\CurrentControlSet\Control\Power'
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

Write-Verbose "Better11 Performance module loaded"
