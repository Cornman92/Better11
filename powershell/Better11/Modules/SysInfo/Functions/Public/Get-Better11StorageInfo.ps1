function Get-Better11StorageInfo {
    <#
    .SYNOPSIS
        Gets storage device information.
    .DESCRIPTION
        Retrieves disk drive specifications.
    .EXAMPLE
        Get-Better11StorageInfo
    #>
    [CmdletBinding()]
    param()

    try {
        $Disks = Get-CimInstance Win32_DiskDrive
        
        $Results = foreach ($Disk in $Disks) {
            $MediaType = $Disk.MediaType
            $Model = $Disk.Model.ToLower()
            
            if ($Model -match 'nvme') { $MediaType = 'NVMe' }
            elseif ($Model -match 'ssd' -or $MediaType -eq 'Solid state drive') { $MediaType = 'SSD' }
            elseif ($MediaType -match 'Fixed hard disk') { $MediaType = 'HDD' }
            
            [PSCustomObject]@{
                Name = $Disk.DeviceID
                Model = $Disk.Model
                MediaType = $MediaType
                SizeGB = [math]::Round($Disk.Size / 1GB, 2)
                InterfaceType = $Disk.InterfaceType
                Status = $Disk.Status
                Partitions = $Disk.Partitions
                SerialNumber = $Disk.SerialNumber
            }
        }
        
        return $Results
    }
    catch {
        Write-Error "Failed to get storage info: $_"
        return @()
    }
}
