function Disable-Better11NagleAlgorithm {
    <#
    .SYNOPSIS
        Disables Nagle's algorithm for reduced network latency.
    .DESCRIPTION
        Disables TCP/IP packet coalescing to reduce network latency in games.
    .EXAMPLE
        Disable-Better11NagleAlgorithm
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param()

    if ($PSCmdlet.ShouldProcess("Nagle Algorithm", "Disable")) {
        try {
            $InterfacesPath = 'HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces'
            $Modified = 0
            
            Get-ChildItem -Path $InterfacesPath | ForEach-Object {
                try {
                    Set-ItemProperty -Path $_.PSPath -Name 'TcpAckFrequency' -Value 1 -Type DWord -ErrorAction SilentlyContinue
                    Set-ItemProperty -Path $_.PSPath -Name 'TCPNoDelay' -Value 1 -Type DWord -ErrorAction SilentlyContinue
                    $Modified++
                } catch { }
            }
            
            Write-Verbose "Nagle algorithm disabled on $Modified interfaces"
            return [PSCustomObject]@{ Success = $true; InterfacesModified = $Modified }
        }
        catch {
            Write-Error "Failed to disable Nagle algorithm: $_"
            return [PSCustomObject]@{ Success = $false; Error = $_.Exception.Message }
        }
    }
}
