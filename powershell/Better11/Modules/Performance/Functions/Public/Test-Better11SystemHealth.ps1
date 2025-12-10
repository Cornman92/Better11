function Test-Better11SystemHealth {
    <#
    .SYNOPSIS
        Performs a comprehensive system health check.
    
    .DESCRIPTION
        Checks various system health indicators and provides recommendations.
    
    .EXAMPLE
        Test-Better11SystemHealth
    #>
    [CmdletBinding()]
    param()
    
    try {
        Write-Better11Log -Message "Running system health check..." -Level Info
        
        $HealthReport = @{
            Timestamp = Get-Date
            OverallStatus = 'Healthy'
            Checks = @()
            Warnings = @()
            Recommendations = @()
        }
        
        # Check disk space
        $Disk = Get-CimInstance -ClassName Win32_LogicalDisk -Filter "DeviceID='C:'"
        $DiskFreePercent = ($Disk.FreeSpace / $Disk.Size) * 100
        
        $DiskCheck = [PSCustomObject]@{
            Name = 'Disk Space'
            Status = if ($DiskFreePercent -gt 20) { 'OK' } elseif ($DiskFreePercent -gt 10) { 'Warning' } else { 'Critical' }
            Value = "$([math]::Round($DiskFreePercent, 2))% free"
        }
        $HealthReport.Checks += $DiskCheck
        
        if ($DiskCheck.Status -ne 'OK') {
            $HealthReport.Warnings += "Low disk space on C: drive"
            $HealthReport.Recommendations += "Run disk cleanup or remove unnecessary files"
        }
        
        # Check memory usage
        $OS = Get-CimInstance -ClassName Win32_OperatingSystem
        $MemoryUsagePercent = (($OS.TotalVisibleMemorySize - $OS.FreePhysicalMemory) / $OS.TotalVisibleMemorySize) * 100
        
        $MemoryCheck = [PSCustomObject]@{
            Name = 'Memory Usage'
            Status = if ($MemoryUsagePercent -lt 80) { 'OK' } elseif ($MemoryUsagePercent -lt 90) { 'Warning' } else { 'Critical' }
            Value = "$([math]::Round($MemoryUsagePercent, 2))% used"
        }
        $HealthReport.Checks += $MemoryCheck
        
        if ($MemoryCheck.Status -ne 'OK') {
            $HealthReport.Warnings += "High memory usage"
            $HealthReport.Recommendations += "Close unnecessary applications or upgrade RAM"
        }
        
        # Check Windows Update status
        try {
            $UpdateSession = New-Object -ComObject Microsoft.Update.Session
            $UpdateSearcher = $UpdateSession.CreateUpdateSearcher()
            $PendingUpdates = $UpdateSearcher.Search("IsInstalled=0").Updates.Count
            
            $UpdateCheck = [PSCustomObject]@{
                Name = 'Windows Updates'
                Status = if ($PendingUpdates -eq 0) { 'OK' } else { 'Warning' }
                Value = "$PendingUpdates pending updates"
            }
            $HealthReport.Checks += $UpdateCheck
            
            if ($PendingUpdates -gt 0) {
                $HealthReport.Recommendations += "Install pending Windows updates"
            }
        }
        catch {
            Write-Better11Log -Message "Could not check Windows Update status: $_" -Level Warning
        }
        
        # Check system uptime
        $Uptime = (Get-Date) - $OS.LastBootUpTime
        $UptimeCheck = [PSCustomObject]@{
            Name = 'System Uptime'
            Status = if ($Uptime.TotalDays -lt 30) { 'OK' } else { 'Warning' }
            Value = "$([math]::Round($Uptime.TotalDays, 1)) days"
        }
        $HealthReport.Checks += $UptimeCheck
        
        if ($Uptime.TotalDays -gt 30) {
            $HealthReport.Recommendations += "Consider restarting your computer to apply updates and clear memory"
        }
        
        # Determine overall status
        if ($HealthReport.Checks | Where-Object { $_.Status -eq 'Critical' }) {
            $HealthReport.OverallStatus = 'Critical'
        }
        elseif ($HealthReport.Checks | Where-Object { $_.Status -eq 'Warning' }) {
            $HealthReport.OverallStatus = 'Warning'
        }
        
        Write-Better11Log -Message "System health check completed. Status: $($HealthReport.OverallStatus)" -Level Info
        
        return [PSCustomObject]$HealthReport
    }
    catch {
        Write-Better11Log -Message "System health check failed: $_" -Level Error
        throw
    }
}
