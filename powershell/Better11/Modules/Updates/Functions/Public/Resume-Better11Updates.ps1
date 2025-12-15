function Resume-Better11Updates {
    <#
    .SYNOPSIS
        Resumes Windows updates.
    .DESCRIPTION
        Removes the pause on Windows updates and allows them to proceed.
    .EXAMPLE
        Resume-Better11Updates
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param()

    if ($PSCmdlet.ShouldProcess("Windows Updates", "Resume")) {
        try {
            $RegPath = 'HKLM:\SOFTWARE\Microsoft\WindowsUpdate\UX\Settings'
            
            $PropertiesToRemove = @(
                'PauseFeatureUpdatesStartTime',
                'PauseFeatureUpdatesEndTime',
                'PauseQualityUpdatesStartTime',
                'PauseQualityUpdatesEndTime',
                'PauseUpdatesExpiryTime',
                'PauseUpdatesStartTime'
            )
            
            foreach ($Property in $PropertiesToRemove) {
                try {
                    Remove-ItemProperty -Path $RegPath -Name $Property -ErrorAction SilentlyContinue
                } catch { }
            }
            
            Write-Verbose "Updates resumed"
            return [PSCustomObject]@{ Success = $true; Message = "Updates resumed" }
        }
        catch {
            Write-Error "Failed to resume updates: $_"
            return [PSCustomObject]@{ Success = $false; Error = $_.Exception.Message }
        }
    }
}
