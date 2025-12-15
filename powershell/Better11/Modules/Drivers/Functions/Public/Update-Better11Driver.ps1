function Update-Better11Driver {
    <#
    .SYNOPSIS
        Updates a device driver.
    .DESCRIPTION
        Uses Windows Update or an INF file to update a driver.
    .PARAMETER DeviceID
        The device instance ID.
    .PARAMETER InfPath
        Optional path to an INF file.
    .EXAMPLE
        Update-Better11Driver -DeviceID "PCI\VEN_8086..."
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$DeviceID,
        
        [Parameter()]
        [string]$InfPath
    )

    try {
        if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
            throw "Administrator privileges required"
        }
        
        if ($InfPath) {
            if (-not (Test-Path $InfPath)) {
                throw "INF file not found: $InfPath"
            }
            
            # Use pnputil to add and install driver
            $Result = & pnputil /add-driver "$InfPath" /install 2>&1
            
            return [PSCustomObject]@{
                Success = $LASTEXITCODE -eq 0
                DeviceID = $DeviceID
                Method = 'INF'
                Message = $Result
            }
        }
        else {
            # Use pnputil to scan for updates
            $Result = & pnputil /scan-devices 2>&1
            
            return [PSCustomObject]@{
                Success = $LASTEXITCODE -eq 0
                DeviceID = $DeviceID
                Method = 'WindowsUpdate'
                Message = "Scan completed. Check Device Manager for updates."
            }
        }
    }
    catch {
        Write-Error "Failed to update driver: $_"
        return [PSCustomObject]@{ Success = $false; DeviceID = $DeviceID; Error = $_.Exception.Message }
    }
}
