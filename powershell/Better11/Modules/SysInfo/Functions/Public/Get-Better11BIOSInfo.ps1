function Get-Better11BIOSInfo {
    <#
    .SYNOPSIS
        Gets BIOS/UEFI information.
    .DESCRIPTION
        Retrieves BIOS or UEFI firmware details.
    .EXAMPLE
        Get-Better11BIOSInfo
    #>
    [CmdletBinding()]
    param()

    try {
        $BIOS = Get-CimInstance Win32_BIOS
        
        $IsUEFI = Test-Path "HKLM:\System\CurrentControlSet\Control\SecureBoot\State"
        
        return [PSCustomObject]@{
            Manufacturer = $BIOS.Manufacturer
            Version = $BIOS.SMBIOSBIOSVersion
            ReleaseDate = $BIOS.ReleaseDate
            SerialNumber = $BIOS.SerialNumber
            IsUEFI = $IsUEFI
            SMBIOSVersion = "$($BIOS.SMBIOSMajorVersion).$($BIOS.SMBIOSMinorVersion)"
        }
    }
    catch {
        Write-Error "Failed to get BIOS info: $_"
        return $null
    }
}
