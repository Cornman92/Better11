function Get-Better11ActiveConnections {
    <#
    .SYNOPSIS
        Gets all active network connections.
    
    .DESCRIPTION
        Retrieves information about active TCP/UDP connections and listening ports.
    
    .PARAMETER Protocol
        Filter by protocol (TCP or UDP).
    
    .PARAMETER State
        Filter by connection state.
    
    .EXAMPLE
        Get-Better11ActiveConnections -Protocol TCP -State Established
    #>
    [CmdletBinding()]
    param(
        [Parameter()]
        [ValidateSet('TCP', 'UDP', 'All')]
        [string]$Protocol = 'All',
        
        [Parameter()]
        [ValidateSet('Established', 'Listen', 'TimeWait', 'All')]
        [string]$State = 'All'
    )
    
    try {
        $Connections = @()
        
        if ($Protocol -in @('TCP', 'All')) {
            $TCPConnections = Get-NetTCPConnection
            
            foreach ($Conn in $TCPConnections) {
                if ($State -ne 'All' -and $Conn.State -ne $State) {
                    continue
                }
                
                $Process = Get-Process -Id $Conn.OwningProcess -ErrorAction SilentlyContinue
                
                $Connections += [PSCustomObject]@{
                    Protocol = 'TCP'
                    LocalAddress = $Conn.LocalAddress
                    LocalPort = $Conn.LocalPort
                    RemoteAddress = $Conn.RemoteAddress
                    RemotePort = $Conn.RemotePort
                    State = $Conn.State
                    ProcessId = $Conn.OwningProcess
                    ProcessName = $Process.ProcessName
                }
            }
        }
        
        if ($Protocol -in @('UDP', 'All')) {
            $UDPEndpoints = Get-NetUDPEndpoint
            
            foreach ($Endpoint in $UDPEndpoints) {
                $Process = Get-Process -Id $Endpoint.OwningProcess -ErrorAction SilentlyContinue
                
                $Connections += [PSCustomObject]@{
                    Protocol = 'UDP'
                    LocalAddress = $Endpoint.LocalAddress
                    LocalPort = $Endpoint.LocalPort
                    RemoteAddress = $null
                    RemotePort = $null
                    State = 'N/A'
                    ProcessId = $Endpoint.OwningProcess
                    ProcessName = $Process.ProcessName
                }
            }
        }
        
        return $Connections | Sort-Object Protocol, LocalPort
    }
    catch {
        Write-Better11Log -Message "Failed to get active connections: $_" -Level Error
        throw
    }
}
