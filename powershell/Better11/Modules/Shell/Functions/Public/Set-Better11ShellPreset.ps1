function Set-Better11ShellPreset {
    <#
    .SYNOPSIS
        Applies a shell customization preset.
    .DESCRIPTION
        Applies a predefined set of shell settings.
    .PARAMETER Preset
        The preset to apply: Productivity, Minimalist, Classic, or Default.
    .EXAMPLE
        Set-Better11ShellPreset -Preset Productivity
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet('Productivity', 'Minimalist', 'Classic', 'Default')]
        [string]$Preset
    )

    if ($PSCmdlet.ShouldProcess("Shell Settings", "Apply $Preset preset")) {
        $Results = @{
            Preset = $Preset
            Changes = @()
            Success = $true
        }

        try {
            switch ($Preset) {
                'Productivity' {
                    $Results.Changes += Set-Better11TaskbarAlignment -Alignment Left
                    $Results.Changes += Set-Better11SearchMode -Mode IconOnly
                    $Results.Changes += Set-Better11WidgetsVisible -Visible $false
                    $Results.Changes += Set-Better11TaskViewVisible -Visible $false
                    $Results.Changes += Enable-Better11ClassicContextMenu
                }
                'Minimalist' {
                    $Results.Changes += Set-Better11TaskbarAlignment -Alignment Center
                    $Results.Changes += Set-Better11SearchMode -Mode Hidden
                    $Results.Changes += Set-Better11WidgetsVisible -Visible $false
                    $Results.Changes += Set-Better11TaskViewVisible -Visible $false
                    $Results.Changes += Set-Better11CopilotVisible -Visible $false
                    $Results.Changes += Enable-Better11ClassicContextMenu
                }
                'Classic' {
                    $Results.Changes += Set-Better11TaskbarAlignment -Alignment Left
                    $Results.Changes += Set-Better11SearchMode -Mode SearchBox
                    $Results.Changes += Set-Better11WidgetsVisible -Visible $false
                    $Results.Changes += Set-Better11TaskViewVisible -Visible $true
                    $Results.Changes += Set-Better11CopilotVisible -Visible $false
                    $Results.Changes += Enable-Better11ClassicContextMenu
                }
                'Default' {
                    $Results.Changes += Set-Better11TaskbarAlignment -Alignment Center
                    $Results.Changes += Set-Better11SearchMode -Mode SearchBox
                    $Results.Changes += Set-Better11WidgetsVisible -Visible $true
                    $Results.Changes += Set-Better11TaskViewVisible -Visible $true
                    $Results.Changes += Set-Better11CopilotVisible -Visible $true
                    $Results.Changes += Disable-Better11ClassicContextMenu
                }
            }

            Write-Verbose "$Preset shell preset applied"
            return [PSCustomObject]$Results
        }
        catch {
            Write-Error "Failed to apply shell preset: $_"
            $Results.Success = $false
            $Results.Error = $_.Exception.Message
            return [PSCustomObject]$Results
        }
    }
}
