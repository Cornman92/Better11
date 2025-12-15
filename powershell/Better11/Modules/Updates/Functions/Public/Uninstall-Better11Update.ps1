function Uninstall-Better11Update {
    <#
    .SYNOPSIS
        Uninstalls a Windows update.
    .DESCRIPTION
        Removes an installed Windows update by its KB number.
    .PARAMETER KBArticle
        The KB article number (e.g., "KB5001234" or "5001234").
    .PARAMETER NoRestart
        Prevent automatic restart after uninstallation.
    .EXAMPLE
        Uninstall-Better11Update -KBArticle "KB5001234"
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory = $true)]
        [string]$KBArticle,

        [Parameter()]
        [switch]$NoRestart
    )

    # Normalize KB article format
    $KB = $KBArticle -replace '^KB', ''

    if ($PSCmdlet.ShouldProcess("KB$KB", "Uninstall")) {
        try {
            Write-Verbose "Uninstalling update KB$KB..."
            
            $Args = "/uninstall /kb:$KB /quiet"
            if ($NoRestart) {
                $Args += " /norestart"
            }
            
            $Process = Start-Process -FilePath "wusa.exe" -ArgumentList $Args -Wait -PassThru
            
            $Result = switch ($Process.ExitCode) {
                0 { [PSCustomObject]@{ Success = $true; Message = "Update uninstalled successfully"; RebootRequired = $false } }
                3010 { [PSCustomObject]@{ Success = $true; Message = "Update uninstalled, restart required"; RebootRequired = $true } }
                2359303 { [PSCustomObject]@{ Success = $false; Message = "Update not installed"; RebootRequired = $false } }
                default { [PSCustomObject]@{ Success = $false; Message = "Uninstall failed with code $($Process.ExitCode)"; RebootRequired = $false } }
            }
            
            return $Result
        }
        catch {
            Write-Error "Failed to uninstall update: $_"
            return [PSCustomObject]@{ Success = $false; Message = $_.Exception.Message }
        }
    }
}
