function Export-Better11DriverList {
    <#
    .SYNOPSIS
        Exports driver list to file.
    .DESCRIPTION
        Saves the list of installed drivers to a JSON or CSV file.
    .PARAMETER Path
        The output file path.
    .PARAMETER Format
        Output format (JSON or CSV).
    .EXAMPLE
        Export-Better11DriverList -Path "drivers.json"
    #>
    [CmdletBinding()]
    param(
        [Parameter()]
        [string]$Path,
        
        [Parameter()]
        [ValidateSet('JSON', 'CSV')]
        [string]$Format = 'JSON'
    )

    try {
        if (-not $Path) {
            $Extension = $Format.ToLower()
            $Path = Join-Path $env:USERPROFILE "Better11-Drivers-$(Get-Date -Format 'yyyyMMdd').$Extension"
        }
        
        $Drivers = Get-Better11Drivers
        
        if ($Format -eq 'JSON') {
            $Drivers | ConvertTo-Json -Depth 5 | Out-File -FilePath $Path -Encoding utf8
        }
        else {
            $Drivers | Export-Csv -Path $Path -NoTypeInformation -Encoding utf8
        }
        
        return [PSCustomObject]@{
            Success = $true
            Path = $Path
            DriverCount = $Drivers.Count
        }
    }
    catch {
        Write-Error "Failed to export driver list: $_"
        return [PSCustomObject]@{ Success = $false; Error = $_.Exception.Message }
    }
}
