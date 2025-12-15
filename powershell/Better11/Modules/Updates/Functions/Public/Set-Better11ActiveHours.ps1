function Set-Better11ActiveHours {
    <#
    .SYNOPSIS
        Sets Windows Update active hours.
    .DESCRIPTION
        Configures the active hours during which Windows will not restart for updates.
    .PARAMETER StartHour
        Start hour (0-23).
    .PARAMETER EndHour
        End hour (0-23).
    .EXAMPLE
        Set-Better11ActiveHours -StartHour 8 -EndHour 17
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateRange(0, 23)]
        [int]$StartHour,

        [Parameter(Mandatory = $true)]
        [ValidateRange(0, 23)]
        [int]$EndHour
    )

    # Validate span
    $Span = if ($EndHour -gt $StartHour) { $EndHour - $StartHour } else { (24 - $StartHour) + $EndHour }
    if ($Span -gt 18) {
        throw "Active hours span cannot exceed 18 hours (currently $Span hours)"
    }

    if ($PSCmdlet.ShouldProcess("Active Hours", "Set to $StartHour`:00 - $EndHour`:00")) {
        try {
            $RegPath = 'HKLM:\SOFTWARE\Microsoft\WindowsUpdate\UX\Settings'
            
            if (-not (Test-Path $RegPath)) {
                New-Item -Path $RegPath -Force | Out-Null
            }
            
            Set-ItemProperty -Path $RegPath -Name 'ActiveHoursStart' -Value $StartHour -Type DWord
            Set-ItemProperty -Path $RegPath -Name 'ActiveHoursEnd' -Value $EndHour -Type DWord
            Set-ItemProperty -Path $RegPath -Name 'IsActiveHoursEnabled' -Value 1 -Type DWord
            
            Write-Verbose "Active hours set to $StartHour`:00 - $EndHour`:00"
            return [PSCustomObject]@{
                Success = $true
                StartHour = $StartHour
                EndHour = $EndHour
                Span = $Span
            }
        }
        catch {
            Write-Error "Failed to set active hours: $_"
            return [PSCustomObject]@{ Success = $false; Error = $_.Exception.Message }
        }
    }
}
