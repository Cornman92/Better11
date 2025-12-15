function Export-Better11Configuration {
    <#
    .SYNOPSIS
        Exports Better11 configuration to a file.
    
    .PARAMETER OutputPath
        Path where the configuration will be exported.
    
    .EXAMPLE
        Export-Better11Configuration -OutputPath "C:\Configs\better11-config.json"
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$OutputPath
    )
    
    try {
        $Config = @{
            Version = "0.4.0"
            ExportDate = (Get-Date).ToString('o')
            ComputerName = $env:COMPUTERNAME
            InstalledApps = Get-Better11Apps | Where-Object { $_.IsInstalled }
            Settings = @{
                # Export any Better11 settings
            }
        }
        
        $Config | ConvertTo-Json -Depth 10 | Out-File $OutputPath -Encoding UTF8
        
        Write-Better11Log -Message "Configuration exported to: $OutputPath" -Level Info
        
        return [PSCustomObject]@{
            Success = $true
            Path = $OutputPath
        }
    }
    catch {
        Write-Better11Log -Message "Failed to export configuration: $_" -Level Error
        throw
    }
}
