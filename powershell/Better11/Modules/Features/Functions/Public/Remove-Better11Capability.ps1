function Remove-Better11Capability {
    <#
    .SYNOPSIS
        Removes a Windows capability.
    .DESCRIPTION
        Uninstalls a Windows capability using DISM.
    .PARAMETER Name
        The capability name.
    .EXAMPLE
        Remove-Better11Capability -Name "Browser.InternetExplorer~~~~0.0.11.0"
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
        
        if ($Cap.State -eq 'NotPresent') {
            return [PSCustomObject]@{
                Success = $true
                Capability = $Name
                Message = "Already removed"
            }
        }
        
        Remove-WindowsCapability -Online -Name $Name
        
        return [PSCustomObject]@{
            Success = $true
            Capability = $Name
            Message = "Capability removed"
        }
    }
    catch {
        Write-Error "Failed to remove capability $Name: $_"
        return [PSCustomObject]@{ Success = $false; Capability = $Name; Error = $_.Exception.Message }
    }
}
