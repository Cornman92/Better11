function Set-Better11SearchMode {
    <#
    .SYNOPSIS
        Sets the search box display mode.
    .DESCRIPTION
        Configures how the search box appears on the taskbar.
    .PARAMETER Mode
        The display mode: Hidden, IconOnly, SearchBox, or IconAndLabel.
    .EXAMPLE
        Set-Better11SearchMode -Mode IconOnly
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet('Hidden', 'IconOnly', 'SearchBox', 'IconAndLabel')]
        [string]$Mode
    )

    $Value = switch ($Mode) {
        'Hidden' { 0 }
        'IconOnly' { 1 }
        'SearchBox' { 2 }
        'IconAndLabel' { 3 }
    }

    if ($PSCmdlet.ShouldProcess("Search Box", "Set mode to $Mode")) {
        try {
            $Path = 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced'
            Set-ItemProperty -Path $Path -Name 'SearchboxTaskbarMode' -Value $Value -Type DWord
            
            Write-Verbose "Search mode set to $Mode"
            return [PSCustomObject]@{ Success = $true; Mode = $Mode }
        }
        catch {
            Write-Error "Failed to set search mode: $_"
            return [PSCustomObject]@{ Success = $false; Error = $_.Exception.Message }
        }
    }
}
