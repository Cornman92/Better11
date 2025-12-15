<#
.SYNOPSIS
    Better11 - Windows 11 System Enhancement Tool (PowerShell Edition)

.DESCRIPTION
    Command-line interface for Better11 system enhancement and optimization tools.
    
    This is the PowerShell equivalent of the Python CLI, providing all the same
    functionality using native Windows PowerShell.

.NOTES
    Version: 0.3.0
    Author: Better11 Team
    
.EXAMPLE
    .\Better11.ps1 startup list
    
.EXAMPLE
    .\Better11.ps1 startup disable -Name "Spotify"
    
.EXAMPLE
    .\Better11.ps1 startup info
#>

[CmdletBinding()]
param(
    [Parameter(Position=0)]
    [ValidateSet('startup', 'apps', 'registry', 'config', 'help')]
    [string]$Command,
    
    [Parameter(Position=1)]
    [string]$SubCommand,
    
    [Parameter()]
    [string]$Name,
    
    [Parameter()]
    [string]$Location,
    
    [Parameter()]
    [switch]$Force,
    
    [Parameter()]
    [switch]$DryRun,
    
    [Parameter()]
    [string]$ConfigPath
)

# Import modules
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Import-Module (Join-Path $scriptDir "Better11\Config.psm1") -Force
Import-Module (Join-Path $scriptDir "SystemTools\Safety.psm1") -Force
Import-Module (Join-Path $scriptDir "SystemTools\Base.psm1") -Force
Import-Module (Join-Path $scriptDir "SystemTools\StartupManager.psm1") -Force

# Color output functions
function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-Failure {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host $Message -ForegroundColor Cyan
}

# Help function
function Show-Help {
    @"

Better11 - Windows 11 System Enhancement Tool
==============================================

Usage: .\Better11.ps1 <command> <subcommand> [options]

Commands:
  startup       Manage startup programs
  apps          Manage applications (coming soon)
  registry      Apply registry tweaks (coming soon)
  config        Configuration management (coming soon)
  help          Show this help message

Startup Commands:
  list          List all startup items
    Options:
      -Location <registry|folder|all>  Filter by location
  
  disable       Disable a startup item
    -Name <name>                      Name of item to disable
    -Force                            Skip confirmation
  
  enable        Enable a startup item
    -Name <name>                      Name of item to enable
  
  remove        Permanently remove a startup item
    -Name <name>                      Name of item to remove
    -Force                            Skip confirmation
  
  info          Show startup information and recommendations

Examples:
  .\Better11.ps1 startup list
  .\Better11.ps1 startup list -Location registry
  .\Better11.ps1 startup disable -Name "Spotify"
  .\Better11.ps1 startup disable -Name "Spotify" -Force
  .\Better11.ps1 startup enable -Name "Spotify"
  .\Better11.ps1 startup remove -Name "OldApp" -Force
  .\Better11.ps1 startup info

For more information, visit: https://github.com/better11/better11

"@
}

# Startup list command
function Invoke-StartupList {
    param(
        [string]$Location
    )
    
    try {
        Write-Info "=== Startup Items ==="
        Write-Host ""
        
        $items = Get-StartupItems
        
        # Filter by location if specified
        if ($Location) {
            switch ($Location) {
                'registry' {
                    $items = $items | Where-Object {
                        $_.Location -match 'REGISTRY'
                    }
                }
                'folder' {
                    $items = $items | Where-Object {
                        $_.Location -match 'FOLDER'
                    }
                }
            }
        }
        
        if ($items.Count -eq 0) {
            Write-Host "No startup items found."
            return 0
        }
        
        # Group by location
        $grouped = $items | Group-Object Location
        
        foreach ($group in $grouped) {
            Write-Host ""
            Write-Host "$($group.Name):" -ForegroundColor Yellow
            Write-Host ("-" * 60)
            
            foreach ($item in $group.Group | Sort-Object Name) {
                $status = if ($item.Enabled) { "✓" } else { "✗" }
                $color = if ($item.Enabled) { "Green" } else { "Gray" }
                
                Write-Host "  $status " -NoNewline -ForegroundColor $color
                Write-Host $item.Name -NoNewline
                
                if ($item.Impact -ne 'UNKNOWN') {
                    $impactColor = switch ($item.Impact) {
                        'HIGH' { 'Red' }
                        'MEDIUM' { 'Yellow' }
                        'LOW' { 'Green' }
                        default { 'Gray' }
                    }
                    Write-Host " [$($item.Impact)]" -ForegroundColor $impactColor
                }
                else {
                    Write-Host ""
                }
            }
        }
        
        Write-Host ""
        Write-Host "Total: $($items.Count) items ($($items | Where-Object { $_.Enabled } | Measure-Object | Select-Object -ExpandProperty Count) enabled)"
        
        return 0
    }
    catch {
        Write-Failure "Failed to list startup items: $_"
        return 1
    }
}

# Startup info command
function Invoke-StartupInfo {
    try {
        $manager = [StartupManager]::new()
        $items = $manager.ListStartupItems()
        
        $enabled = $items | Where-Object { $_.Enabled }
        $enabledCount = $enabled.Count
        $bootTime = $manager.GetBootTimeEstimate()
        $recommendations = $manager.GetRecommendations()
        
        Write-Info "=== Startup Information ==="
        Write-Host ""
        Write-Host "Total startup items:    $($items.Count)"
        Write-Host "Enabled items:          $enabledCount"
        Write-Host "Disabled items:         $($items.Count - $enabledCount)"
        Write-Host "Estimated boot impact:  $($bootTime.ToString('0.0')) seconds"
        
        if ($recommendations.Count -gt 0) {
            Write-Host ""
            Write-Info "=== Recommendations ==="
            Write-Host ""
            
            $i = 1
            foreach ($rec in $recommendations) {
                Write-Host "$i. $rec"
                $i++
            }
        }
        else {
            Write-Host ""
            Write-Success "No optimization recommendations at this time."
        }
        
        return 0
    }
    catch {
        Write-Failure "Failed to get startup info: $_"
        return 1
    }
}

