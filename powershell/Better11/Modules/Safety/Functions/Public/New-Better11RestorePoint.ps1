function New-Better11RestorePoint {
    <#
    .SYNOPSIS
        Creates a system restore point.
    .DESCRIPTION
        Creates a Windows system restore point before making system changes.
    .PARAMETER Description
        Description for the restore point.
    .PARAMETER RestorePointType
        Type of restore point (MODIFY_SETTINGS, APPLICATION_INSTALL, etc.)
    .EXAMPLE
        New-Better11RestorePoint -Description "Before Better11 changes"
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Description,

        [Parameter()]
        [ValidateSet('MODIFY_SETTINGS', 'APPLICATION_INSTALL', 'APPLICATION_UNINSTALL', 'DEVICE_DRIVER_INSTALL')]
        [string]$RestorePointType = 'MODIFY_SETTINGS'
    )

    if (-not (Test-Better11Administrator)) {
        throw "Creating restore points requires administrator privileges"
    }

    if ($PSCmdlet.ShouldProcess("System", "Create restore point: $Description")) {
        try {
            Write-Verbose "Creating restore point: $Description"
            
            # Enable System Restore if disabled
            $srService = Get-Service -Name 'SDRSVC' -ErrorAction SilentlyContinue
            if ($srService -and $srService.Status -ne 'Running') {
                Start-Service -Name 'SDRSVC' -ErrorAction SilentlyContinue
                Start-Sleep -Seconds 2
            }

            Checkpoint-Computer -Description $Description -RestorePointType $RestorePointType -ErrorAction Stop
            
            Write-Verbose "Restore point created successfully"
            
            # Return the latest restore point
            Get-ComputerRestorePoint | Select-Object -First 1
        }
        catch {
            Write-Error "Failed to create restore point: $_"
            throw
        }
    }
}
