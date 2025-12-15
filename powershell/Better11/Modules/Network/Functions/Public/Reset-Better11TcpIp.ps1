function Reset-Better11TcpIp {
    <#
    .SYNOPSIS
        Resets the TCP/IP stack.

    .DESCRIPTION
        Resets TCP/IP configuration to default settings.
        Requires administrative privileges and a system restart to take effect.

    .EXAMPLE
        Reset-Better11TcpIp
        Resets TCP/IP stack.
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param()

    process {
        if (-not (Test-Better11Administrator)) {
            Write-Better11Log -Message "Administrator privileges required" -Level "ERROR"
            throw "Administrator privileges required"
        }

        if ($PSCmdlet.ShouldProcess("System", "Reset TCP/IP Stack")) {
            Write-Better11Log -Message "Resetting TCP/IP stack..." -Level "INFO"

            try {
                # Reset IPv4
                Start-Process -FilePath "netsh.exe" -ArgumentList "int ip reset" -Wait -NoNewWindow
                
                # Reset IPv6
                Start-Process -FilePath "netsh.exe" -ArgumentList "int ipv6 reset" -Wait -NoNewWindow

                Write-Better11Log -Message "TCP/IP stack reset successfully. A restart is required." -Level "SUCCESS"
                Write-Warning "You must restart your computer for these changes to take effect."
            }
            catch {
                Write-Better11Log -Message "Failed to reset TCP/IP stack: $_" -Level "ERROR"
                throw
            }
        }
    }
}
