function Get-Better11Drivers {
    <#
    .SYNOPSIS
        Gets installed drivers.
    .DESCRIPTION
        Lists all installed hardware drivers.
    .PARAMETER Category
        Filter by driver category.
    .EXAMPLE
        Get-Better11Drivers
        Get-Better11Drivers -Category "Display"
    #>
    [CmdletBinding()]
    param(
        [Parameter()]
        [string]$Category
    )

    try {
        $Drivers = Get-CimInstance Win32_PnPSignedDriver | 
            Where-Object { $_.DeviceName -ne $null }
        
        if ($Category) {
            $Drivers = $Drivers | Where-Object { $_.DeviceClass -like "*$Category*" }
        }
        
        $Results = foreach ($Driver in $Drivers) {
            [PSCustomObject]@{
                DeviceName = $Driver.DeviceName
                DriverVersion = $Driver.DriverVersion
                DriverDate = $Driver.DriverDate
                Manufacturer = $Driver.Manufacturer
                DeviceClass = $Driver.DeviceClass
                DeviceID = $Driver.DeviceID
                IsSigned = $Driver.IsSigned
                InfName = $Driver.InfName
            }
        }
        
        return $Results
    }
    catch {
        Write-Error "Failed to get drivers: $_"
        return @()
    }
}
