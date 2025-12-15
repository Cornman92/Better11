function Get-Better11PerformanceMetrics {
    <#
    .SYNOPSIS
        Gets current system performance metrics.
    
    .DESCRIPTION
        Collects real-time performance data including CPU, memory, disk, and network usage.
    
    .PARAMETER SampleInterval
        Interval in seconds between samples for average calculation.
    
    .EXAMPLE
        Get-Better11PerformanceMetrics -SampleInterval 2
    #>
    [CmdletBinding()]
    param(
        [Parameter()]
        [int]$SampleInterval = 1
    )
    
    try {
        # CPU Usage
        $CPUUsage = (Get-Counter '\Processor(_Total)\% Processor Time' -SampleInterval $SampleInterval).CounterSamples.CookedValue
        
        # Memory Usage
        $OS = Get-CimInstance -ClassName Win32_OperatingSystem
        $TotalMemory = $OS.TotalVisibleMemorySize
        $FreeMemory = $OS.FreePhysicalMemory
        $UsedMemory = $TotalMemory - $FreeMemory
        $MemoryUsagePercent = [math]::Round(($UsedMemory / $TotalMemory) * 100, 2)
        
        # Disk Usage (C: drive)
        $DiskUsage = (Get-Counter '\LogicalDisk(C:)\% Disk Time' -SampleInterval $SampleInterval).CounterSamples.CookedValue
        
        # Process Count
        $ProcessCount = (Get-Process).Count
        
        # Top 5 CPU processes
        $TopCPU = Get-Process | Sort-Object CPU -Descending | Select-Object -First 5 -Property Name, CPU, WorkingSet
        
        # Top 5 Memory processes
        $TopMemory = Get-Process | Sort-Object WorkingSet -Descending | Select-Object -First 5 -Property Name, WorkingSet, CPU
        
        $Metrics = [PSCustomObject]@{
            Timestamp = Get-Date
            CPUUsagePercent = [math]::Round($CPUUsage, 2)
            MemoryUsagePercent = $MemoryUsagePercent
            MemoryUsedMB = [math]::Round($UsedMemory / 1024, 2)
            MemoryFreeMB = [math]::Round($FreeMemory / 1024, 2)
            DiskUsagePercent = [math]::Round($DiskUsage, 2)
            ProcessCount = $ProcessCount
            TopCPUProcesses = $TopCPU
            TopMemoryProcesses = $TopMemory
        }
        
        return $Metrics
    }
    catch {
        Write-Better11Log -Message "Failed to get performance metrics: $_" -Level Error
        throw
    }
}
