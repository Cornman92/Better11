function Disable-Better11AdvertisingId {
    <#
    .SYNOPSIS
        Disables Windows advertising ID.
    .DESCRIPTION
        Prevents apps from using the advertising ID to track user activity.
    .EXAMPLE
        Disable-Better11AdvertisingId
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param()

    if ($PSCmdlet.ShouldProcess("Advertising ID", "Disable")) {
        try {
            $Path = 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo'
            
            if (-not (Test-Path $Path)) {
                New-Item -Path $Path -Force | Out-Null
            }

            Set-ItemProperty -Path $Path -Name 'Enabled' -Value 0 -Type DWord

            Write-Verbose "Advertising ID disabled"
            return [PSCustomObject]@{ Success = $true; AdvertisingId = $false }
        }
        catch {
            Write-Error "Failed to disable advertising ID: $_"
            return [PSCustomObject]@{ Success = $false; Error = $_.Exception.Message }
        }
    }
}
