function Enable-Better11ClassicContextMenu {
    <#
    .SYNOPSIS
        Enables Windows 10-style classic context menu.
    .DESCRIPTION
        Restores the full context menu without needing "Show more options".
    .EXAMPLE
        Enable-Better11ClassicContextMenu
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param()

    if ($PSCmdlet.ShouldProcess("Context Menu", "Enable classic style")) {
        try {
            $Path = 'HKCU:\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32'
            
            # Create the key path
            $ParentPath = 'HKCU:\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}'
            if (-not (Test-Path $ParentPath)) {
                New-Item -Path $ParentPath -Force | Out-Null
            }
            if (-not (Test-Path $Path)) {
                New-Item -Path $Path -Force | Out-Null
            }
            
            # Set default value to empty string
            Set-ItemProperty -Path $Path -Name '(Default)' -Value ''
            
            Write-Verbose "Classic context menu enabled. Restart Explorer to apply."
            return [PSCustomObject]@{ 
                Success = $true
                ClassicContextMenu = $true
                Message = "Restart Explorer to apply changes"
            }
        }
        catch {
            Write-Error "Failed to enable classic context menu: $_"
            return [PSCustomObject]@{ Success = $false; Error = $_.Exception.Message }
        }
    }
}
