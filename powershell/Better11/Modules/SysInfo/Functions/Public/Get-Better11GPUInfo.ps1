function Get-Better11GPUInfo {
    <#
    .SYNOPSIS
        Gets GPU information.
    .DESCRIPTION
        Retrieves graphics card specifications.
    .EXAMPLE
        Get-Better11GPUInfo
    #>
    [CmdletBinding()]
    param()

    try {
        $GPUs = Get-CimInstance Win32_VideoController
        
        $Results = foreach ($GPU in $GPUs) {
            [PSCustomObject]@{
                Name = $GPU.Name
                Manufacturer = $GPU.AdapterCompatibility
                DriverVersion = $GPU.DriverVersion
                DriverDate = $GPU.DriverDate
                VideoMemoryMB = [math]::Round($GPU.AdapterRAM / 1MB, 0)
                CurrentResolution = "$($GPU.CurrentHorizontalResolution)x$($GPU.CurrentVerticalResolution)"
                RefreshRate = $GPU.CurrentRefreshRate
                Status = $GPU.Status
            }
        }
        
        return $Results
    }
    catch {
        Write-Error "Failed to get GPU info: $_"
        return @()
    }
}
