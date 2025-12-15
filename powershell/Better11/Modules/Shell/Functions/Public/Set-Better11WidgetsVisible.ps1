function Set-Better11WidgetsVisible {
    <#
    .SYNOPSIS
        Shows or hides the Widgets button.
    .DESCRIPTION
        Controls the visibility of the Widgets button on the taskbar.
    .PARAMETER Visible
        Whether to show the button.
    .EXAMPLE
        Set-Better11WidgetsVisible -Visible $false
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory = $true)]
        [bool]$Visible
    )

    $Action = if ($Visible) { "Show" } else { "Hide" }

    if ($PSCmdlet.ShouldProcess("Widgets button", $Action)) {
        try {
            $Path = 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced'
            Set-ItemProperty -Path $Path -Name 'TaskbarDa' -Value $(if ($Visible) { 1 } else { 0 }) -Type DWord
            
            Write-Verbose "Widgets button visibility set to $Visible"
            return [PSCustomObject]@{ Success = $true; Visible = $Visible }
        }
        catch {
            Write-Error "Failed to set Widgets visibility: $_"
            return [PSCustomObject]@{ Success = $false; Error = $_.Exception.Message }
        }
    }
}
