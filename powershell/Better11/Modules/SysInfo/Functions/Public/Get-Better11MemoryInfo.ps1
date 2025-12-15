function Get-Better11MemoryInfo {
    <#
    .SYNOPSIS
        Gets memory information.
    .DESCRIPTION
        Retrieves RAM specifications and current usage.
    .EXAMPLE
        Get-Better11MemoryInfo
    #>
    [CmdletBinding()]
    param()

    try {
        $OS = Get-CimInstance Win32_OperatingSystem
        $Memory = Get-CimInstance Win32_PhysicalMemory
        $MemArray = Get-CimInstance Win32_PhysicalMemoryArray
        
        $TotalBytes = $OS.TotalVisibleMemorySize * 1024
        $FreeBytes = $OS.FreePhysicalMemory * 1024
        $UsedBytes = $TotalBytes - $FreeBytes
        $UsagePercent = if ($TotalBytes -gt 0) { [math]::Round(($UsedBytes / $TotalBytes) * 100, 1) } else { 0 }
        
        $TypeMap = @{
            24 = 'DDR3'
            26 = 'DDR4'
            30 = 'DDR5'
        }
        
        return [PSCustomObject]@{
            TotalGB = [math]::Round($TotalBytes / 1GB, 2)
            AvailableGB = [math]::Round($FreeBytes / 1GB, 2)
            UsedGB = [math]::Round($UsedBytes / 1GB, 2)
            UsagePercent = $UsagePercent
            SlotsUsed = ($Memory | Measure-Object).Count
            SlotsTotal = $MemArray.MemoryDevices
            SpeedMHz = ($Memory | Select-Object -First 1).Speed
            Type = $TypeMap[($Memory | Select-Object -First 1).MemoryType]
        }
    }
    catch {
        Write-Error "Failed to get memory info: $_"
        return $null
    }
}
