function Get-Better11RestorePoints {
    <#
    .SYNOPSIS
        Lists system restore points.

    .DESCRIPTION
        Retrieves a list of available system restore points using Get-ComputerRestorePoint.
        Requires administrative privileges.

    .EXAMPLE
        Get-Better11RestorePoints
        Lists all restore points.
    #>
    [CmdletBinding()]
    param()

    process {
        if (-not (Test-Better11Administrator)) {
            Write-Better11Log -Message "Administrator privileges required" -Level "ERROR"
            throw "Administrator privileges required"
        }

        Write-Better11Log -Message "Getting restore points..." -Level "INFO"

        try {
            $points = Get-ComputerRestorePoint -ErrorAction Stop
            Write-Better11Log -Message "Found $(@($points).Count) restore points" -Level "INFO"
            return $points
        }
        catch {
            Write-Better11Log -Message "Failed to get restore points: $_" -Level "ERROR"
            throw
        }
    }
}
