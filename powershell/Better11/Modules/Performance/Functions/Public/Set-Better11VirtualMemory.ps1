function Set-Better11VirtualMemory {
    <#
    .SYNOPSIS
        Configures virtual memory settings.
    .DESCRIPTION
        Sets page file size or enables system-managed virtual memory.
    .PARAMETER SystemManaged
        Let Windows manage the page file.
    .PARAMETER InitialSizeMB
        Initial page file size in MB.
    .PARAMETER MaximumSizeMB
        Maximum page file size in MB.
    .PARAMETER Drive
        Drive letter for the page file.
    .EXAMPLE
        Set-Better11VirtualMemory -SystemManaged
        Set-Better11VirtualMemory -InitialSizeMB 4096 -MaximumSizeMB 8192 -Drive "C"
    #>
    [CmdletBinding()]
    param(
        [Parameter(ParameterSetName = 'Managed')]
        [switch]$SystemManaged,
        
        [Parameter(ParameterSetName = 'Custom', Mandatory = $true)]
        [int]$InitialSizeMB,
        
        [Parameter(ParameterSetName = 'Custom', Mandatory = $true)]
        [int]$MaximumSizeMB,
        
        [Parameter(ParameterSetName = 'Custom')]
        [string]$Drive = 'C'
    )

    try {
        if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
            throw "Administrator privileges required"
        }
        
        $RegPath = 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management'
        
        if ($SystemManaged) {
            # Enable automatic page file management
            $ComputerSystem = Get-WmiObject Win32_ComputerSystem -EnableAllPrivileges
            $ComputerSystem.AutomaticManagedPagefile = $true
            $ComputerSystem.Put() | Out-Null
            
            return [PSCustomObject]@{
                Success = $true
                Mode = 'SystemManaged'
                Message = 'Virtual memory set to system managed. Restart required.'
            }
        }
        else {
            # Disable automatic management
            $ComputerSystem = Get-WmiObject Win32_ComputerSystem -EnableAllPrivileges
            $ComputerSystem.AutomaticManagedPagefile = $false
            $ComputerSystem.Put() | Out-Null
            
            # Set custom page file
            $PageFile = Get-WmiObject Win32_PageFileSetting -Filter "Name='$Drive:\\pagefile.sys'" -ErrorAction SilentlyContinue
            
            if (-not $PageFile) {
                # Create new page file setting
                $PageFile = ([WmiClass]"Win32_PageFileSetting").CreateInstance()
                $PageFile.Name = "$Drive`:\pagefile.sys"
            }
            
            $PageFile.InitialSize = $InitialSizeMB
            $PageFile.MaximumSize = $MaximumSizeMB
            $PageFile.Put() | Out-Null
            
            return [PSCustomObject]@{
                Success = $true
                Mode = 'Custom'
                Drive = $Drive
                InitialSizeMB = $InitialSizeMB
                MaximumSizeMB = $MaximumSizeMB
                Message = 'Virtual memory configured. Restart required.'
            }
        }
    }
    catch {
        Write-Error "Failed to set virtual memory: $_"
        return [PSCustomObject]@{ Success = $false; Error = $_.Exception.Message }
    }
}
