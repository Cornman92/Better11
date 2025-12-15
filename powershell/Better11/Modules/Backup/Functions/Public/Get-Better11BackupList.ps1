function Get-Better11BackupList {
    <#
    .SYNOPSIS
        Lists all available Better11 backups.
    
    .PARAMETER BackupPath
        Path to search for backups. Defaults to user profile.
    
    .EXAMPLE
        Get-Better11BackupList
    #>
    [CmdletBinding()]
    param(
        [Parameter()]
        [string]$BackupPath = "$env:USERPROFILE\Better11\Backups"
    )
    
    if (-not (Test-Path $BackupPath)) {
        Write-Better11Log -Message "No backups found at $BackupPath" -Level Info
        return @()
    }
    
    $Backups = Get-ChildItem -Path $BackupPath -Directory | Where-Object { $_.Name -like "Better11_Backup_*" }
    
    $BackupList = foreach ($Backup in $Backups) {
        $ManifestFile = Join-Path $Backup.FullName "Manifest.json"
        
        if (Test-Path $ManifestFile) {
            $Manifest = Get-Content $ManifestFile | ConvertFrom-Json
            
            [PSCustomObject]@{
                BackupName = $Manifest.BackupName
                Timestamp = $Manifest.Timestamp
                Description = $Manifest.Description
                ComputerName = $Manifest.ComputerName
                Components = $Manifest.Components
                Path = $Backup.FullName
                SizeBytes = (Get-ChildItem $Backup.FullName -Recurse | Measure-Object -Property Length -Sum).Sum
            }
        }
    }
    
    return $BackupList | Sort-Object Timestamp -Descending
}
