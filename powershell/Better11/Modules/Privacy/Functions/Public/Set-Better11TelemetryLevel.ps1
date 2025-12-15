function Set-Better11TelemetryLevel {
    <#
    .SYNOPSIS
        Sets the Windows telemetry level.
    .DESCRIPTION
        Configures the Windows diagnostic data collection level.
    .PARAMETER Level
        Telemetry level: Security (0), Basic (1), Enhanced (2), Full (3)
    .EXAMPLE
        Set-Better11TelemetryLevel -Level Basic
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet('Security', 'Basic', 'Enhanced', 'Full')]
        [string]$Level
    )

    $LevelValue = switch ($Level) {
        'Security' { 0 }
        'Basic' { 1 }
        'Enhanced' { 2 }
        'Full' { 3 }
    }

    if ($PSCmdlet.ShouldProcess("Telemetry", "Set level to $Level ($LevelValue)")) {
        try {
            $Path = 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection'
            
            if (-not (Test-Path $Path)) {
                New-Item -Path $Path -Force | Out-Null
            }

            Set-ItemProperty -Path $Path -Name 'AllowTelemetry' -Value $LevelValue -Type DWord
            
            Write-Verbose "Telemetry level set to $Level"
            return [PSCustomObject]@{
                Success = $true
                Level = $Level
                Value = $LevelValue
            }
        }
        catch {
            Write-Error "Failed to set telemetry level: $_"
            return [PSCustomObject]@{ Success = $false; Error = $_.Exception.Message }
        }
    }
}
