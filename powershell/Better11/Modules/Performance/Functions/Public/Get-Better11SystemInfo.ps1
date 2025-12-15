function Get-Better11SystemInfo {
    <#
    .SYNOPSIS
        Gets comprehensive system information.
    
    .DESCRIPTION
        Collects detailed information about the system including hardware, OS, and performance.
    
    .EXAMPLE
        Get-Better11SystemInfo
    #>
    [CmdletBinding()]
    param()
    
    try {
        $OS = Get-CimInstance -ClassName Win32_OperatingSystem
        $CS = Get-CimInstance -ClassName Win32_ComputerSystem
        $CPU = Get-CimInstance -ClassName Win32_Processor
        $Disk = Get-CimInstance -ClassName Win32_LogicalDisk -Filter "DeviceID='C:'"
        
        $SystemInfo = [PSCustomObject]@{
            ComputerName = $CS.Name
            Manufacturer = $CS.Manufacturer
            Model = $CS.Model
            OSName = $OS.Caption
            OSVersion = $OS.Version
            OSBuild = $OS.BuildNumber
            Architecture = $OS.OSArchitecture
            InstallDate = $OS.InstallDate
            LastBootTime = $OS.LastBootUpTime
            Uptime = (Get-Date) - $OS.LastBootUpTime
            TotalMemoryGB = [math]::Round($CS.TotalPhysicalMemory / 1GB, 2)
            FreeMemoryGB = [math]::Round($OS.FreePhysicalMemory / 1MB / 1024, 2)
            CPUName = $CPU.Name
            CPUCores = $CPU.NumberOfCores
            CPULogicalProcessors = $CPU.NumberOfLogicalProcessors
            DiskTotalGB = [math]::Round($Disk.Size / 1GB, 2)
            DiskFreeGB = [math]::Round($Disk.FreeSpace / 1GB, 2)
            DiskUsedPercent = [math]::Round((($Disk.Size - $Disk.FreeSpace) / $Disk.Size) * 100, 2)
        }
        
        return $SystemInfo
    }
    catch {
        Write-Better11Log -Message "Failed to get system info: $_" -Level Error
        throw
    }
}
