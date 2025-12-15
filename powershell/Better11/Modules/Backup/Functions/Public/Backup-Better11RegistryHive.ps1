function Backup-Better11RegistryHive {
    <#
    .SYNOPSIS
        Backs up a registry hive.

    .DESCRIPTION
        Exports a registry hive to a file using reg.exe.
        Requires administrative privileges.

    .PARAMETER Hive
        The registry hive to backup (e.g., HKLM\Software).

    .PARAMETER Path
        The path where the backup file will be saved.

    .EXAMPLE
        Backup-Better11RegistryHive -Hive "HKLM\Software" -Path "C:\Backups\Software.reg"
        Backs up HKLM\Software hive.
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory=$true)]
        [string]$Hive,

        [Parameter(Mandatory=$true)]
        [string]$Path
    )

    process {
        if (-not (Test-Better11Administrator)) {
            Write-Better11Log -Message "Administrator privileges required" -Level "ERROR"
            throw "Administrator privileges required"
        }

        if ($PSCmdlet.ShouldProcess($Hive, "Backup to $Path")) {
            Write-Better11Log -Message "Backing up registry hive $Hive to $Path..." -Level "INFO"

            try {
                # Ensure directory exists
                $dir = Split-Path $Path -Parent
                if (-not (Test-Path $dir)) {
                    New-Item -ItemType Directory -Path $dir -Force | Out-Null
                }

                $process = Start-Process -FilePath "reg.exe" -ArgumentList "export `"$Hive`" `"$Path`" /y" -Wait -NoNewWindow -PassThru
                
                if ($process.ExitCode -eq 0) {
                    Write-Better11Log -Message "Registry hive backed up successfully" -Level "SUCCESS"
                }
                else {
                    throw "reg.exe exited with code $($process.ExitCode)"
                }
            }
            catch {
                Write-Better11Log -Message "Failed to backup registry hive: $_" -Level "ERROR"
                throw
            }
        }
    }
}
