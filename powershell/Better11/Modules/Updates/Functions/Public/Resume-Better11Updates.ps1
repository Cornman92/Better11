function Resume-Better11Updates {
    <#
    .SYNOPSIS
        Resumes Windows updates if paused.
    
    .DESCRIPTION
        Removes the Windows Update pause setting, allowing updates to download
        and install automatically again.
    
    .PARAMETER Force
        Skip confirmation prompt.
    
    .EXAMPLE
        Resume-Better11Updates
        Resumes Windows updates.
    
    .OUTPUTS
        PSCustomObject
        Result of the operation.
    #>
    
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter()]
        [switch]$Force
    )
    
    begin {
        Write-Better11Log -Message "Resuming Windows updates" -Level Info
        
        if (-not (Test-Better11Administrator)) {
            throw "Resuming Windows updates requires administrator privileges"
        }
    }
    
    process {
        try {
            # Confirm
            if (-not $Force) {
                $confirmed = Confirm-Better11Action -Prompt "Resume Windows updates?"
                if (-not $confirmed) {
                    throw "Operation cancelled by user"
                }
            }
            
            if ($PSCmdlet.ShouldProcess("Windows Update", "Resume updates")) {
                # Remove pause registry key
                $registryPath = 'HKLM:\SOFTWARE\Microsoft\WindowsUpdate\UX\Settings'
                
                if (Test-Path $registryPath) {
                    Remove-ItemProperty -Path $registryPath -Name 'PauseUpdatesExpiryTime' -ErrorAction SilentlyContinue
                }
                
                Write-Better11Log -Message "Windows updates resumed" -Level Info
                
                return [PSCustomObject]@{
                    Success = $true
                    Status = 'Resumed'
                }
            }
        }
        catch {
            Write-Better11Log -Message "Failed to resume Windows updates: $_" -Level Error
            throw
        }
    }
}
