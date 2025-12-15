function Enable-Better11AdvertisingId {
    <#
    .SYNOPSIS
        Enables Windows advertising ID.
    .DESCRIPTION
        Allows apps to use the advertising ID for personalized experiences.
    .EXAMPLE
        Enable-Better11AdvertisingId
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param()

    if ($PSCmdlet.ShouldProcess("Advertising ID", "Enable")) {
        try {
            $Path = 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo'
            
            if (-not (Test-Path $Path)) {
                New-Item -Path $Path -Force | Out-Null
            }

            Set-ItemProperty -Path $Path -Name 'Enabled' -Value 1 -Type DWord

            Write-Verbose "Advertising ID enabled"
            return [PSCustomObject]@{ Success = $true; AdvertisingId = $true }
        }
        catch {
            Write-Error "Failed to enable advertising ID: $_"
            return [PSCustomObject]@{ Success = $false; Error = $_.Exception.Message }
        }
    }
}
