<#
.SYNOPSIS
    Windows startup program management.

.DESCRIPTION
    This module provides functionality to list, enable, disable, and remove
    startup programs from various locations in Windows.
#>

using module .\Base.psm1
using module .\Safety.psm1

# Startup location enumeration
enum StartupLocation {
    REGISTRY_HKLM_RUN
    REGISTRY_HKCU_RUN
    REGISTRY_HKLM_RUN_ONCE
    REGISTRY_HKCU_RUN_ONCE
    STARTUP_FOLDER_COMMON
    STARTUP_FOLDER_USER
    TASK_SCHEDULER
    SERVICES
}

# Startup impact enumeration
enum StartupImpact {
    HIGH      # >3s delay
    MEDIUM    # 1-3s delay
    LOW       # <1s delay
    UNKNOWN
}

# Startup item class
class StartupItem {
    [string]$Name
    [string]$Command
    [StartupLocation]$Location
    [bool]$Enabled
    [StartupImpact]$Impact = [StartupImpact]::UNKNOWN
    [string]$Publisher
    
    StartupItem(
        [string]$Name,
        [string]$Command,
        [StartupLocation]$Location,
        [bool]$Enabled
    ) {
        $this.Name = $Name
        $this.Command = $Command
        $this.Location = $Location
        $this.Enabled = $Enabled
    }
    
    [string] ToString() {
        $status = if ($this.Enabled) { "✓" } else { "✗" }
        return "$status $($this.Name) [$($this.Location)]"
    }
}

# Startup Manager class
class StartupManager : SystemTool {
    # Registry keys to check
    static [hashtable[]] $RegistryKeys = @(
        @{
            Hive = 'HKLM'
            SubKey = 'SOFTWARE\Microsoft\Windows\CurrentVersion\Run'
            Location = [StartupLocation]::REGISTRY_HKLM_RUN
        },
        @{
            Hive = 'HKCU'
            SubKey = 'SOFTWARE\Microsoft\Windows\CurrentVersion\Run'
            Location = [StartupLocation]::REGISTRY_HKCU_RUN
        },
        @{
            Hive = 'HKLM'
            SubKey = 'SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce'
            Location = [StartupLocation]::REGISTRY_HKLM_RUN_ONCE
        },
        @{
            Hive = 'HKCU'
            SubKey = 'SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce'
            Location = [StartupLocation]::REGISTRY_HKCU_RUN_ONCE
        }
    )
    
    StartupManager([hashtable]$Config = @{}, [bool]$DryRun = $false) : base($Config, $DryRun) {
    }
    
    [ToolMetadata] GetMetadata() {
        return [ToolMetadata]::new(
            "Startup Manager",
            "Manage Windows startup programs",
            "0.3.0"
        )
    }
    
    [void] ValidateEnvironment() {
        Test-WindowsPlatform
    }
    
    [bool] Execute() {
        $items = $this.ListStartupItems()
        $this.Log("Found $($items.Count) startup items")
        return $true
    }
    
    # List all startup items
    [StartupItem[]] ListStartupItems() {
        $items = [System.Collections.Generic.List[StartupItem]]::new()
        
        # Get registry items
        $items.AddRange($this.GetRegistryItems())
        
        # Get startup folder items
        $items.AddRange($this.GetStartupFolderItems())
        
        # Get scheduled tasks
        $items.AddRange($this.GetScheduledTasks())
        
        # TODO: Add services
        
        $this.Log("Listed $($items.Count) startup items")
        return $items.ToArray()
    }
    
