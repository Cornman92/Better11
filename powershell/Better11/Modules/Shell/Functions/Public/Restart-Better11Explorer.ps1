function Restart-Better11Explorer {
    <#
    .SYNOPSIS
        Restarts Windows Explorer.
    .DESCRIPTION
        Stops and restarts the Windows Explorer process to apply shell changes.
    .EXAMPLE
        Restart-Better11Explorer
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param()

    if ($PSCmdlet.ShouldProcess("Windows Explorer", "Restart")) {
        try {
            Write-Verbose "Restarting Windows Explorer..."
            
            # Stop Explorer
            Stop-Process -Name explorer -Force -ErrorAction SilentlyContinue
            
            # Wait a moment
            Start-Sleep -Seconds 2
            
            # Start Explorer
            Start-Process explorer.exe
            
            Write-Verbose "Windows Explorer restarted"
            return [PSCustomObject]@{ Success = $true; Message = "Explorer restarted" }
        }
        catch {
            Write-Error "Failed to restart Explorer: $_"
            return [PSCustomObject]@{ Success = $false; Error = $_.Exception.Message }
        }
    }
}
