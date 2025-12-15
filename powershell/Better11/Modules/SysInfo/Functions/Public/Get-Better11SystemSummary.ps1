function Get-Better11SystemSummary {
    <#
    .SYNOPSIS
        Gets a complete system summary.
    .DESCRIPTION
        Gathers comprehensive system information including hardware and software details.
    .EXAMPLE
        Get-Better11SystemSummary
    #>
    [CmdletBinding()]
    param()

    try {
        Write-Verbose "Gathering system information..."
        
        $ComputerSystem = Get-CimInstance Win32_ComputerSystem
        
        return [PSCustomObject]@{
            ComputerName = $env:COMPUTERNAME
            Domain = $ComputerSystem.Domain
            Manufacturer = $ComputerSystem.Manufacturer
            Model = $ComputerSystem.Model
            SystemType = $ComputerSystem.SystemType
            Windows = Get-Better11WindowsInfo
            CPU = Get-Better11CPUInfo
            Memory = Get-Better11MemoryInfo
            GPU = Get-Better11GPUInfo
            Storage = Get-Better11StorageInfo
            Network = Get-Better11NetworkInfo
            BIOS = Get-Better11BIOSInfo
        }
    }
    catch {
        Write-Error "Failed to get system summary: $_"
        return $null
    }
}
