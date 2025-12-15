function Add-Better11Capability {
    <#
    .SYNOPSIS
        Adds a Windows capability.
    .DESCRIPTION
        Installs a Windows capability using DISM.
    .PARAMETER Name
        The capability name.
    .EXAMPLE
        Add-Better11Capability -Name "OpenSSH.Client~~~~0.0.1.0"
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name
    )

    try {
        if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
            throw "Administrator privileges required"
        }
        
        $Cap = Get-WindowsCapability -Online -Name $Name -ErrorAction Stop
        
        if ($Cap.State -eq 'Installed') {
            return [PSCustomObject]@{
                Success = $true
                Capability = $Name
                Message = "Already installed"
            }
        }
        
        Add-WindowsCapability -Online -Name $Name
        
        return [PSCustomObject]@{
            Success = $true
            Capability = $Name
            Message = "Capability installed"
        }
    }
    catch {
        Write-Error "Failed to add capability $Name: $_"
        return [PSCustomObject]@{ Success = $false; Capability = $Name; Error = $_.Exception.Message }
    }
}