    # Get registry startup items
    [StartupItem[]] GetRegistryItems() {
        $items = [System.Collections.Generic.List[StartupItem]]::new()
        
        foreach ($regKey in [StartupManager]::RegistryKeys) {
            $hivePath = "$($regKey.Hive):\"
            $fullPath = Join-Path $hivePath $regKey.SubKey
            
            try {
                if (Test-Path $fullPath) {
                    $key = Get-Item -Path $fullPath -ErrorAction Stop
                    
                    foreach ($valueName in $key.GetValueNames()) {
                        if ([string]::IsNullOrWhiteSpace($valueName)) {
                            continue
                        }
                        
                        $command = $key.GetValue($valueName)
                        
                        $item = [StartupItem]::new(
                            $valueName,
                            $command,
                            $regKey.Location,
                            $true
                        )
                        
                        $items.Add($item)
                    }
                }
            }
            catch {
                $this.LogWarning("Failed to read registry key ${fullPath}: $_")
            }
        }
        
        return $items.ToArray()
    }
    
    # Get startup folder items
    [StartupItem[]] GetStartupFolderItems() {
        $items = [System.Collections.Generic.List[StartupItem]]::new()
        
        # User startup folder
        $userStartup = [Environment]::GetFolderPath('Startup')
        if (Test-Path $userStartup) {
            $items.AddRange($this.GetFolderItems($userStartup, [StartupLocation]::STARTUP_FOLDER_USER))
        }
        
        # Common startup folder
        $commonStartup = [Environment]::GetFolderPath('CommonStartup')
        if (Test-Path $commonStartup) {
            $items.AddRange($this.GetFolderItems($commonStartup, [StartupLocation]::STARTUP_FOLDER_COMMON))
        }
        
        return $items.ToArray()
    }
    
    # Get items from a specific folder
    [StartupItem[]] GetFolderItems([string]$FolderPath, [StartupLocation]$Location) {
        $items = [System.Collections.Generic.List[StartupItem]]::new()
        
        try {
            $files = Get-ChildItem -Path $FolderPath -File -ErrorAction Stop
            
            foreach ($file in $files) {
                # Check if file is disabled (has .disabled extension)
                $enabled = $file.Extension -ne '.disabled'
                $name = if ($enabled) { $file.BaseName } else { 
                    [System.IO.Path]::GetFileNameWithoutExtension($file.BaseName)
                }
                
                $item = [StartupItem]::new(
                    $name,
                    $file.FullName,
                    $Location,
                    $enabled
                )
                
                $items.Add($item)
            }
        }
        catch {
            $this.LogWarning("Failed to read startup folder ${FolderPath}: $_")
        }
        
        return $items.ToArray()
    }
    
    # Get scheduled tasks that run at startup/logon
    [StartupItem[]] GetScheduledTasks() {
        $items = [System.Collections.Generic.List[StartupItem]]::new()
        
        try {
            # Query all scheduled tasks
            $tasks = schtasks /query /fo CSV /v 2>$null | ConvertFrom-Csv
            
            foreach ($task in $tasks) {
                # Filter for startup/logon tasks
                $triggers = $task.'Logon Mode'
                if ($null -ne $triggers) {
                    $triggersLower = $triggers.ToLower()
                    if ($triggersLower -match 'logon|startup|boot') {
                        $enabled = $task.Status -eq 'Ready' -or $task.Status -eq 'Running'
                        
                        $item = [StartupItem]::new(
                            $task.TaskName,
                            "Task: $($task.TaskName)",
                            [StartupLocation]::TASK_SCHEDULER,
                            $enabled
                        )
                        $item.Impact = [StartupImpact]::MEDIUM
                        
                        $items.Add($item)
                    }
                }
            }
            
            $this.Log("Found $($items.Count) scheduled startup tasks")
        }
        catch {
            $this.LogWarning("Failed to query scheduled tasks: $_")
        }
        
        return $items.ToArray()
    }
    
