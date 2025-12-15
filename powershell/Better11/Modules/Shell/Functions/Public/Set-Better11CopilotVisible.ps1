function Set-Better11CopilotVisible {
    <#
    .SYNOPSIS
        Shows or hides the Copilot button.
    .DESCRIPTION
        Controls the visibility of the Copilot button on the taskbar.
    .PARAMETER Visible
        Whether to show the button.
    .EXAMPLE
        Set-Better11CopilotVisible -Visible $false
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory = $true)]
        [bool]$Visible
    )

    $Action = if ($Visible) { "Show" } else { "Hide" }

    if ($PSCmdlet.ShouldProcess("Copilot button", $Action)) {
        try {
            $Path = 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced'
            Set-ItemProperty -Path $Path -Name 'ShowCopilotButton' -Value $(if ($Visible) { 1 } else { 0 }) -Type DWord
            
            Write-Verbose "Copilot button visibility set to $Visible"
            return [PSCustomObject]@{ Success = $true; Visible = $Visible }
        }
        catch {
            Write-Error "Failed to set Copilot visibility: $_"
            return [PSCustomObject]@{ Success = $false; Error = $_.Exception.Message }
        }
    }
}
