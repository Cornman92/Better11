function Suspend-Better11Updates {
    <#
    .SYNOPSIS
        Pauses Windows updates for a specified period.
    
    .DESCRIPTION
        Temporarily pauses Windows Update for up to 35 days. This prevents
        automatic download and installation of updates.
    
    .PARAMETER Days
        Number of days to pause updates (1-35). Default is 7 days.
    
    .PARAMETER Force
        Skip confirmation prompt.
    
    .EXAMPLE
        Suspend-Better11Updates -Days 14
        Pauses Windows updates for 14 days.
    
    .OUTPUTS
        PSCustomObject
        Result of the operation.
    #>
    
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter()]
        [ValidateRange(1, 35)]
        [int]$Days = 7,
        
        [Parameter()]
        [switch]$Force
    )
    
    begin {
        Write-Better11Log -Message "Suspending Windows updates for $Days days" -Level Info
        
        if (-not (Test-Better11Administrator)) {
            throw "Pausing Windows updates requires administrator privileges"
        }
    }
    
    process {
        try {
            # Confirm
            if (-not $Force) {
                $confirmed = Confirm-Better11Action -Prompt "Pause Windows updates for $Days days?"
                if (-not $confirmed) {
                    throw "Operation cancelled by user"
                }
            }
            
            if ($PSCmdlet.ShouldProcess("Windows Update", "Pause for $Days days")) {
                # Calculate expiry date
                $expiryDate = (Get-Date).AddDays($Days).ToString('yyyy-MM-ddTHH:mm:ssZ')
                
                # Set registry key to pause updates
                $registryPath = 'HKLM:\SOFTWARE\Microsoft\WindowsUpdate\UX\Settings'
                
                if (-not (Test-Path $registryPath)) {
                    New-Item -Path $registryPath -Force | Out-Null
                }
                
                Set-ItemProperty -Path $registryPath -Name 'PauseUpdatesExpiryTime' -Value $expiryDate -Type String
                
                Write-Better11Log -Message "Windows updates paused until $expiryDate" -Level Info
                
                return [PSCustomObject]@{
                    Success = $true
                    PausedUntil = $expiryDate
                    DaysPaused = $Days
                }
            }
        }
        catch {
            Write-Better11Log -Message "Failed to pause Windows updates: $_" -Level Error
            throw
        }
    }
}
