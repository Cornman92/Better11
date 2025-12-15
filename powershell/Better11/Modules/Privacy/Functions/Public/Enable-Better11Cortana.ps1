function Enable-Better11Cortana {
    <#
    .SYNOPSIS
        Enables Cortana.
    .DESCRIPTION
        Re-enables Cortana by removing the policy restriction.
    .EXAMPLE
        Enable-Better11Cortana
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param()

    if ($PSCmdlet.ShouldProcess("Cortana", "Enable")) {
        try {
            $Path = 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\Windows Search'
            
            if (Test-Path $Path) {
                Remove-ItemProperty -Path $Path -Name 'AllowCortana' -ErrorAction SilentlyContinue
            }

            Write-Verbose "Cortana enabled"
            return [PSCustomObject]@{ Success = $true; CortanaEnabled = $true }
        }
        catch {
            Write-Error "Failed to enable Cortana: $_"
            return [PSCustomObject]@{ Success = $false; Error = $_.Exception.Message }
        }
    }
}
