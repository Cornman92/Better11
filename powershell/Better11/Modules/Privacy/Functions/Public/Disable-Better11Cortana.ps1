function Disable-Better11Cortana {
    <#
    .SYNOPSIS
        Disables Cortana.
    .DESCRIPTION
        Disables Cortana via group policy registry settings.
    .EXAMPLE
        Disable-Better11Cortana
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param()

    if ($PSCmdlet.ShouldProcess("Cortana", "Disable")) {
        try {
            $Path = 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\Windows Search'
            
            if (-not (Test-Path $Path)) {
                New-Item -Path $Path -Force | Out-Null
            }

            Set-ItemProperty -Path $Path -Name 'AllowCortana' -Value 0 -Type DWord

            Write-Verbose "Cortana disabled"
            return [PSCustomObject]@{ Success = $true; CortanaEnabled = $false }
        }
        catch {
            Write-Error "Failed to disable Cortana: $_"
            return [PSCustomObject]@{ Success = $false; Error = $_.Exception.Message }
        }
    }
}
