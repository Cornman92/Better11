function Get-Better11DiskSpace {
    <#
    .SYNOPSIS
        Gets disk space information for all drives.
    
    .DESCRIPTION
        Retrieves detailed disk space information including total, used, and free
        space for all available drives. Returns information as custom objects.
    
    .PARAMETER DriveLetter
        Optional drive letter to query. If not specified, queries all drives.
    
    .EXAMPLE
        Get-Better11DiskSpace
        
        Gets disk space for all drives.
    
    .EXAMPLE
        Get-Better11DiskSpace -DriveLetter C
        
        Gets disk space for C: drive only.
    
    .OUTPUTS
        PSCustomObject[]
        Array of disk space information objects
    #>
    
    [CmdletBinding()]
    [OutputType([PSCustomObject[]])]
    param(
        [Parameter()]
        [ValidatePattern('^[A-Z]$')]
        [string]$DriveLetter
    )
    
    begin {
        Write-Better11Log -Message "Analyzing disk space" -Level Info -Component "Disk"
    }
    
    process {
        try {
            # Get all logical disks or specific drive
            $filter = if ($DriveLetter) {
                "DeviceID='${DriveLetter}:'"
            } else {
                "DriveType=3"  # Local disks only
            }
            
            $disks = Get-CimInstance -ClassName Win32_LogicalDisk -Filter $filter
            
            $results = foreach ($disk in $disks) {
                $totalGB = [math]::Round($disk.Size / 1GB, 2)
                $freeGB = [math]::Round($disk.FreeSpace / 1GB, 2)
                $usedGB = [math]::Round(($disk.Size - $disk.FreeSpace) / 1GB, 2)
                $usagePercent = if ($disk.Size -gt 0) {
                    [math]::Round((($disk.Size - $disk.FreeSpace) / $disk.Size) * 100, 1)
                } else {
                    0
                }
                
                [PSCustomObject]@{
                    DriveLetter = $disk.DeviceID.TrimEnd(':')
                    Label = $disk.VolumeName
                    FileSystem = $disk.FileSystem
                    TotalGB = $totalGB
                    UsedGB = $usedGB
                    FreeGB = $freeGB
                    UsagePercent = $usagePercent
                    DriveType = switch ($disk.DriveType) {
                        2 { "Removable" }
                        3 { "Local Disk" }
                        4 { "Network" }
                        5 { "CD-ROM" }
                        default { "Unknown" }
                    }
                }
            }
            
            Write-Better11Log -Message "Found $($results.Count) disk(s)" -Level Info -Component "Disk"
            
            return $results
        }
        catch {
            Write-Better11Log -Message "Failed to get disk space: $_" -Level Error -Component "Disk"
            throw
        }
    }
}
