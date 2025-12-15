function Set-Better11ServiceStartMode {
    <#
    .SYNOPSIS
        Sets service start mode.

    .DESCRIPTION
        Changes the start mode of a Windows service (Automatic, Manual, Disabled).
        Requires administrative privileges.

    .PARAMETER Name
        Service name.

    .PARAMETER StartupType
        Startup type (Automatic, Manual, Disabled).

    .EXAMPLE
        Set-Better11ServiceStartMode -Name "Spooler" -StartupType Disabled
        Disables the Print Spooler service.
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory=$true)]
        [string]$Name,

        [Parameter(Mandatory=$true)]
        [ValidateSet("Automatic", "Manual", "Disabled")]
        [string]$StartupType
    )

    process {
        if (-not (Test-Better11Administrator)) {
            Write-Better11Log -Message "Administrator privileges required" -Level "ERROR"
            throw "Administrator privileges required"
        }

        if ($PSCmdlet.ShouldProcess($Name, "Set Startup Type to $StartupType")) {
            Write-Better11Log -Message "Setting service '$Name' startup type to $StartupType..." -Level "INFO"

            try {
                Set-Service -Name $Name -StartupType $StartupType -ErrorAction Stop
                
                # If disabled, also stop it
                if ($StartupType -eq "Disabled") {
                    Stop-Service -Name $Name -Force -ErrorAction SilentlyContinue
                }

                Write-Better11Log -Message "Service configuration updated successfully" -Level "SUCCESS"
            }
            catch {
                Write-Better11Log -Message "Failed to configure service: $_" -Level "ERROR"
                throw
            }
        }
    }
}
