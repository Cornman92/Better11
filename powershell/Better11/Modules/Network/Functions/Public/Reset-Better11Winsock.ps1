function Reset-Better11Winsock {
    <#
    .SYNOPSIS
        Resets the Winsock catalog.

    .DESCRIPTION
        Resets Winsock Catalog to default settings.
        Useful for fixing network connectivity issues caused by socket errors.
        Requires administrative privileges and a system restart.

    .EXAMPLE
        Reset-Better11Winsock
        Resets Winsock catalog.
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param()

    process {
        if (-not (Test-Better11Administrator)) {
            Write-Better11Log -Message "Administrator privileges required" -Level "ERROR"
            throw "Administrator privileges required"
        }

        if ($PSCmdlet.ShouldProcess("System", "Reset Winsock Catalog")) {
            Write-Better11Log -Message "Resetting Winsock catalog..." -Level "INFO"

            try {
                Start-Process -FilePath "netsh.exe" -ArgumentList "winsock reset" -Wait -NoNewWindow

                Write-Better11Log -Message "Winsock catalog reset successfully. A restart is required." -Level "SUCCESS"
                Write-Warning "You must restart your computer for these changes to take effect."
            }
            catch {
                Write-Better11Log -Message "Failed to reset Winsock: $_" -Level "ERROR"
                throw
            }
        }
    }
}
