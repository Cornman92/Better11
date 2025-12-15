function Get-Better11NetworkInfo {
    <#
    .SYNOPSIS
        Gets detailed network adapter information.
    
    .DESCRIPTION
        Retrieves information about all network adapters including IP configuration,
        status, and statistics.
    
    .EXAMPLE
        Get-Better11NetworkInfo
    #>
    [CmdletBinding()]
    param()
    
    try {
        $Adapters = Get-NetAdapter | Where-Object { $_.Status -eq 'Up' }
        
        $NetworkInfo = foreach ($Adapter in $Adapters) {
            $IPConfig = Get-NetIPAddress -InterfaceIndex $Adapter.ifIndex -ErrorAction SilentlyContinue
            $DNSServers = Get-DnsClientServerAddress -InterfaceIndex $Adapter.ifIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue
            $Gateway = Get-NetRoute -InterfaceIndex $Adapter.ifIndex -DestinationPrefix '0.0.0.0/0' -ErrorAction SilentlyContinue
            
            [PSCustomObject]@{
                Name = $Adapter.Name
                Description = $Adapter.InterfaceDescription
                Status = $Adapter.Status
                Speed = $Adapter.LinkSpeed
                MacAddress = $Adapter.MacAddress
                IPv4Address = ($IPConfig | Where-Object { $_.AddressFamily -eq 'IPv4' }).IPAddress
                IPv6Address = ($IPConfig | Where-Object { $_.AddressFamily -eq 'IPv6' }).IPAddress
                Gateway = $Gateway.NextHop
                DNSServers = $DNSServers.ServerAddresses -join ', '
                BytesReceived = $Adapter.Statistics.ReceivedBytes
                BytesSent = $Adapter.Statistics.SentBytes
            }
        }
        
        return $NetworkInfo
    }
    catch {
        Write-Better11Log -Message "Failed to get network info: $_" -Level Error
        throw
    }
}
