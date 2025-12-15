function Set-Better11MouseAcceleration {
    <#
    .SYNOPSIS
        Enables or disables mouse acceleration.
    .DESCRIPTION
        Configures mouse acceleration (pointer precision enhancement).
    .PARAMETER Enabled
        Whether to enable mouse acceleration.
    .EXAMPLE
        Set-Better11MouseAcceleration -Enabled $false
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory = $true)]
        [bool]$Enabled
    )

    $Action = if ($Enabled) { "Enable" } else { "Disable" }

    if ($PSCmdlet.ShouldProcess("Mouse Acceleration", $Action)) {
        try {
            $Path = 'HKCU:\Control Panel\Mouse'
            
            if ($Enabled) {
                # Default Windows acceleration
                Set-ItemProperty -Path $Path -Name 'MouseSpeed' -Value '1'
                Set-ItemProperty -Path $Path -Name 'MouseThreshold1' -Value '6'
                Set-ItemProperty -Path $Path -Name 'MouseThreshold2' -Value '10'
            } else {
                # Disable acceleration
                Set-ItemProperty -Path $Path -Name 'MouseSpeed' -Value '0'
                Set-ItemProperty -Path $Path -Name 'MouseThreshold1' -Value '0'
                Set-ItemProperty -Path $Path -Name 'MouseThreshold2' -Value '0'
            }
            
            Write-Verbose "Mouse acceleration set to $Enabled (logout may be required)"
            return [PSCustomObject]@{ Success = $true; MouseAccelerationEnabled = $Enabled }
        }
        catch {
            Write-Error "Failed to set mouse acceleration: $_"
            return [PSCustomObject]@{ Success = $false; Error = $_.Exception.Message }
        }
    }
}
