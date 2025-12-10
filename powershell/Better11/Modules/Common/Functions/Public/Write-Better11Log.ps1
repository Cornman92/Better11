function Write-Better11Log {
    <#
    .SYNOPSIS
        Writes a log entry to the Better11 log file.
    
    .DESCRIPTION
        Writes structured log entries to the Better11 log file with timestamp,
        level, and message. Supports multiple log levels and automatic log rotation.
    
    .PARAMETER Message
        The message to log
    
    .PARAMETER Level
        Log level: Info, Warning, Error, Debug, Verbose
    
    .PARAMETER Component
        Optional component/module name for the log entry
    
    .EXAMPLE
        Write-Better11Log -Message "Application installed successfully" -Level Info
    
    .EXAMPLE
        Write-Better11Log -Message "Failed to connect" -Level Error -Component "Network"
    
    .OUTPUTS
        None
    #>
    
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$Message,
        
        [Parameter()]
        [ValidateSet('Info', 'Warning', 'Error', 'Debug', 'Verbose')]
        [string]$Level = 'Info',
        
        [Parameter()]
        [string]$Component = 'Better11'
    )
    
    begin {
        $LogFile = Join-Path $script:LogPath "better11-$(Get-Date -Format 'yyyy-MM-dd').log"
        
        # Ensure log directory exists
        if (-not (Test-Path $script:LogPath)) {
            New-Item -Path $script:LogPath -ItemType Directory -Force | Out-Null
        }
    }
    
    process {
        $Timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
        $LogEntry = "[$Timestamp] [$Level] [$Component] $Message"
        
        # Write to log file
        Add-Content -Path $LogFile -Value $LogEntry -ErrorAction SilentlyContinue
        
        # Also write to appropriate stream
        switch ($Level) {
            'Info'    { Write-Verbose $Message }
            'Warning' { Write-Warning $Message }
            'Error'   { Write-Error $Message }
            'Debug'   { Write-Debug $Message }
            'Verbose' { Write-Verbose $Message }
        }
    }
}
