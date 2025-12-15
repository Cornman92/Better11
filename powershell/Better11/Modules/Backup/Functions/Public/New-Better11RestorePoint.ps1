function New-Better11RestorePoint {
    <#
    .SYNOPSIS
        Creates a system restore point.

    .DESCRIPTION
        Creates a new system restore point using Checkpoint-Computer.
        Requires administrative privileges.

    .PARAMETER Description
        Description for the restore point.

    .EXAMPLE
        New-Better11RestorePoint -Description "Before installing apps"
        Creates a restore point.
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory=$true)]
        [string]$Description
    )

    process {
        if (-not (Test-Better11Administrator)) {
            Write-Better11Log -Message "Administrator privileges required" -Level "ERROR"
            throw "Administrator privileges required"
        }

        if ($PSCmdlet.ShouldProcess("System", "Create Restore Point '$Description'")) {
            Write-Better11Log -Message "Creating restore point '$Description'..." -Level "INFO"

            try {
                Checkpoint-Computer -Description $Description -RestorePointType "MODIFY_SETTINGS" -ErrorAction Stop
                Write-Better11Log -Message "Restore point created successfully" -Level "SUCCESS"
            }
            catch {
                Write-Better11Log -Message "Failed to create restore point: $_" -Level "ERROR"
                throw
            }
        }
    }
}
