function Set-Better11GamingPreset {
    <#
    .SYNOPSIS
        Applies a gaming optimization preset.
    .DESCRIPTION
        Applies a predefined set of gaming optimizations.
    .PARAMETER Preset
        The preset to apply: MaximumPerformance, Balanced, Streaming, or Default.
    .EXAMPLE
        Set-Better11GamingPreset -Preset MaximumPerformance
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet('MaximumPerformance', 'Balanced', 'Streaming', 'Default')]
        [string]$Preset
    )

    if ($PSCmdlet.ShouldProcess("Gaming Settings", "Apply $Preset preset")) {
        $Results = @{
            Preset = $Preset
            Changes = @()
            Success = $true
        }

        try {
            switch ($Preset) {
                'MaximumPerformance' {
                    $Results.Changes += Set-Better11GameMode -Enabled $true
                    $Results.Changes += Set-Better11GameBar -Enabled $false
                    $Results.Changes += Set-Better11GPUScheduling -Enabled $true
                    $Results.Changes += Set-Better11MouseAcceleration -Enabled $false
                    $Results.Changes += Disable-Better11NagleAlgorithm
                    $Results.Changes += Set-Better11HighPerformancePower
                }
                'Balanced' {
                    $Results.Changes += Set-Better11GameMode -Enabled $true
                    $Results.Changes += Set-Better11GameBar -Enabled $true
                    $Results.Changes += Set-Better11GPUScheduling -Enabled $true
                    $Results.Changes += Set-Better11MouseAcceleration -Enabled $false
                }
                'Streaming' {
                    $Results.Changes += Set-Better11GameMode -Enabled $true
                    $Results.Changes += Set-Better11GameBar -Enabled $true
                    $Results.Changes += Set-Better11GPUScheduling -Enabled $true
                    $Results.Changes += Set-Better11MouseAcceleration -Enabled $false
                    $Results.Changes += Set-Better11HighPerformancePower
                }
                'Default' {
                    $Results.Changes += Set-Better11GameMode -Enabled $true
                    $Results.Changes += Set-Better11GameBar -Enabled $true
                    $Results.Changes += Set-Better11GPUScheduling -Enabled $false
                    $Results.Changes += Set-Better11MouseAcceleration -Enabled $true
                    $Results.Changes += Enable-Better11NagleAlgorithm
                }
            }

            Write-Verbose "$Preset gaming preset applied"
            return [PSCustomObject]$Results
        }
        catch {
            Write-Error "Failed to apply gaming preset: $_"
            $Results.Success = $false
            $Results.Error = $_.Exception.Message
            return [PSCustomObject]$Results
        }
    }
}
