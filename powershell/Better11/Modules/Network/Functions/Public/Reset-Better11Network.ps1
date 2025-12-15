function Reset-Better11Network {
    <#
    .SYNOPSIS
        Resets network configuration to defaults.
    
    .DESCRIPTION
        Performs a network reset including:
        - Flush DNS cache
        - Reset TCP/IP stack
        - Reset Winsock catalog
        - Renew IP address
    
    .PARAMETER Force
        Skip confirmation prompt.
    
    .EXAMPLE
        Reset-Better11Network
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter()]
        [switch]$Force
    )
    
    if (-not (Test-Better11Administrator)) {
        throw "This function requires administrator privileges"
    }
    
    if (-not $Force) {
        $Message = "Reset network configuration? This will temporarily disconnect you from the network."
        if (-not (Confirm-Better11Action -Message $Message)) {
            Write-Better11Log -Message "Network reset cancelled" -Level Info
            return
        }
    }
    
    try {
        Write-Better11Log -Message "Resetting network configuration..." -Level Info
        
        $Results = @()
        
        # Flush DNS cache
        Write-Better11Log -Message "Flushing DNS cache..." -Level Info
        Clear-DnsClientCache
        $Results += "DNS cache flushed"
        
        # Reset TCP/IP stack
        Write-Better11Log -Message "Resetting TCP/IP stack..." -Level Info
        netsh int ip reset | Out-Null
        $Results += "TCP/IP stack reset"
        
        # Reset Winsock catalog
        Write-Better11Log -Message "Resetting Winsock catalog..." -Level Info
        netsh winsock reset | Out-Null
        $Results += "Winsock catalog reset"
        
        # Renew IP addresses
        Write-Better11Log -Message "Renewing IP addresses..." -Level Info
        $Adapters = Get-NetAdapter | Where-Object { $_.Status -eq 'Up' }
        foreach ($Adapter in $Adapters) {
            try {
                ipconfig /release $Adapter.Name | Out-Null
                ipconfig /renew $Adapter.Name | Out-Null
                $Results += "IP renewed for $($Adapter.Name)"
            }
            catch {
                Write-Better11Log -Message "Failed to renew IP for $($Adapter.Name): $_" -Level Warning
            }
        }
        
        Write-Better11Log -Message "Network reset completed. Please restart your computer." -Level Info
        
        return [PSCustomObject]@{
            Success = $true
            ActionsPerformed = $Results
            Message = "Network reset completed. Restart required."
        }
    }
    catch {
        Write-Better11Log -Message "Network reset failed: $_" -Level Error
        throw
    }
}
