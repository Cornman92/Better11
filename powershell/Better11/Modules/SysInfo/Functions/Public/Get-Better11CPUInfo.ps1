function Get-Better11CPUInfo {
    <#
    .SYNOPSIS
        Gets CPU information.
    .DESCRIPTION
        Retrieves detailed CPU specifications and current usage.
    .EXAMPLE
        Get-Better11CPUInfo
    #>
    [CmdletBinding()]
    param()

    try {
        $CPU = Get-CimInstance Win32_Processor
        
        return [PSCustomObject]@{
            Name = $CPU.Name.Trim()
            Manufacturer = $CPU.Manufacturer
            Cores = $CPU.NumberOfCores
            LogicalProcessors = $CPU.NumberOfLogicalProcessors
            MaxClockMHz = $CPU.MaxClockSpeed
            Architecture = switch ($CPU.Architecture) {
                0 { 'x86' }
                9 { 'x64' }
                12 { 'ARM64' }
                default { 'Unknown' }
            }
            CurrentUsage = $CPU.LoadPercentage
            L2CacheKB = $CPU.L2CacheSize
            L3CacheKB = $CPU.L3CacheSize
        }
    }
    catch {
        Write-Error "Failed to get CPU info: $_"
        return $null
    }
}
