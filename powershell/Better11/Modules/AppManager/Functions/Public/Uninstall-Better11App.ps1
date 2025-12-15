function Uninstall-Better11App {
    <#
    .SYNOPSIS
        Uninstalls an application.

    .DESCRIPTION
        Uninstalls an application using its uninstall string.
        Attempts to make the uninstallation silent if possible (best effort).

    .PARAMETER UninstallString
        The command to run to uninstall the application.

    .EXAMPLE
        Uninstall-Better11App -UninstallString "msiexec /x {GUID}"
        Uninstalls an app.
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory=$true)]
        [string]$UninstallString
    )

    process {
        if ($PSCmdlet.ShouldProcess($UninstallString, "Uninstall Application")) {
            Write-Better11Log -Message "Uninstalling application..." -Level "INFO"

            try {
                # Parse the uninstall string (basic handling)
                # cmd /c or directly exe
                
                # Simple execution for now
                Start-Process -FilePath "cmd.exe" -ArgumentList "/c $UninstallString" -Wait -NoNewWindow
                
                Write-Better11Log -Message "Uninstallation command executed" -Level "SUCCESS"
            }
            catch {
                Write-Better11Log -Message "Failed to uninstall application: $_" -Level "ERROR"
                throw
            }
        }
    }
}
