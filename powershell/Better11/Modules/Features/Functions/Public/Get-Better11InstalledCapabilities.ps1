function Get-Better11InstalledCapabilities {
    <#
    .SYNOPSIS
        Gets Windows capabilities.
    .DESCRIPTION
        Lists installed and available Windows capabilities.
    .PARAMETER Installed
        Only show installed capabilities.
    .EXAMPLE
        Get-Better11InstalledCapabilities
        Get-Better11InstalledCapabilities -Installed
    #>
    [CmdletBinding()]
    param(
        [Parameter()]
        [switch]$Installed
    )

    try {
        $Capabilities = Get-WindowsCapability -Online
        
        if ($Installed) {
            $Capabilities = $Capabilities | Where-Object { $_.State -eq 'Installed' }
        }
        
        $Results = foreach ($Cap in $Capabilities) {
            [PSCustomObject]@{
                Name = $Cap.Name
                State = $Cap.State
                DisplayName = ($Cap.Name -split '~')[0]
            }
        }
        
        return $Results
    }
    catch {
        Write-Error "Failed to get capabilities: $_"
        return @()
    }
}
