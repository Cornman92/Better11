function Test-Better11NetworkConnectivity {
    <#
    .SYNOPSIS
        Tests network connectivity.

    .DESCRIPTION
        Performs ping tests to known reliable hosts (Google DNS, Cloudflare DNS)
        to verify internet connectivity.

    .PARAMETER Targets
        List of IP addresses or hostnames to ping. Defaults to 8.8.8.8 and 1.1.1.1.

    .EXAMPLE
        Test-Better11NetworkConnectivity
        Tests connectivity to default targets.
    #>
    [CmdletBinding()]
    param(
        [string[]]$Targets = @("8.8.8.8", "1.1.1.1", "www.google.com")
    )

    process {
        Write-Better11Log -Message "Testing network connectivity..." -Level "INFO"

        $results = @()

        foreach ($target in $Targets) {
            try {
                $ping = Test-Connection -ComputerName $target -Count 1 -ErrorAction SilentlyContinue
                
                $status = if ($ping) { "Success" } else { "Failed" }
                $latency = if ($ping) { $ping.ResponseTime } else { $null }

                $results += [PSCustomObject]@{
                    Target = $target
                    Status = $status
                    LatencyMS = $latency
                }
            }
            catch {
                 $results += [PSCustomObject]@{
                    Target = $target
                    Status = "Error"
                    LatencyMS = $null
                }
            }
        }

        $successCount = ($results | Where-Object { $_.Status -eq "Success" }).Count
        
        if ($successCount -gt 0) {
            Write-Better11Log -Message "Network connectivity verified ($successCount/$($Targets.Count) targets reachable)" -Level "INFO"
        }
        else {
            Write-Better11Log -Message "Network connectivity check failed" -Level "WARNING"
        }

        return $results
    }
}
