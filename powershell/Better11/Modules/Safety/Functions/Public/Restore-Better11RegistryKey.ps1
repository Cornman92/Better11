function Restore-Better11RegistryKey {
    <#
    .SYNOPSIS
        Restores a registry key from a backup file.
    .DESCRIPTION
        Imports a previously exported .reg file to restore registry settings.
    .PARAMETER BackupPath
        Path to the .reg backup file.
    .EXAMPLE
        Restore-Better11RegistryKey -BackupPath "C:\backup\settings.reg"
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateScript({ Test-Path $_ -PathType Leaf })]
        [string]$BackupPath
    )

    if (-not (Test-Better11Administrator)) {
        throw "Restoring registry requires administrator privileges"
    }

    if ($PSCmdlet.ShouldProcess($BackupPath, "Restore registry from backup")) {
        try {
            Write-Verbose "Restoring registry from: $BackupPath"
            
            $result = & reg.exe import $BackupPath 2>&1
            
            if ($LASTEXITCODE -eq 0) {
                Write-Verbose "Registry restored successfully"
                return [PSCustomObject]@{
                    Success = $true
                    BackupPath = $BackupPath
                    Timestamp = Get-Date
                }
            } else {
                throw "reg.exe failed: $result"
            }
        }
        catch {
            Write-Error "Failed to restore registry: $_"
            return [PSCustomObject]@{
                Success = $false
                BackupPath = $BackupPath
                Error = $_.Exception.Message
            }
        }
    }
}
