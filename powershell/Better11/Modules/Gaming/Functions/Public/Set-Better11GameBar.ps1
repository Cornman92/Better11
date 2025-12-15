function Set-Better11GameBar {
    <#
    .SYNOPSIS
        Enables or disables Xbox Game Bar.
    .DESCRIPTION
        Configures the Xbox Game Bar overlay.
    .PARAMETER Enabled
        Whether to enable Game Bar.
    .EXAMPLE
        Set-Better11GameBar -Enabled $false
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory = $true)]
        [bool]$Enabled
    )

    $Action = if ($Enabled) { "Enable" } else { "Disable" }

    if ($PSCmdlet.ShouldProcess("Xbox Game Bar", $Action)) {
        try {
            $GameDVRPath = 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR'
            $GameBarPath = 'HKCU:\SOFTWARE\Microsoft\GameBar'
            
            foreach ($Path in @($GameDVRPath, $GameBarPath)) {
                if (-not (Test-Path $Path)) {
                    New-Item -Path $Path -Force | Out-Null
                }
            }
            
            Set-ItemProperty -Path $GameDVRPath -Name 'AppCaptureEnabled' -Value $(if ($Enabled) { 1 } else { 0 }) -Type DWord
            Set-ItemProperty -Path $GameBarPath -Name 'UseNexusForGameBarEnabled' -Value $(if ($Enabled) { 1 } else { 0 }) -Type DWord
            
            Write-Verbose "Game Bar set to $Enabled"
            return [PSCustomObject]@{ Success = $true; GameBarEnabled = $Enabled }
        }
        catch {
            Write-Error "Failed to set Game Bar: $_"
            return [PSCustomObject]@{ Success = $false; Error = $_.Exception.Message }
        }
    }
}
