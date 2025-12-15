<#
.SYNOPSIS
    Better11 Startup Module - Startup program management
.DESCRIPTION
    Manages programs that run at Windows startup.
#>

$script:ModuleRoot = $PSScriptRoot

# Registry locations for startup programs
$script:StartupRegistryPaths = @{
    CurrentUserRun = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run'
    LocalMachineRun = 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run'
    CurrentUserRunOnce = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\RunOnce'
    LocalMachineRunOnce = 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce'
}

# Startup folder locations
$script:StartupFolders = @{
    CurrentUser = [Environment]::GetFolderPath('Startup')
    AllUsers = [Environment]::GetFolderPath('CommonStartup')
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

Write-Verbose "Better11 Startup module loaded"
