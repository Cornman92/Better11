function Restore-Better11Backup {
    <#
    .SYNOPSIS
        Restores system settings from a Better11 backup.
    
    .DESCRIPTION
        Restores configurations from a previously created backup.
    
    .PARAMETER BackupPath
        Path to the backup folder to restore from.
    
    .PARAMETER RestoreRegistry
        Restore registry settings.
    
    .PARAMETER Force
        Skip confirmation prompts.
    
    .EXAMPLE
        Restore-Better11Backup -BackupPath "C:\Users\...\Backups\Better11_Backup_20251210_120000"
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory)]
        [string]$BackupPath,
        
        [Parameter()]
        [switch]$RestoreRegistry,
        
        [Parameter()]
        [switch]$Force
    )
    
    begin {
        if (-not (Test-Path $BackupPath)) {
            throw "Backup path not found: $BackupPath"
        }
        
        Write-Better11Log -Message "Starting restore from: $BackupPath" -Level Info
    }
    
    process {
        try {
            # Load manifest
            $ManifestFile = Join-Path $BackupPath "Manifest.json"
            if (-not (Test-Path $ManifestFile)) {
                throw "Backup manifest not found. Invalid backup."
            }
            
            $Manifest = Get-Content $ManifestFile | ConvertFrom-Json
            
            # Confirm action
            if (-not $Force) {
                $Message = "Restore backup from $($Manifest.Timestamp)? This may overwrite current settings."
                if (-not (Confirm-Better11Action -Message $Message)) {
                    Write-Better11Log -Message "Restore cancelled by user" -Level Info
                    return [PSCustomObject]@{ Success = $false; Message = "Cancelled by user" }
                }
            }
            
            # Create restore point before restoration
            New-Better11RestorePoint -Description "Before Better11 restore from $($Manifest.BackupName)"
            
            $RestoredComponents = @()
            
            # Restore registry if requested
            if ($RestoreRegistry) {
                Write-Better11Log -Message "Restoring registry..." -Level Info
                
                $RegFiles = Get-ChildItem -Path $BackupPath -Filter "Registry_*.reg"
                foreach ($RegFile in $RegFiles) {
                    try {
                        # Import registry file
                        $Process = Start-Process -FilePath "reg.exe" -ArgumentList "import", "`"$($RegFile.FullName)`"" -Wait -PassThru -NoNewWindow
                        if ($Process.ExitCode -eq 0) {
                            $RestoredComponents += "Registry: $($RegFile.Name)"
                        }
                    }
                    catch {
                        Write-Better11Log -Message "Failed to restore registry from $($RegFile.Name): $_" -Level Warning
                    }
                }
            }
            
            # Note: Application restoration would require re-installation
            # We only restore the list for reference
            
            Write-Better11Log -Message "Restore completed successfully" -Level Info
            
            return [PSCustomObject]@{
                Success = $true
                BackupName = $Manifest.BackupName
                RestoredComponents = $RestoredComponents
                Message = "Restore completed. Please restart your computer."
            }
        }
        catch {
            Write-Better11Log -Message "Restore failed: $_" -Level Error
            throw
        }
    }
}