    # Disable a startup item
    [bool] DisableStartupItem([StartupItem]$Item) {
        if ($this.DryRun) {
            $this.Log("DRY RUN: Would disable $($Item.Name)")
            return $true
        }
        
        if (-not $Item.Enabled) {
            $this.LogWarning("Item $($Item.Name) is already disabled")
            return $true
        }
        
        $this.Log("Disabling startup item: $($Item.Name)")
        
        try {
            switch ($Item.Location) {
                { $_ -in @([StartupLocation]::REGISTRY_HKLM_RUN,
                           [StartupLocation]::REGISTRY_HKCU_RUN,
                           [StartupLocation]::REGISTRY_HKLM_RUN_ONCE,
                           [StartupLocation]::REGISTRY_HKCU_RUN_ONCE) } {
                    return $this.DisableRegistryItem($Item)
                }
                { $_ -in @([StartupLocation]::STARTUP_FOLDER_USER,
                           [StartupLocation]::STARTUP_FOLDER_COMMON) } {
                    return $this.DisableFolderItem($Item)
                }
                ([StartupLocation]::TASK_SCHEDULER) {
                    return $this.DisableScheduledTask($Item)
                }
                default {
                    throw "Disable not yet implemented for $($Item.Location)"
                }
            }
        }
        catch {
            $this.LogError("Failed to disable $($Item.Name): $_")
            throw [SafetyError]::new("Failed to disable startup item: $_")
        }
    }
    
    # Disable registry item
    [bool] DisableRegistryItem([StartupItem]$Item) {
        # Get registry path
        $regPath = $this.GetRegistryPath($Item.Location)
        
        try {
            # Backup the value first
            $backupPath = $regPath -replace 'CurrentVersion\\', 'CurrentVersion\Better11Backup\'
            
            # Create backup
            try {
                if (-not (Test-Path $backupPath)) {
                    New-Item -Path $backupPath -Force | Out-Null
                }
                
                $key = Get-Item -Path $regPath
                $value = $key.GetValue($Item.Name)
                
                Set-ItemProperty -Path $backupPath -Name $Item.Name -Value $value -Type String
                $this.Log("Backed up $($Item.Name) to $backupPath")
            }
            catch {
                $this.LogWarning("Failed to create backup: $_")
            }
            
            # Delete the value from startup key
            Remove-ItemProperty -Path $regPath -Name $Item.Name -ErrorAction Stop
            $this.Log("Deleted registry value: $($Item.Name)")
            
            return $true
        }
        catch [System.Management.Automation.ItemNotFoundException] {
            $this.LogWarning("Registry value not found: $($Item.Name)")
            return $true  # Already disabled
        }
        catch {
            $this.LogError("Failed to disable registry item: $_")
            throw
        }
    }
    
    # Disable folder item
    [bool] DisableFolderItem([StartupItem]$Item) {
        $filePath = $Item.Command
        
        if (-not (Test-Path $filePath)) {
            $this.LogWarning("Startup file not found: $filePath")
            return $true  # Already disabled
        }
        
        # Rename the file to disable it
        $disabledPath = "$filePath.disabled"
        
        try {
            Move-Item -Path $filePath -Destination $disabledPath -Force
            $this.Log("Renamed $filePath to $disabledPath")
            return $true
        }
        catch {
            $this.LogError("Failed to rename file: $_")
            throw
        }
    }
    
    # Disable scheduled task
    [bool] DisableScheduledTask([StartupItem]$Item) {
        try {
            $result = schtasks /change /tn $Item.Name /disable 2>&1
            
            if ($LASTEXITCODE -eq 0) {
                $this.Log("Disabled scheduled task: $($Item.Name)")
                return $true
            }
            else {
                throw "schtasks returned error code $LASTEXITCODE : $result"
            }
        }
        catch {
            $this.LogError("Failed to disable task: $_")
            throw [SafetyError]::new("Failed to disable scheduled task: $_")
        }
    }
    
