function Enable-Better11NagleAlgorithm {
    <#
    .SYNOPSIS
        Re-enables Nagle's algorithm (Windows default).
    .DESCRIPTION
        Restores TCP/IP packet coalescing to default behavior.
    .EXAMPLE
        Enable-Better11NagleAlgorithm
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param()

    if ($PSCmdlet.ShouldProcess("Nagle Algorithm", "Enable (restore default)")) {
        try {
            $InterfacesPath = 'HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces'
            $Modified = 0
            
            Get-ChildItem -Path $InterfacesPath | ForEach-Object {
                try {
                    Remove-ItemProperty -Path $_.PSPath -Name 'TcpAckFrequency' -ErrorAction SilentlyContinue
                    Remove-ItemProperty -Path $_.PSPath -Name 'TCPNoDelay' -ErrorAction SilentlyContinue
                    $Modified++
                } catch { }
            }
            
            Write-Verbose "Nagle algorithm restored on $Modified interfaces"
            return [PSCustomObject]@{ Success = $true; InterfacesModified = $Modified }
        }
        catch {
            Write-Error "Failed to enable Nagle algorithm: $_"
            return [PSCustomObject]@{ Success = $false; Error = $_.Exception.Message }
        }
    }
}
