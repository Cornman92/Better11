function Set-Better11TaskbarAlignment {
    <#
    .SYNOPSIS
        Sets taskbar alignment.
    .DESCRIPTION
        Configures the Windows 11 taskbar alignment (Left or Center).
    .PARAMETER Alignment
        The alignment to set: Left or Center.
    .EXAMPLE
        Set-Better11TaskbarAlignment -Alignment Left
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet('Left', 'Center')]
        [string]$Alignment
    )

    $Value = if ($Alignment -eq 'Left') { 0 } else { 1 }

    if ($PSCmdlet.ShouldProcess("Taskbar", "Set alignment to $Alignment")) {
        try {
            $Path = 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced'
            Set-ItemProperty -Path $Path -Name 'TaskbarAl' -Value $Value -Type DWord
            
            Write-Verbose "Taskbar alignment set to $Alignment"
            return [PSCustomObject]@{ Success = $true; Alignment = $Alignment }
        }
        catch {
            Write-Error "Failed to set taskbar alignment: $_"
            return [PSCustomObject]@{ Success = $false; Error = $_.Exception.Message }
        }
    }
}
