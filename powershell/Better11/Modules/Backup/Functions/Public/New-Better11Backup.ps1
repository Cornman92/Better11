function New-Better11Backup {
    <#
    .SYNOPSIS
        Creates a comprehensive backup of system settings and configurations.
    
    .DESCRIPTION
        Creates a backup including:
        - Registry keys
        - Installed applications list
        - System configurations
        - Better11 settings
    
    .PARAMETER BackupPath
        Path where the backup will be stored. Defaults to user profile.
    
    .PARAMETER IncludeRegistry
        Include registry backups.
    
    .PARAMETER IncludeApps
        Include installed applications list.
    
    .PARAMETER Description
        Description for the backup.
    
    .EXAMPLE
        New-Better11Backup -Description "Before major update"
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter()]
        [string]$BackupPath = "$env:USERPROFILE\Better11\Backups",
        
        [Parameter()]
        [switch]$IncludeRegistry = $true,
        
        [Parameter()]
        [switch]$IncludeApps = $true,
        
        [Parameter()]
        [string]$Description = "Manual backup"
    )
    
    begin {
        $Timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
        $BackupName = "Better11_Backup_$Timestamp"
        $BackupFolder = Join-Path $BackupPath $BackupName
        
        Write-Better11Log -Message "Starting backup creation: $BackupName" -Level Info
    }
    
    process {
        try {
            # Create backup directory
            if (-not (Test-Path $BackupFolder)) {
                New-Item -Path $BackupFolder -ItemType Directory -Force | Out-Null
            }
            
            # Create backup manifest
            $Manifest = @{
                BackupName = $BackupName
                Timestamp = $Timestamp
                Description = $Description
                ComputerName = $env:COMPUTERNAME
                UserName = $env:USERNAME
                OSVersion = [System.Environment]::OSVersion.VersionString
                Components = @()
            }
            
            # Backup registry if requested
            if ($IncludeRegistry) {
                Write-Better11Log -Message "Backing up registry..." -Level Info
                
                $RegistryKeys = @(
                    "HKCU\Software\Microsoft\Windows\CurrentVersion\Run",
                    "HKLM\Software\Microsoft\Windows\CurrentVersion\Run",
                    "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer",
                    "HKLM\System\CurrentControlSet\Services"
                )
                
                foreach ($Key in $RegistryKeys) {
                    $SafeName = $Key -replace '[\\/:]', '_'
                    $RegFile = Join-Path $BackupFolder "Registry_$SafeName.reg"
                    
                    try {
                        Backup-Better11Registry -RegistryPath $Key -BackupPath $RegFile
                        $Manifest.Components += "Registry: $Key"
                    }
                    catch {
                        Write-Better11Log -Message "Failed to backup registry key $Key : $_" -Level Warning
                    }
                }
            }
            
            # Backup installed applications list
            if ($IncludeApps) {
                Write-Better11Log -Message "Backing up applications list..." -Level Info
                
                $AppsFile = Join-Path $BackupFolder "InstalledApps.json"
                $Apps = Get-Better11Apps
                $Apps | ConvertTo-Json -Depth 10 | Out-File $AppsFile -Encoding UTF8
                $Manifest.Components += "Installed Applications"
            }
            
            # Backup Better11 configuration
            $ConfigFile = Join-Path $BackupFolder "Better11Config.json"
            $Config = @{
                Version = "0.4.0"
                BackupDate = $Timestamp
                Settings = @{
                    # Add any Better11 specific settings here
                }
            }
            $Config | ConvertTo-Json -Depth 10 | Out-File $ConfigFile -Encoding UTF8
            $Manifest.Components += "Better11 Configuration"
            
            # Save manifest
            $ManifestFile = Join-Path $BackupFolder "Manifest.json"
            $Manifest | ConvertTo-Json -Depth 10 | Out-File $ManifestFile -Encoding UTF8
            
            Write-Better11Log -Message "Backup created successfully: $BackupFolder" -Level Info
            
            return [PSCustomObject]@{
                Success = $true
                BackupPath = $BackupFolder
                BackupName = $BackupName
                Components = $Manifest.Components
            }
        }
        catch {
            Write-Better11Log -Message "Backup creation failed: $_" -Level Error
            throw
        }
    }
}
