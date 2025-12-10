function Remove-Better11Backup {
    <#
    .SYNOPSIS
        Removes a Better11 backup.
    
    .PARAMETER BackupPath
        Path to the backup to remove.
    
    .PARAMETER Force
        Skip confirmation prompt.
    
    .EXAMPLE
        Remove-Better11Backup -BackupPath "C:\Users\...\Backups\Better11_Backup_20251210_120000"
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)]
        [string]$BackupPath,
        
        [Parameter()]
        [switch]$Force
    )
    
    if (-not (Test-Path $BackupPath)) {
        throw "Backup not found: $BackupPath"
    }
    
    if (-not $Force) {
        $Message = "Delete backup at $BackupPath ?"
        if (-not (Confirm-Better11Action -Message $Message)) {
            Write-Better11Log -Message "Backup deletion cancelled" -Level Info
            return
        }
    }
    
    try {
        Remove-Item -Path $BackupPath -Recurse -Force
        Write-Better11Log -Message "Backup deleted: $BackupPath" -Level Info
        
        return [PSCustomObject]@{
            Success = $true
            Message = "Backup deleted successfully"
        }
    }
    catch {
        Write-Better11Log -Message "Failed to delete backup: $_" -Level Error
        throw
    }
}
