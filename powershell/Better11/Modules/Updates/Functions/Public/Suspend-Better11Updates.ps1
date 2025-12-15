function Suspend-Better11Updates {
    <#
    .SYNOPSIS
        Pauses Windows updates.
    .DESCRIPTION
        Pauses Windows updates for the specified number of days (max 35).
    .PARAMETER Days
        Number of days to pause updates (1-35).
    .EXAMPLE
        Suspend-Better11Updates -Days 7
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateRange(1, 35)]
        [int]$Days
    )

    if ($PSCmdlet.ShouldProcess("Windows Updates", "Pause for $Days days")) {
        try {
            $PauseUntil = (Get-Date).AddDays($Days)
            $PauseUntilStr = $PauseUntil.ToString("yyyy-MM-ddTHH:mm:ssZ")
            $CurrentTime = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssZ")
            
            $RegPath = 'HKLM:\SOFTWARE\Microsoft\WindowsUpdate\UX\Settings'
            
            if (-not (Test-Path $RegPath)) {
                New-Item -Path $RegPath -Force | Out-Null
            }
            
            # Pause feature updates
            Set-ItemProperty -Path $RegPath -Name 'PauseFeatureUpdatesStartTime' -Value $CurrentTime
            Set-ItemProperty -Path $RegPath -Name 'PauseFeatureUpdatesEndTime' -Value $PauseUntilStr
            
            # Pause quality updates
            Set-ItemProperty -Path $RegPath -Name 'PauseQualityUpdatesStartTime' -Value $CurrentTime
            Set-ItemProperty -Path $RegPath -Name 'PauseQualityUpdatesEndTime' -Value $PauseUntilStr
            
            # Set general pause
            Set-ItemProperty -Path $RegPath -Name 'PauseUpdatesExpiryTime' -Value $PauseUntilStr
            Set-ItemProperty -Path $RegPath -Name 'PauseUpdatesStartTime' -Value $CurrentTime
            
            Write-Verbose "Updates paused until $PauseUntil"
            return [PSCustomObject]@{
                Success = $true
                PausedUntil = $PauseUntil
                Days = $Days
            }
        }
        catch {
            Write-Error "Failed to pause updates: $_"
            return [PSCustomObject]@{ Success = $false; Error = $_.Exception.Message }
        }
    }
}
