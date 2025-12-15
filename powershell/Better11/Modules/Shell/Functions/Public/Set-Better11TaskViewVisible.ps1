function Set-Better11TaskViewVisible {
    <#
    .SYNOPSIS
        Shows or hides the Task View button.
    .DESCRIPTION
        Controls the visibility of the Task View button on the taskbar.
    .PARAMETER Visible
        Whether to show the button.
    .EXAMPLE
        Set-Better11TaskViewVisible -Visible $false
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory = $true)]
        [bool]$Visible
    )

    $Action = if ($Visible) { "Show" } else { "Hide" }

    if ($PSCmdlet.ShouldProcess("Task View button", $Action)) {
        try {
            $Path = 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced'
            Set-ItemProperty -Path $Path -Name 'ShowTaskViewButton' -Value $(if ($Visible) { 1 } else { 0 }) -Type DWord
            
            Write-Verbose "Task View button visibility set to $Visible"
            return [PSCustomObject]@{ Success = $true; Visible = $Visible }
        }
        catch {
            Write-Error "Failed to set Task View visibility: $_"
            return [PSCustomObject]@{ Success = $false; Error = $_.Exception.Message }
        }
    }
}