    # Enable a startup item
    [bool] EnableStartupItem([StartupItem]$Item) {
        if ($this.DryRun) {
            $this.Log("DRY RUN: Would enable $($Item.Name)")
            return $true
        }
        
        if ($Item.Enabled) {
            $this.LogWarning("Item $($Item.Name) is already enabled")
            return $true
        }
        
        $this.Log("Enabling startup item: $($Item.Name)")
        
        try {
            switch ($Item.Location) {
                { $_ -in @([StartupLocation]::REGISTRY_HKLM_RUN,
                           [StartupLocation]::REGISTRY_HKCU_RUN,
                           [StartupLocation]::REGISTRY_HKLM_RUN_ONCE,
                           [StartupLocation]::REGISTRY_HKCU_RUN_ONCE) } {
                    return $this.EnableRegistryItem($Item)
                }
                { $_ -in @([StartupLocation]::STARTUP_FOLDER_USER,
                           [StartupLocation]::STARTUP_FOLDER_COMMON) } {
                    return $this.EnableFolderItem($Item)
                }
                ([StartupLocation]::TASK_SCHEDULER) {
                    return $this.EnableScheduledTask($Item)
                }
                default {
                    throw "Enable not yet implemented for $($Item.Location)"
                }
            }
        }
        catch {
            $this.LogError("Failed to enable $($Item.Name): $_")
            throw [SafetyError]::new("Failed to enable startup item: $_")
        }
    }
    
    # Enable registry item
    [bool] EnableRegistryItem([StartupItem]$Item) {
        # Try to restore from backup
        $regPath = $this.GetRegistryPath($Item.Location)
        $backupPath = $regPath -replace 'CurrentVersion\\', 'CurrentVersion\Better11Backup\'
        
        try {
            if (Test-Path $backupPath) {
                $backupKey = Get-Item -Path $backupPath
                $value = $backupKey.GetValue($Item.Name, $null)
                
                if ($value) {
                    Set-ItemProperty -Path $regPath -Name $Item.Name -Value $value -Type String
                    $this.Log("Restored $($Item.Name) from backup")
                    
                    # Remove from backup
                    Remove-ItemProperty -Path $backupPath -Name $Item.Name -ErrorAction SilentlyContinue
                    
                    return $true
                }
            }
            
            $this.LogWarning("Registry item restoration not fully implemented. Item must be manually added back.")
            return $false
        }
        catch {
            $this.LogError("Failed to enable registry item: $_")
            throw
        }
    }
    
    # Enable folder item
    [bool] EnableFolderItem([StartupItem]$Item) {
        $disabledPath = "$($Item.Command).disabled"
        
        if (-not (Test-Path $disabledPath)) {
            $this.LogWarning("Disabled file not found: $disabledPath")
            return $false
        }
        
        try {
            Move-Item -Path $disabledPath -Destination $Item.Command -Force
            $this.Log("Renamed $disabledPath to $($Item.Command)")
            return $true
        }
        catch {
            $this.LogError("Failed to rename file: $_")
            throw
        }
    }
    
    # Enable scheduled task
    [bool] EnableScheduledTask([StartupItem]$Item) {
        try {
            $result = schtasks /change /tn $Item.Name /enable 2>&1
            
            if ($LASTEXITCODE -eq 0) {
                $this.Log("Enabled scheduled task: $($Item.Name)")
                return $true
            }
            else {
                throw "schtasks returned error code $LASTEXITCODE : $result"
            }
        }
        catch {
            $this.LogError("Failed to enable task: $_")
            throw [SafetyError]::new("Failed to enable scheduled task: $_")
        }
    }
    
    # Remove a startup item permanently
    [bool] RemoveStartupItem([StartupItem]$Item) {
        if ($this.DryRun) {
            $this.Log("DRY RUN: Would remove $($Item.Name)")
            return $true
        }
        
        $this.Log("Removing startup item: $($Item.Name)")
        
        try {
            switch ($Item.Location) {
                { $_ -in @([StartupLocation]::REGISTRY_HKLM_RUN,
                           [StartupLocation]::REGISTRY_HKCU_RUN,
                           [StartupLocation]::REGISTRY_HKLM_RUN_ONCE,
                           [StartupLocation]::REGISTRY_HKCU_RUN_ONCE) } {
                    return $this.RemoveRegistryItem($Item)
                }
                { $_ -in @([StartupLocation]::STARTUP_FOLDER_USER,
                           [StartupLocation]::STARTUP_FOLDER_COMMON) } {
                    return $this.RemoveFolderItem($Item)
                }
                ([StartupLocation]::TASK_SCHEDULER) {
                    return $this.RemoveScheduledTask($Item)
                }
                default {
                    throw "Remove not yet implemented for $($Item.Location)"
                }
            }
        }
        catch {
            $this.LogError("Failed to remove $($Item.Name): $_")
            throw [SafetyError]::new("Failed to remove startup item: $_")
        }
    }
    
