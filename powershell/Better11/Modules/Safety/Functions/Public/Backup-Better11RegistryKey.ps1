function Backup-Better11RegistryKey {
    <#
    .SYNOPSIS
        Backs up a registry key to a file.
    .DESCRIPTION
        Exports a registry key and its subkeys to a .reg file for backup purposes.
    .PARAMETER KeyPath
        Full registry path (e.g., "HKCU:\SOFTWARE\Microsoft\Windows")
    .PARAMETER BackupPath
        Path to save the backup file. If not specified, auto-generates.
    .EXAMPLE
        Backup-Better11RegistryKey -KeyPath "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer"
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory = $true)]
        [string]$KeyPath,

        [Parameter()]
        [string]$BackupPath
    )

    # Convert PowerShell path to reg.exe format
    $RegPath = $KeyPath -replace 'HKCU:', 'HKCU' -replace 'HKLM:', 'HKLM' -replace 'HKU:', 'HKU'

    if (-not $BackupPath) {
        $BackupDir = Join-Path $env:USERPROFILE ".better11\backups\registry"
        if (-not (Test-Path $BackupDir)) {
            New-Item -Path $BackupDir -ItemType Directory -Force | Out-Null
        }
        $Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $SafeName = ($RegPath -replace '\\', '_' -replace ':', '') -replace '[^a-zA-Z0-9_]', ''
        $BackupPath = Join-Path $BackupDir "$SafeName`_$Timestamp.reg"
    }

    if ($PSCmdlet.ShouldProcess($KeyPath, "Backup registry key")) {
        try {
            Write-Verbose "Backing up registry key: $KeyPath to $BackupPath"
            
            $result = & reg.exe export $RegPath $BackupPath /y 2>&1
            
            if ($LASTEXITCODE -eq 0) {
                Write-Verbose "Registry backup created: $BackupPath"
                return [PSCustomObject]@{
                    Success = $true
                    KeyPath = $KeyPath
                    BackupPath = $BackupPath
                    Timestamp = Get-Date
                }
            } else {
                throw "reg.exe failed: $result"
            }
        }
        catch {
            Write-Error "Failed to backup registry key: $_"
            return [PSCustomObject]@{
                Success = $false
                KeyPath = $KeyPath
                Error = $_.Exception.Message
            }
        }
    }
}
