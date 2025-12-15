function Get-Better11ResourceUsage {
    <#
    .SYNOPSIS
        Gets current resource usage.
    .DESCRIPTION
        Shows current CPU, memory, and disk usage.
    .EXAMPLE
        Get-Better11ResourceUsage
    #>
    [CmdletBinding()]
    param()

    try {
        $CPU = Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average
        $OS = Get-CimInstance Win32_OperatingSystem
        $Disks = Get-CimInstance Win32_LogicalDisk -Filter "DriveType=3"
        
        $MemUsed = $OS.TotalVisibleMemorySize - $OS.FreePhysicalMemory
        $MemPercent = [math]::Round(($MemUsed / $OS.TotalVisibleMemorySize) * 100, 1)
        
        $DiskUsage = foreach ($Disk in $Disks) {
            $UsedSpace = $Disk.Size - $Disk.FreeSpace
            $UsedPercent = if ($Disk.Size -gt 0) { [math]::Round(($UsedSpace / $Disk.Size) * 100, 1) } else { 0 }
            
            [PSCustomObject]@{
                Drive = $Disk.DeviceID
                TotalGB = [math]::Round($Disk.Size / 1GB, 2)
                FreeGB = [math]::Round($Disk.FreeSpace / 1GB, 2)
                UsedPercent = $UsedPercent
            }
        }
        
        return [PSCustomObject]@{
            CPUUsagePercent = [math]::Round($CPU.Average, 1)
            MemoryUsedGB = [math]::Round(($MemUsed * 1024) / 1GB, 2)
            MemoryTotalGB = [math]::Round(($OS.TotalVisibleMemorySize * 1024) / 1GB, 2)
            MemoryUsedPercent = $MemPercent
            Disks = $DiskUsage
            Timestamp = Get-Date
        }
    }
    catch {
        Write-Error "Failed to get resource usage: $_"
        return $null
    }
}
