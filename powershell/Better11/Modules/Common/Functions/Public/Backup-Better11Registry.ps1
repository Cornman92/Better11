function Backup-Better11Registry {
    <#
    .SYNOPSIS
        Backs up a registry key to a file.
    
    .DESCRIPTION
        Exports a registry key and its subkeys to a .reg file for backup purposes.
        The backup can be restored later if needed.
    
    .PARAMETER KeyPath
        Full path to the registry key (e.g., "HKCU:\Software\MyApp").
    
    .PARAMETER Destination
        Optional destination file path. If not specified, creates a timestamped
        backup in the Better11 backup directory.
    
    .EXAMPLE
        Backup-Better11Registry -KeyPath "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer"
    
    .EXAMPLE
        Backup-Better11Registry -KeyPath "HKLM:\Software\MyApp" -Destination "C:\Backups\myapp.reg"
    
    .OUTPUTS
        System.IO.FileInfo
        Returns the backup file information.
    #>
    
    [CmdletBinding()]
    [OutputType([System.IO.FileInfo])]
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$KeyPath,
        
        [Parameter()]
        [string]$Destination
    )
    
    begin {
        if (-not (Test-Better11Administrator)) {
            Write-Warning "Registry backup may fail without administrator privileges for system keys"
        }
        
        # Setup backup directory
        $backupDir = Join-Path $env:USERPROFILE '.better11\backups\registry'
        if (-not (Test-Path $backupDir)) {
            New-Item -Path $backupDir -ItemType Directory -Force | Out-Null
        }
    }
    
    process {
        try {
            # Convert PS drive path to registry path
            $regPath = $KeyPath -replace '^HKCU:', 'HKEY_CURRENT_USER' `
                                -replace '^HKLM:', 'HKEY_LOCAL_MACHINE' `
                                -replace '^HKCR:', 'HKEY_CLASSES_ROOT' `
                                -replace '^HKU:', 'HKEY_USERS' `
                                -replace '^HKCC:', 'HKEY_CURRENT_CONFIG'
            
            # Determine backup file path
            if (-not $Destination) {
                $timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
                $safeKeyName = ($KeyPath -replace '[:\\]', '_')
                $Destination = Join-Path $backupDir "backup_${safeKeyName}_${timestamp}.reg"
            }
            
            Write-Better11Log -Message "Backing up registry key: $regPath to $Destination" -Level Info
            
            # Export registry key
            $process = Start-Process -FilePath 'reg.exe' -ArgumentList "export `"$regPath`" `"$Destination`" /y" -Wait -PassThru -WindowStyle Hidden
            
            if ($process.ExitCode -eq 0) {
                Write-Better11Log -Message "Registry backup completed successfully" -Level Info
                return Get-Item $Destination
            }
            else {
                throw "reg.exe exited with code $($process.ExitCode)"
            }
        }
        catch {
            $errorMsg = "Failed to backup registry key ${KeyPath}: $_"
            Write-Better11Log -Message $errorMsg -Level Error
            throw
        }
    }
}
