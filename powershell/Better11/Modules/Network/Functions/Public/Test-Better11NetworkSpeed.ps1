function Test-Better11NetworkSpeed {
    <#
    .SYNOPSIS
        Tests network connectivity and speed.
    
    .DESCRIPTION
        Performs network connectivity tests including ping latency and basic throughput.
    
    .PARAMETER TestHosts
        Array of hosts to test connectivity against.
    
    .EXAMPLE
        Test-Better11NetworkSpeed -TestHosts @('8.8.8.8', 'google.com')
    #>
    [CmdletBinding()]
    param(
        [Parameter()]
        [string[]]$TestHosts = @('8.8.8.8', '1.1.1.1', 'google.com')
    )
    
    try {
        Write-Better11Log -Message "Testing network speed..." -Level Info
        
        $Results = foreach ($Host in $TestHosts) {
            $PingResult = Test-Connection -ComputerName $Host -Count 4 -ErrorAction SilentlyContinue
            
            if ($PingResult) {
                $AvgLatency = ($PingResult | Measure-Object -Property ResponseTime -Average).Average
                $MinLatency = ($PingResult | Measure-Object -Property ResponseTime -Minimum).Minimum
                $MaxLatency = ($PingResult | Measure-Object -Property ResponseTime -Maximum).Maximum
                $PacketLoss = (4 - $PingResult.Count) / 4 * 100
                
                [PSCustomObject]@{
                    Host = $Host
                    Status = 'Online'
                    AverageLatencyMs = [math]::Round($AvgLatency, 2)
                    MinLatencyMs = $MinLatency
                    MaxLatencyMs = $MaxLatency
                    PacketLossPercent = $PacketLoss
                }
            }
            else {
                [PSCustomObject]@{
                    Host = $Host
                    Status = 'Offline'
                    AverageLatencyMs = 0
                    MinLatencyMs = 0
                    MaxLatencyMs = 0
                    PacketLossPercent = 100
                }
            }
        }
        
        return $Results
    }
    catch {
        Write-Better11Log -Message "Network speed test failed: $_" -Level Error
        throw
    }
}
