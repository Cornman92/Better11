function Get-Better11RestorePoints {
    <#
    .SYNOPSIS
        Gets system restore points.
    .DESCRIPTION
        Retrieves all available system restore points.
    .PARAMETER Count
        Maximum number of restore points to return.
    .EXAMPLE
        Get-Better11RestorePoints -Count 10
    #>
    [CmdletBinding()]
    param(
        [Parameter()]
        [int]$Count = 20
    )

    try {
        $RestorePoints = Get-ComputerRestorePoint -ErrorAction SilentlyContinue | 
            Select-Object -First $Count |
            ForEach-Object {
                [PSCustomObject]@{
                    SequenceNumber = $_.SequenceNumber
                    Description = $_.Description
                    CreationTime = $_.ConvertToDateTime($_.CreationTime)
                    RestorePointType = switch ($_.RestorePointType) {
                        0 { 'APPLICATION_INSTALL' }
                        1 { 'APPLICATION_UNINSTALL' }
                        10 { 'DEVICE_DRIVER_INSTALL' }
                        12 { 'MODIFY_SETTINGS' }
                        13 { 'CANCELLED_OPERATION' }
                        default { 'UNKNOWN' }
                    }
                    EventType = $_.EventType
                }
            }

        return $RestorePoints
    }
    catch {
        Write-Warning "Failed to get restore points: $_"
        return @()
    }
}