    # Remove registry item
    [bool] RemoveRegistryItem([StartupItem]$Item) {
        $regPath = $this.GetRegistryPath($Item.Location)
        
        try {
            Remove-ItemProperty -Path $regPath -Name $Item.Name -ErrorAction Stop
            $this.Log("Permanently deleted registry value: $($Item.Name)")
            return $true
        }
        catch [System.Management.Automation.ItemNotFoundException] {
            $this.LogWarning("Registry value not found: $($Item.Name)")
            return $true  # Already removed
        }
        catch {
            $this.LogError("Failed to remove registry item: $_")
            throw
        }
    }
    
    # Remove folder item
    [bool] RemoveFolderItem([StartupItem]$Item) {
        $filePath = $Item.Command
        
        if (-not (Test-Path $filePath)) {
            $this.LogWarning("Startup file not found: $filePath")
            return $true  # Already removed
        }
        
        try {
            Remove-Item -Path $filePath -Force
            $this.Log("Permanently deleted file: $filePath")
            return $true
        }
        catch {
            $this.LogError("Failed to delete file: $_")
            throw
        }
    }
    
    # Remove scheduled task
    [bool] RemoveScheduledTask([StartupItem]$Item) {
        try {
            $result = schtasks /delete /tn $Item.Name /f 2>&1
            
            if ($LASTEXITCODE -eq 0) {
                $this.Log("Permanently deleted scheduled task: $($Item.Name)")
                return $true
            }
            else {
                throw "schtasks returned error code $LASTEXITCODE : $result"
            }
        }
        catch {
            $this.LogError("Failed to delete task: $_")
            throw [SafetyError]::new("Failed to delete scheduled task: $_")
        }
    }
    
    # Get boot time estimate
    [double] GetBootTimeEstimate() {
        $items = $this.ListStartupItems()
        $enabledCount = ($items | Where-Object { $_.Enabled }).Count
        
        # Heuristic: 0.5s base + 0.2s per enabled item
        $estimate = 0.5 + ($enabledCount * 0.2)
        
        return $estimate
    }
    
    # Get recommendations
    [string[]] GetRecommendations() {
        $items = $this.ListStartupItems()
        $recommendations = [System.Collections.Generic.List[string]]::new()
        
        $enabled = $items | Where-Object { $_.Enabled }
        $enabledCount = $enabled.Count
        
        if ($enabledCount -gt 15) {
            $recommendations.Add("You have $enabledCount startup items. Consider disabling unnecessary items.")
        }
        
        $highImpact = $enabled | Where-Object { $_.Impact -eq [StartupImpact]::HIGH }
        if ($highImpact.Count -gt 0) {
            $recommendations.Add("$($highImpact.Count) high-impact items detected. Review these for optimization.")
        }
        
        if ($enabledCount -gt 20) {
            $recommendations.Add("CRITICAL: Too many startup items ($enabledCount). This significantly impacts boot time.")
        }
        
        return $recommendations.ToArray()
    }
    
    # Helper: Get registry path for location
    [string] GetRegistryPath([StartupLocation]$Location) {
        $mapping = @{
            [StartupLocation]::REGISTRY_HKLM_RUN = 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run'
            [StartupLocation]::REGISTRY_HKCU_RUN = 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run'
            [StartupLocation]::REGISTRY_HKLM_RUN_ONCE = 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce'
            [StartupLocation]::REGISTRY_HKCU_RUN_ONCE = 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce'
        }
        
        return $mapping[$Location]
    }
}

# Convenience functions
function Get-StartupItems {
    <#
    .SYNOPSIS
        Get all startup items
    
    .EXAMPLE
        $items = Get-StartupItems
        $items | Format-Table Name, Location, Enabled
    #>
    [CmdletBinding()]
    [OutputType([StartupItem[]])]
    param()
    
    $manager = [StartupManager]::new()
    return $manager.ListStartupItems()
}

