function Backup-Better11Drivers {
    <#
    .SYNOPSIS
        Backs up installed drivers.
    .DESCRIPTION
        Creates a backup of all third-party drivers using DISM.
    .PARAMETER Path
        The backup destination folder.
    .EXAMPLE
        Backup-Better11Drivers -Path "D:\DriverBackup"
    #>
    [CmdletBinding()]
    param(
        [Parameter()]
        [string]$Path
    )

    try {
        if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
            throw "Administrator privileges required"
        }
        
        if (-not $Path) {
            $Path = Join-Path $script:DefaultBackupPath (Get-Date -Format 'yyyyMMdd-HHmmss')
        }
        
        if (-not (Test-Path $Path)) {
            New-Item -ItemType Directory -Path $Path -Force | Out-Null
        }
        
        Write-Verbose "Backing up drivers to $Path"
        
        # Use DISM to export drivers
        $DismResult = & dism /online /export-driver /destination:"$Path" 2>&1
        
        if ($LASTEXITCODE -ne 0) {
            throw "DISM export failed: $DismResult"
        }
        
        # Get backed up driver count
        $DriverCount = (Get-ChildItem -Path $Path -Filter "*.inf" -Recurse).Count
        
        return [PSCustomObject]@{
            Success = $true
            Path = $Path
            DriversBackedUp = $DriverCount
            Timestamp = Get-Date
        }
    }
    catch {
        Write-Error "Failed to backup drivers: $_"
        return [PSCustomObject]@{ Success = $false; Error = $_.Exception.Message }
    }
}
