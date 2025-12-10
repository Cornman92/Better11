function Write-Better11Log {
    <#
    .SYNOPSIS
        Writes a log message to the Better11 log file and optionally to console.
    
    .DESCRIPTION
        Centralized logging function that writes timestamped messages to both
        file and console. Supports multiple log levels and automatic log rotation.
    
    .PARAMETER Message
        The message to log.
    
    .PARAMETER Level
        Log level: Info, Warning, Error, Debug, Verbose
    
    .PARAMETER NoConsole
        If specified, only writes to file, not to console.
    
    .EXAMPLE
        Write-Better11Log -Message "Application installed successfully" -Level Info
    
    .EXAMPLE
        Write-Better11Log -Message "Failed to download installer" -Level Error
    #>
    
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$Message,
        
        [Parameter()]
        [ValidateSet('Info', 'Warning', 'Error', 'Debug', 'Verbose')]
        [string]$Level = 'Info',
        
        [Parameter()]
        [switch]$NoConsole
    )
    
    begin {
        # Get module private data
        $moduleData = $ExecutionContext.SessionState.Module.Parent.PrivateData
        if ($null -eq $moduleData) {
            $logPath = Join-Path $env:USERPROFILE '.better11\logs'
        }
        else {
            $logPath = $moduleData.LogPath
        }
        
        # Ensure log directory exists
        if (-not (Test-Path $logPath)) {
            New-Item -Path $logPath -ItemType Directory -Force | Out-Null
        }
        
        $logFile = Join-Path $logPath 'better11.log'
        $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    }
    
    process {
        # Format log entry
        $logEntry = "[$timestamp] [$Level] $Message"
        
        # Write to file
        try {
            Add-Content -Path $logFile -Value $logEntry -ErrorAction Stop
        }
        catch {
            Write-Warning "Failed to write to log file: $_"
        }
        
        # Write to console based on level
        if (-not $NoConsole) {
            switch ($Level) {
                'Info' { Write-Host $logEntry -ForegroundColor Green }
                'Warning' { Write-Warning $Message }
                'Error' { Write-Error $Message }
                'Debug' { Write-Debug $Message }
                'Verbose' { Write-Verbose $Message }
            }
        }
        
        # Rotate log if too large (>10MB)
        if ((Get-Item $logFile -ErrorAction SilentlyContinue).Length -gt 10MB) {
            $archiveFile = Join-Path $logPath "better11_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
            Move-Item -Path $logFile -Destination $archiveFile -Force
            Write-Verbose "Log file rotated to: $archiveFile"
        }
    }
}