function Disable-StartupItem {
    <#
    .SYNOPSIS
        Disable a startup item
    
    .PARAMETER Item
        The startup item to disable
    
    .PARAMETER Name
        Name of the startup item to disable
    
    .EXAMPLE
        $items = Get-StartupItems
        $item = $items | Where-Object { $_.Name -eq 'Spotify' }
        Disable-StartupItem -Item $item
    
    .EXAMPLE
        Disable-StartupItem -Name 'Spotify'
    #>
    [CmdletBinding(SupportsShouldProcess=$true)]
    param(
        [Parameter(Mandatory=$true, ParameterSetName='Item', ValueFromPipeline=$true)]
        [StartupItem]$Item,
        
        [Parameter(Mandatory=$true, ParameterSetName='Name')]
        [string]$Name
    )
    
    process {
        if ($PSCmdlet.ParameterSetName -eq 'Name') {
            $manager = [StartupManager]::new()
            $items = $manager.ListStartupItems()
            $Item = $items | Where-Object { $_.Name -eq $Name } | Select-Object -First 1
            
            if (-not $Item) {
                throw "Startup item not found: $Name"
            }
        }
        
        if ($PSCmdlet.ShouldProcess($Item.Name, "Disable startup item")) {
            $manager = [StartupManager]::new()
            return $manager.DisableStartupItem($Item)
        }
    }
}

function Enable-StartupItem {
    <#
    .SYNOPSIS
        Enable a startup item
    
    .PARAMETER Item
        The startup item to enable
    
    .PARAMETER Name
        Name of the startup item to enable
    
    .EXAMPLE
        Enable-StartupItem -Name 'Spotify'
    #>
    [CmdletBinding(SupportsShouldProcess=$true)]
    param(
        [Parameter(Mandatory=$true, ParameterSetName='Item', ValueFromPipeline=$true)]
        [StartupItem]$Item,
        
        [Parameter(Mandatory=$true, ParameterSetName='Name')]
        [string]$Name
    )
    
    process {
        if ($PSCmdlet.ParameterSetName -eq 'Name') {
            $manager = [StartupManager]::new()
            $items = $manager.ListStartupItems()
            $Item = $items | Where-Object { $_.Name -eq $Name } | Select-Object -First 1
            
            if (-not $Item) {
                throw "Startup item not found: $Name"
            }
        }
        
        if ($PSCmdlet.ShouldProcess($Item.Name, "Enable startup item")) {
            $manager = [StartupManager]::new()
            return $manager.EnableStartupItem($Item)
        }
    }
}

function Remove-StartupItem {
    <#
    .SYNOPSIS
        Permanently remove a startup item
    
    .PARAMETER Item
        The startup item to remove
    
    .PARAMETER Name
        Name of the startup item to remove
    
    .EXAMPLE
        Remove-StartupItem -Name 'OldApp' -Confirm:$false
    #>
    [CmdletBinding(SupportsShouldProcess=$true, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory=$true, ParameterSetName='Item', ValueFromPipeline=$true)]
        [StartupItem]$Item,
        
        [Parameter(Mandatory=$true, ParameterSetName='Name')]
        [string]$Name
    )
    
    process {
        if ($PSCmdlet.ParameterSetName -eq 'Name') {
            $manager = [StartupManager]::new()
            $items = $manager.ListStartupItems()
            $Item = $items | Where-Object { $_.Name -eq $Name } | Select-Object -First 1
            
            if (-not $Item) {
                throw "Startup item not found: $Name"
            }
        }
        
        if ($PSCmdlet.ShouldProcess($Item.Name, "PERMANENTLY remove startup item")) {
            $manager = [StartupManager]::new()
            return $manager.RemoveStartupItem($Item)
        }
    }
}

# Export members
Export-ModuleMember -Function Get-StartupItems, Disable-StartupItem, Enable-StartupItem, Remove-StartupItem
