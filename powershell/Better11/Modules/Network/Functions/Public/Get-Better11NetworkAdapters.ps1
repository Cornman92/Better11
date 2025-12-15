function Get-Better11NetworkAdapters {
    <#
    .SYNOPSIS
        Lists network adapters with their configuration.

    .DESCRIPTION
        Returns detailed information about network adapters, including IP addresses,
        DNS servers, and status.

    .PARAMETER PhysicalOnly
        If set, only returns physical network adapters.

    .EXAMPLE
        Get-Better11NetworkAdapters
        Lists all network adapters.

    .EXAMPLE
        Get-Better11NetworkAdapters -PhysicalOnly
        Lists only physical adapters.
    #>
    [CmdletBinding()]
    param(
        [switch]$PhysicalOnly
    )

    process {
        Write-Better11Log -Message "Getting network adapters info..." -Level "INFO"

        try {
            $params = @{}
            if ($PhysicalOnly) {
                $params['Physical'] = $true
            }

            $adapters = Get-NetAdapter @params | ForEach-Object {
                $config = Get-NetIPConfiguration -InterfaceAlias $_.Name -ErrorAction SilentlyContinue

                [PSCustomObject]@{
                    Name = $_.Name
                    Description = $_.InterfaceDescription
                    Status = $_.Status
                    MacAddress = $_.MacAddress
                    LinkSpeed = $_.LinkSpeed
                    IPv4Address = $config.IPv4Address.IPAddress
                    IPv6Address = $config.IPv6Address.IPAddress
                    DNSServers = $config.DNSServer.ServerAddresses
                    IsPhysical = $_.Physical
                    InterfaceIndex = $_.InterfaceIndex
                }
            }

            Write-Better11Log -Message "Found $(@($adapters).Count) adapters" -Level "INFO"
            return $adapters
        }
        catch {
            Write-Better11Log -Message "Failed to get network adapters: $_" -Level "ERROR"
            throw
        }
    }
}
