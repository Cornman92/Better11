function Install-Better11App {
    <#
    .SYNOPSIS
        Installs an application from a file.

    .DESCRIPTION
        Installs an application using its installer file (MSI, EXE, etc.).
        Supports silent installation arguments.

    .PARAMETER Path
        Path to the installer file.

    .PARAMETER Arguments
        Arguments to pass to the installer.

    .EXAMPLE
        Install-Better11App -Path "C:\Downloads\app.msi" -Arguments "/quiet"
        Installs an MSI silently.
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory=$true)]
        [string]$Path,

        [string]$Arguments
    )

    process {
        if ($PSCmdlet.ShouldProcess($Path, "Install Application")) {
            Write-Better11Log -Message "Installing application from $Path..." -Level "INFO"

            try {
                if (-not (Test-Path $Path)) {
                    throw "Installer file not found: $Path"
                }

                $process = Start-Process -FilePath $Path -ArgumentList $Arguments -Wait -NoNewWindow -PassThru
                
                if ($process.ExitCode -eq 0) {
                    Write-Better11Log -Message "Application installed successfully" -Level "SUCCESS"
                }
                else {
                    Write-Better11Log -Message "Installer exited with code $($process.ExitCode)" -Level "WARNING"
                }
            }
            catch {
                Write-Better11Log -Message "Failed to install application: $_" -Level "ERROR"
                throw
            }
        }
    }
}
