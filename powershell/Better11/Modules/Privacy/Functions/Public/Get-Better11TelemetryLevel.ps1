function Get-Better11TelemetryLevel {
    <#
    .SYNOPSIS
        Gets the current Windows telemetry level.
    .DESCRIPTION
        Retrieves the current telemetry data collection level setting.
    .OUTPUTS
        PSCustomObject with Level (0-3) and LevelName (Security/Basic/Enhanced/Full)
    .EXAMPLE
        Get-Better11TelemetryLevel
    #>
    [CmdletBinding()]
    param()

    try {
        $Path = 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection'
        $Value = Get-ItemProperty -Path $Path -Name 'AllowTelemetry' -ErrorAction SilentlyContinue

        $Level = if ($Value) { $Value.AllowTelemetry } else { 3 }

        $LevelName = switch ($Level) {
            0 { 'Security' }
            1 { 'Basic' }
            2 { 'Enhanced' }
            3 { 'Full' }
            default { 'Unknown' }
        }

        return [PSCustomObject]@{
            Level = $Level
            LevelName = $LevelName
            Description = switch ($Level) {
                0 { 'Security data only (Enterprise only)' }
                1 { 'Basic diagnostic data' }
                2 { 'Enhanced diagnostic data' }
                3 { 'Full diagnostic data' }
                default { 'Unknown level' }
            }
        }
    }
    catch {
        Write-Error "Failed to get telemetry level: $_"
        return [PSCustomObject]@{ Level = 3; LevelName = 'Full'; Error = $_.Exception.Message }
    }
}
