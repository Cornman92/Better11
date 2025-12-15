function Get-Better11DriverIssues {
    <#
    .SYNOPSIS
        Gets drivers with issues.
    .DESCRIPTION
        Lists devices that have driver problems.
    .EXAMPLE
        Get-Better11DriverIssues
    #>
    [CmdletBinding()]
    param()

    try {
        # Error code 0 = working properly
        $ProblemDevices = Get-CimInstance Win32_PnPEntity | 
            Where-Object { $_.ConfigManagerErrorCode -ne 0 }
        
        $ErrorCodeMap = @{
            1 = 'Device not configured correctly'
            3 = 'Driver corrupted or missing'
            10 = 'Device cannot start'
            12 = 'Cannot find free resources'
            14 = 'Restart required'
            18 = 'Reinstall drivers'
            22 = 'Device disabled'
            24 = 'Device not present'
            28 = 'Drivers not installed'
            31 = 'Device not working properly'
            43 = 'Windows stopped device'
        }
        
        $Results = foreach ($Device in $ProblemDevices) {
            [PSCustomObject]@{
                DeviceName = $Device.Name
                Status = $Device.Status
                ErrorCode = $Device.ConfigManagerErrorCode
                ErrorDescription = $ErrorCodeMap[$Device.ConfigManagerErrorCode]
                DeviceID = $Device.DeviceID
                Class = $Device.PNPClass
            }
        }
        
        return $Results
    }
    catch {
        Write-Error "Failed to get driver issues: $_"
        return @()
    }
}
