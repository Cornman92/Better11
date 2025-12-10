function Import-Better11Configuration {
    <#
    .SYNOPSIS
        Imports Better11 configuration from a file.
    
    .PARAMETER ConfigPath
        Path to the configuration file.
    
    .PARAMETER InstallApps
        Automatically install applications from the configuration.
    
    .EXAMPLE
        Import-Better11Configuration -ConfigPath "C:\Configs\better11-config.json"
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$ConfigPath,
        
        [Parameter()]
        [switch]$InstallApps
    )
    
    if (-not (Test-Path $ConfigPath)) {
        throw "Configuration file not found: $ConfigPath"
    }
    
    try {
        $Config = Get-Content $ConfigPath | ConvertFrom-Json
        
        Write-Better11Log -Message "Importing configuration from: $ConfigPath" -Level Info
        
        $Results = @{
            Success = $true
            ImportedSettings = 0
            InstalledApps = @()
        }
        
        # Install applications if requested
        if ($InstallApps -and $Config.InstalledApps) {
            foreach ($App in $Config.InstalledApps) {
                try {
                    Write-Better11Log -Message "Installing $($App.Name)..." -Level Info
                    $InstallResult = Install-Better11App -AppId $App.AppId -Force
                    
                    if ($InstallResult.Success) {
                        $Results.InstalledApps += $App.Name
                    }
                }
                catch {
                    Write-Better11Log -Message "Failed to install $($App.Name): $_" -Level Warning
                }
            }
        }
        
        Write-Better11Log -Message "Configuration import completed" -Level Info
        
        return [PSCustomObject]$Results
    }
    catch {
        Write-Better11Log -Message "Failed to import configuration: $_" -Level Error
        throw
    }
}
