function Get-Better11WindowsInfo {
    <#
    .SYNOPSIS
        Gets Windows version information.
    .DESCRIPTION
        Retrieves detailed Windows version and installation information.
    .EXAMPLE
        Get-Better11WindowsInfo
    #>
    [CmdletBinding()]
    param()

    try {
        $OS = Get-CimInstance Win32_OperatingSystem
        
        $Uptime = (Get-Date) - $OS.LastBootUpTime
        
        return [PSCustomObject]@{
            Version = $OS.Version
            Build = $OS.BuildNumber
            Edition = $OS.Caption
            ProductId = $OS.SerialNumber
            InstallDate = $OS.InstallDate
            LastBoot = $OS.LastBootUpTime
            UptimeHours = [math]::Round($Uptime.TotalHours, 2)
            RegisteredOwner = $OS.RegisteredUser
            SystemRoot = $env:SystemRoot
            Architecture = $OS.OSArchitecture
        }
    }
    catch {
        Write-Error "Failed to get Windows info: $_"
        return $null
    }
}
