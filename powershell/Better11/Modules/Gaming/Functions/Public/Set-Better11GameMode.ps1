function Set-Better11GameMode {
    <#
    .SYNOPSIS
        Enables or disables Game Mode.
    .DESCRIPTION
        Configures Windows Game Mode for gaming optimization.
    .PARAMETER Enabled
        Whether to enable Game Mode.
    .EXAMPLE
        Set-Better11GameMode -Enabled $true
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory = $true)]
        [bool]$Enabled
    )

    $Action = if ($Enabled) { "Enable" } else { "Disable" }

    if ($PSCmdlet.ShouldProcess("Game Mode", $Action)) {
        try {
            $Path = 'HKCU:\SOFTWARE\Microsoft\GameBar'
            
            if (-not (Test-Path $Path)) {
                New-Item -Path $Path -Force | Out-Null
            }
            
            Set-ItemProperty -Path $Path -Name 'AutoGameModeEnabled' -Value $(if ($Enabled) { 1 } else { 0 }) -Type DWord
            
            Write-Verbose "Game Mode set to $Enabled"
            return [PSCustomObject]@{ Success = $true; GameModeEnabled = $Enabled }
        }
        catch {
            Write-Error "Failed to set Game Mode: $_"
            return [PSCustomObject]@{ Success = $false; Error = $_.Exception.Message }
        }
    }
}
