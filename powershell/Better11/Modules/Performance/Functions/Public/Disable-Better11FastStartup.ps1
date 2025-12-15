function Disable-Better11FastStartup {
    <#
    .SYNOPSIS
        Disables Windows Fast Startup.
    .DESCRIPTION
        Disables Fast Startup. Recommended for dual-boot systems.
    .EXAMPLE
        Disable-Better11FastStartup
    #>
    [CmdletBinding()]
    param()

    try {
        if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
            throw "Administrator privileges required"
        }
        
        $RegPath = 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Power'
        
        if (-not (Test-Path $RegPath)) {
            New-Item -Path $RegPath -Force | Out-Null
        }
        
        Set-ItemProperty -Path $RegPath -Name 'HiberbootEnabled' -Value 0 -Type DWord
        
        return [PSCustomObject]@{
            Success = $true
            FastStartup = 'Disabled'
            Message = 'Fast Startup disabled'
        }
    }
    catch {
        Write-Error "Failed to disable Fast Startup: $_"
        return [PSCustomObject]@{ Success = $false; Error = $_.Exception.Message }
    }
}
