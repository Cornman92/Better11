function Enable-Better11FastStartup {
    <#
    .SYNOPSIS
        Enables Windows Fast Startup.
    .DESCRIPTION
        Enables Fast Startup (Hiberboot) for faster boot times.
    .EXAMPLE
        Enable-Better11FastStartup
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
        
        Set-ItemProperty -Path $RegPath -Name 'HiberbootEnabled' -Value 1 -Type DWord
        
        # Ensure hibernation is enabled (required for fast startup)
        & powercfg /hibernate on 2>&1 | Out-Null
        
        return [PSCustomObject]@{
            Success = $true
            FastStartup = 'Enabled'
            Message = 'Fast Startup enabled'
        }
    }
    catch {
        Write-Error "Failed to enable Fast Startup: $_"
        return [PSCustomObject]@{ Success = $false; Error = $_.Exception.Message }
    }
}
