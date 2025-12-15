function Set-Better11SystemResponsiveness {
    <#
    .SYNOPSIS
        Sets system responsiveness for multimedia.
    .DESCRIPTION
        Configures how much CPU is reserved for multimedia/audio.
    .PARAMETER ReservedPercent
        Percentage of CPU to reserve (0-100). Lower = more for apps.
    .EXAMPLE
        Set-Better11SystemResponsiveness -ReservedPercent 10
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateRange(0, 100)]
        [int]$ReservedPercent
    )

    try {
        if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
            throw "Administrator privileges required"
        }
        
        $RegPath = 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile'
        
        Set-ItemProperty -Path $RegPath -Name 'SystemResponsiveness' -Value $ReservedPercent -Type DWord
        
        return [PSCustomObject]@{
            Success = $true
            SystemResponsiveness = $ReservedPercent
            Message = "Reserved $ReservedPercent% CPU for system tasks"
        }
    }
    catch {
        Write-Error "Failed to set system responsiveness: $_"
        return [PSCustomObject]@{ Success = $false; Error = $_.Exception.Message }
    }
}
