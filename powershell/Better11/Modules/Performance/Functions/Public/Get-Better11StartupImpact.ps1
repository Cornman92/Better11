function Get-Better11StartupImpact {
    <#
    .SYNOPSIS
        Analyzes the impact of startup programs on boot time.
    
    .DESCRIPTION
        Evaluates startup programs and their estimated impact on system boot time.
    
    .EXAMPLE
        Get-Better11StartupImpact
    #>
    [CmdletBinding()]
    param()
    
    try {
        $StartupItems = @()
        
        # Registry startup items
        $StartupLocations = @(
            'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run',
            'HKLM:\Software\Microsoft\Windows\CurrentVersion\Run',
            'HKCU:\Software\Microsoft\Windows\CurrentVersion\RunOnce',
            'HKLM:\Software\Microsoft\Windows\CurrentVersion\RunOnce'
        )
        
        foreach ($Location in $StartupLocations) {
            if (Test-Path $Location) {
                $Items = Get-ItemProperty -Path $Location
                $Items.PSObject.Properties | Where-Object { $_.Name -notmatch '^PS' } | ForEach-Object {
                    $StartupItems += [PSCustomObject]@{
                        Name = $_.Name
                        Command = $_.Value
                        Location = $Location
                        Type = 'Registry'
                        EstimatedImpact = 'Medium'  # Simplified estimation
                    }
                }
            }
        }
        
        # Startup folder items
        $StartupFolders = @(
            "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup",
            "$env:ALLUSERSPROFILE\Microsoft\Windows\Start Menu\Programs\Startup"
        )
        
        foreach ($Folder in $StartupFolders) {
            if (Test-Path $Folder) {
                Get-ChildItem -Path $Folder | ForEach-Object {
                    $StartupItems += [PSCustomObject]@{
                        Name = $_.Name
                        Command = $_.FullName
                        Location = $Folder
                        Type = 'Shortcut'
                        EstimatedImpact = 'Low'
                    }
                }
            }
        }
        
        # Scheduled tasks that run at startup
        $Tasks = Get-ScheduledTask | Where-Object { $_.Settings.Enabled -and $_.Triggers.TriggerAt -like '*Startup*' }
        foreach ($Task in $Tasks) {
            $StartupItems += [PSCustomObject]@{
                Name = $Task.TaskName
                Command = $Task.Actions[0].Execute
                Location = 'Task Scheduler'
                Type = 'ScheduledTask'
                EstimatedImpact = 'Low'
            }
        }
        
        Write-Better11Log -Message "Found $($StartupItems.Count) startup items" -Level Info
        
        return $StartupItems | Sort-Object EstimatedImpact -Descending
    }
    catch {
        Write-Better11Log -Message "Failed to get startup impact: $_" -Level Error
        throw
    }
}
