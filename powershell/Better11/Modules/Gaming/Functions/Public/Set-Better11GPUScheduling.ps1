function Set-Better11GPUScheduling {
    <#
    .SYNOPSIS
        Enables or disables hardware-accelerated GPU scheduling.
    .DESCRIPTION
        Configures hardware-accelerated GPU scheduling (requires restart).
    .PARAMETER Enabled
        Whether to enable GPU scheduling.
    .EXAMPLE
        Set-Better11GPUScheduling -Enabled $true
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory = $true)]
        [bool]$Enabled
    )

    $Action = if ($Enabled) { "Enable" } else { "Disable" }

    if ($PSCmdlet.ShouldProcess("GPU Scheduling", $Action)) {
        try {
            $Path = 'HKLM:\SYSTEM\CurrentControlSet\Control\GraphicsDrivers'
            
            if (-not (Test-Path $Path)) {
                New-Item -Path $Path -Force | Out-Null
            }
            
            # 2 = Enabled, 1 = Disabled
            Set-ItemProperty -Path $Path -Name 'HwSchMode' -Value $(if ($Enabled) { 2 } else { 1 }) -Type DWord
            
            Write-Verbose "GPU Scheduling set to $Enabled (restart required)"
            return [PSCustomObject]@{ 
                Success = $true
                GPUSchedulingEnabled = $Enabled
                RestartRequired = $true
            }
        }
        catch {
            Write-Error "Failed to set GPU Scheduling: $_"
            return [PSCustomObject]@{ Success = $false; Error = $_.Exception.Message }
        }
    }
}