# Startup disable command
function Invoke-StartupDisable {
    param(
        [string]$Name,
        [bool]$Force
    )
    
    if (-not $Name) {
        Write-Failure "Error: -Name parameter is required"
        return 1
    }
    
    try {
        $manager = [StartupManager]::new()
        $items = $manager.ListStartupItems()
        
        $item = $items | Where-Object { $_.Name -eq $Name } | Select-Object -First 1
        
        if (-not $item) {
            Write-Failure "Startup item not found: $Name"
            Write-Host ""
            Write-Host "Available items:"
            foreach ($i in $items | Sort-Object Name | Select-Object -First 10) {
                Write-Host "  - $($i.Name)"
            }
            return 1
        }
        
        if (-not $item.Enabled) {
            Write-Host "Item '$Name' is already disabled"
            return 0
        }
        
        # Confirm if not forced
        if (-not $Force) {
            $response = Read-Host "Disable '$Name'? [y/N]"
            if ($response.ToLower() -notin @('y', 'yes')) {
                Write-Host "Cancelled"
                return 0
            }
        }
        
        # Disable the item
        $success = $manager.DisableStartupItem($item)
        
        if ($success) {
            Write-Success "Disabled: $Name"
            return 0
        }
        else {
            Write-Failure "Failed to disable: $Name"
            return 1
        }
    }
    catch {
        Write-Failure "Failed to disable startup item: $_"
        return 1
    }
}

# Startup enable command
function Invoke-StartupEnable {
    param(
        [string]$Name
    )
    
    if (-not $Name) {
        Write-Failure "Error: -Name parameter is required"
        return 1
    }
    
    try {
        $manager = [StartupManager]::new()
        $items = $manager.ListStartupItems()
        
        $item = $items | Where-Object { $_.Name -eq $Name } | Select-Object -First 1
        
        if (-not $item) {
            Write-Failure "Startup item not found: $Name"
            return 1
        }
        
        if ($item.Enabled) {
            Write-Host "Item '$Name' is already enabled"
            return 0
        }
        
        # Enable the item
        $success = $manager.EnableStartupItem($item)
        
        if ($success) {
            Write-Success "Enabled: $Name"
            return 0
        }
        else {
            Write-Failure "Failed to enable: $Name"
            Write-Host "Note: Some items may require manual restoration"
            return 1
        }
    }
    catch {
        Write-Failure "Failed to enable startup item: $_"
        return 1
    }
}

# Startup remove command
function Invoke-StartupRemove {
    param(
        [string]$Name,
        [bool]$Force
    )
    
    if (-not $Name) {
        Write-Failure "Error: -Name parameter is required"
        return 1
    }
    
    try {
        $manager = [StartupManager]::new()
        $items = $manager.ListStartupItems()
        
        $item = $items | Where-Object { $_.Name -eq $Name } | Select-Object -First 1
        
        if (-not $item) {
            Write-Failure "Startup item not found: $Name"
            return 1
        }
        
        # Confirm if not forced
        if (-not $Force) {
            Write-Host "WARNING: This will permanently remove '$Name'" -ForegroundColor Yellow
            Write-Host "Use 'disable' instead if you want to restore it later." -ForegroundColor Yellow
            $response = Read-Host "Permanently remove '$Name'? [y/N]"
            if ($response.ToLower() -notin @('y', 'yes')) {
                Write-Host "Cancelled"
                return 0
            }
        }
        
        # Remove the item
        $success = $manager.RemoveStartupItem($item)
        
        if ($success) {
            Write-Success "Permanently removed: $Name"
            return 0
        }
        else {
            Write-Failure "Failed to remove: $Name"
            return 1
        }
    }
    catch {
        Write-Failure "Failed to remove startup item: $_"
        return 1
    }
}

# Main execution
function Main {
    # No command or help
    if (-not $Command -or $Command -eq 'help') {
        Show-Help
        return 0
    }
    
    # Dispatch commands
    switch ($Command) {
        'startup' {
            switch ($SubCommand) {
                'list' {
                    return Invoke-StartupList -Location $Location
                }
                'info' {
                    return Invoke-StartupInfo
                }
                'disable' {
                    return Invoke-StartupDisable -Name $Name -Force $Force
                }
                'enable' {
                    return Invoke-StartupEnable -Name $Name
                }
                'remove' {
                    return Invoke-StartupRemove -Name $Name -Force $Force
                }
                default {
                    Write-Failure "Unknown startup subcommand: $SubCommand"
                    Write-Host "Use '.\Better11.ps1 help' for usage information"
                    return 1
                }
            }
        }
        'apps' {
            Write-Host "Application management coming soon!" -ForegroundColor Yellow
            return 0
        }
        'registry' {
            Write-Host "Registry tweaks coming soon!" -ForegroundColor Yellow
            return 0
        }
        'config' {
            Write-Host "Configuration management coming soon!" -ForegroundColor Yellow
            return 0
        }
        default {
            Write-Failure "Unknown command: $Command"
            Write-Host "Use '.\Better11.ps1 help' for usage information"
            return 1
        }
    }
}

# Execute main
$exitCode = Main
exit $exitCode
