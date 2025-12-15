function Get-Better11StartupPrograms {
    <#
    .SYNOPSIS
        Gets startup programs.
    .DESCRIPTION
        Lists all programs configured to run at Windows startup.
    .PARAMETER Scope
        CurrentUser, AllUsers, or All.
    .EXAMPLE
        Get-Better11StartupPrograms
        Get-Better11StartupPrograms -Scope CurrentUser
    #>
    [CmdletBinding()]
    param(
        [Parameter()]
        [ValidateSet('CurrentUser', 'AllUsers', 'All')]
        [string]$Scope = 'All'
    )

    try {
        $Results = @()
        
        # Registry-based startup items
        $RegistryItems = @()
        
        if ($Scope -in @('CurrentUser', 'All')) {
            $Path = $script:StartupRegistryPaths.CurrentUserRun
            if (Test-Path $Path) {
                $Props = Get-ItemProperty -Path $Path
                $Props.PSObject.Properties | Where-Object { $_.Name -notmatch '^PS' } | ForEach-Object {
                    $RegistryItems += [PSCustomObject]@{
                        Name = $_.Name
                        Command = $_.Value
                        Location = 'Registry'
                        RegistryPath = $Path
                        Scope = 'CurrentUser'
                        Enabled = $true
                        Type = 'Run'
                    }
                }
            }
        }
        
        if ($Scope -in @('AllUsers', 'All')) {
            $Path = $script:StartupRegistryPaths.LocalMachineRun
            if (Test-Path $Path) {
                $Props = Get-ItemProperty -Path $Path
                $Props.PSObject.Properties | Where-Object { $_.Name -notmatch '^PS' } | ForEach-Object {
                    $RegistryItems += [PSCustomObject]@{
                        Name = $_.Name
                        Command = $_.Value
                        Location = 'Registry'
                        RegistryPath = $Path
                        Scope = 'AllUsers'
                        Enabled = $true
                        Type = 'Run'
                    }
                }
            }
        }
        
        $Results += $RegistryItems
        
        # Folder-based startup items
        $FolderItems = @()
        
        if ($Scope -in @('CurrentUser', 'All') -and (Test-Path $script:StartupFolders.CurrentUser)) {
            Get-ChildItem -Path $script:StartupFolders.CurrentUser -File | ForEach-Object {
                $FolderItems += [PSCustomObject]@{
                    Name = $_.BaseName
                    Command = $_.FullName
                    Location = 'StartupFolder'
                    RegistryPath = $null
                    Scope = 'CurrentUser'
                    Enabled = $true
                    Type = 'Shortcut'
                }
            }
        }
        
        if ($Scope -in @('AllUsers', 'All') -and (Test-Path $script:StartupFolders.AllUsers)) {
            Get-ChildItem -Path $script:StartupFolders.AllUsers -File | ForEach-Object {
                $FolderItems += [PSCustomObject]@{
                    Name = $_.BaseName
                    Command = $_.FullName
                    Location = 'StartupFolder'
                    RegistryPath = $null
                    Scope = 'AllUsers'
                    Enabled = $true
                    Type = 'Shortcut'
                }
            }
        }
        
        $Results += $FolderItems
        
        return $Results
    }
    catch {
        Write-Error "Failed to get startup programs: $_"
        return @()
    }
}
