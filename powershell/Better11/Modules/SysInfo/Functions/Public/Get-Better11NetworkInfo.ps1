function Get-Better11NetworkInfo {
    <#
    .SYNOPSIS
        Gets network adapter information.
    .DESCRIPTION
        Retrieves active network adapter details.
    .EXAMPLE
        Get-Better11NetworkInfo
    #>
    [CmdletBinding()]
    param()

    try {
        $Adapters = Get-NetAdapter | Where-Object { $_.Status -eq 'Up' }
        
        $Results = foreach ($Adapter in $Adapters) {
            $IPConfig = Get-NetIPAddress -InterfaceIndex $Adapter.ifIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue
            $Gateway = Get-NetRoute -InterfaceIndex $Adapter.ifIndex -DestinationPrefix "0.0.0.0/0" -ErrorAction SilentlyContinue
            
            [PSCustomObject]@{
                Name = $Adapter.Name
                Description = $Adapter.InterfaceDescription
                MacAddress = $Adapter.MacAddress
                Status = $Adapter.Status
                SpeedMbps = [math]::Round($Adapter.LinkSpeed / 1000000, 0)
                IPAddresses = @($IPConfig.IPAddress)
                Gateway = if ($Gateway) { $Gateway.NextHop } else { $null }
                MediaType = $Adapter.MediaType
            }
        }
        
        return $Results
    }
    catch {
        Write-Error "Failed to get network info: $_"
        return @()
    }
}
