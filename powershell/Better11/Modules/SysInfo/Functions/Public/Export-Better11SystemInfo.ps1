function Export-Better11SystemInfo {
    <#
    .SYNOPSIS
        Exports system information to a file.
    .DESCRIPTION
        Saves system information to a JSON file.
    .PARAMETER Path
        The file path to save the information.
    .EXAMPLE
        Export-Better11SystemInfo -Path "C:\SystemInfo.json"
    #>
    [CmdletBinding()]
    param(
        [Parameter()]
        [string]$Path
    )

    try {
        if (-not $Path) {
            $Path = Join-Path $env:USERPROFILE "Better11-SystemInfo-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
        }
        
        $SystemInfo = Get-Better11SystemSummary
        
        $SystemInfo | ConvertTo-Json -Depth 10 | Out-File -FilePath $Path -Encoding utf8
        
        Write-Verbose "System info exported to $Path"
        return [PSCustomObject]@{
            Success = $true
            Path = $Path
        }
    }
    catch {
        Write-Error "Failed to export system info: $_"
        return [PSCustomObject]@{ Success = $false; Error = $_.Exception.Message }
    }
}
