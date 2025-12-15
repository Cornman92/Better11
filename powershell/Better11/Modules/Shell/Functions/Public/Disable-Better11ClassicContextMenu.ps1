function Disable-Better11ClassicContextMenu {
    <#
    .SYNOPSIS
        Restores Windows 11 modern context menu.
    .DESCRIPTION
        Returns to the default Windows 11 context menu style.
    .EXAMPLE
        Disable-Better11ClassicContextMenu
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param()

    if ($PSCmdlet.ShouldProcess("Context Menu", "Restore Windows 11 style")) {
        try {
            $Path = 'HKCU:\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}'
            
            if (Test-Path $Path) {
                Remove-Item -Path $Path -Recurse -Force -ErrorAction SilentlyContinue
            }
            
            Write-Verbose "Windows 11 context menu restored. Restart Explorer to apply."
            return [PSCustomObject]@{ 
                Success = $true
                ClassicContextMenu = $false
                Message = "Restart Explorer to apply changes"
            }
        }
        catch {
            Write-Error "Failed to restore Windows 11 context menu: $_"
            return [PSCustomObject]@{ Success = $false; Error = $_.Exception.Message }
        }
    }
}
