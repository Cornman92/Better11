<#
.SYNOPSIS
    Safety utilities for system tools.

.DESCRIPTION
    Provides safety checks, confirmations, and backup functionality
    for system modification operations.
#>

# Custom exception for safety errors
class SafetyError : System.Exception {
    SafetyError([string]$Message) : base($Message) {}
}

function Test-WindowsPlatform {
    <#
    .SYNOPSIS
        Ensure the current platform is Windows
    
    .DESCRIPTION
        Throws SafetyError if not running on Windows
    
    .EXAMPLE
        Test-WindowsPlatform
    #>
    [CmdletBinding()]
    param()
    
    if ($PSVersionTable.Platform -and $PSVersionTable.Platform -ne 'Win32NT') {
        throw [SafetyError]::new("Windows platform is required for this operation")
    }
    
    if (-not $IsWindows -and $null -ne $IsWindows) {
        throw [SafetyError]::new("Windows platform is required for this operation")
    }
}

function Confirm-Action {
    <#
    .SYNOPSIS
        Prompt the user to confirm a sensitive action
    
    .PARAMETER Prompt
        The message shown to the user
    
    .PARAMETER DefaultYes
        If true, default answer is Yes
    
    .EXAMPLE
        if (Confirm-Action "Delete all files?") {
            Remove-Item *
        }
    
    .OUTPUTS
        bool - True if user confirmed
    #>
    [CmdletBinding()]
    [OutputType([bool])]
    param(
        [Parameter(Mandatory=$true)]
        [string]$Prompt,
        
        [switch]$DefaultYes
    )
    
    $choice = if ($DefaultYes) { '[Y/n]' } else { '[y/N]' }
    $response = Read-Host "$Prompt $choice"
    $response = $response.Trim().ToLower()
    
    $confirmed = $response -in @('y', 'yes')
    
    if ($confirmed) {
        Write-Verbose "User confirmed action: $Prompt"
    }
    else {
        Write-Warning "User cancelled action: $Prompt"
    }
    
    return $confirmed
}

function New-SystemRestorePoint {
    <#
    .SYNOPSIS
        Create a system restore point
    
    .PARAMETER Description
        Description for the restore point
    
    .PARAMETER RestorePointType
        Type of restore point (default: MODIFY_SETTINGS)
    
    .EXAMPLE
        New-SystemRestorePoint -Description "Before Better11 changes"
    
    .NOTES
        Requires administrator privileges
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory=$true)]
        [string]$Description,
        
        [ValidateSet('APPLICATION_INSTALL', 'APPLICATION_UNINSTALL', 'DEVICE_DRIVER_INSTALL', 
                     'MODIFY_SETTINGS', 'CANCELLED_OPERATION')]
        [string]$RestorePointType = 'MODIFY_SETTINGS'
    )
    
    Test-WindowsPlatform
    
    try {
        Write-Verbose "Creating restore point: $Description"
        
        # Check if System Restore is enabled
        $srStatus = Get-ComputerRestorePoint -ErrorAction SilentlyContinue
        if ($null -eq $srStatus -and (Get-Command Enable-ComputerRestore -ErrorAction SilentlyContinue)) {
            Write-Warning "System Restore might not be enabled"
        }
        
        # Create the restore point
        Checkpoint-Computer -Description $Description -RestorePointType $RestorePointType -ErrorAction Stop
        
        Write-Verbose "Restore point created successfully"
    }
    catch {
        Write-Error "Failed to create restore point: $_"
        throw [SafetyError]::new("Unable to create system restore point: $_")
    }
}

function Backup-RegistryKey {
    <#
    .SYNOPSIS
        Export a registry key to a file
    
    .PARAMETER KeyPath
        Path of the registry key (e.g., 'HKCU:\Software\MyApp')
    
    .PARAMETER Destination
        Destination file path (optional, creates temp file if not specified)
    
    .EXAMPLE
        $backup = Backup-RegistryKey -KeyPath 'HKCU:\Software\Better11'
        
    .EXAMPLE
        Backup-RegistryKey -KeyPath 'HKLM:\Software\Better11' -Destination 'C:\Backups\reg.reg'
    
    .OUTPUTS
        String - Path to backup file
    #>
    [CmdletBinding()]
    [OutputType([string])]
    param(
        [Parameter(Mandatory=$true)]
        [string]$KeyPath,
        
        [string]$Destination
    )
    
    Test-WindowsPlatform
    
    # Create temp file if destination not specified
    if (-not $Destination) {
        $Destination = [System.IO.Path]::GetTempFileName()
        $Destination = [System.IO.Path]::ChangeExtension($Destination, '.reg')
    }
    
    try {
        Write-Verbose "Backing up registry key $KeyPath to $Destination"
        
        # Convert PowerShell path to reg.exe format
        $regPath = $KeyPath -replace 'HKCU:\\', 'HKEY_CURRENT_USER\' `
                            -replace 'HKLM:\\', 'HKEY_LOCAL_MACHINE\' `
                            -replace 'HKCR:\\', 'HKEY_CLASSES_ROOT\' `
                            -replace 'HKU:\\', 'HKEY_USERS\' `
                            -replace 'HKCC:\\', 'HKEY_CURRENT_CONFIG\'
        
        # Use reg.exe for export
        $process = Start-Process -FilePath 'reg.exe' `
                                 -ArgumentList "export `"$regPath`" `"$Destination`" /y" `
                                 -Wait `
                                 -NoNewWindow `
                                 -PassThru
        
        if ($process.ExitCode -ne 0) {
            throw "reg.exe returned exit code $($process.ExitCode)"
        }
        
        Write-Verbose "Registry backup successful"
        return $Destination
    }
    catch {
        Write-Error "Registry backup failed for ${KeyPath}: $_"
        throw [SafetyError]::new("Unable to back up registry key ${KeyPath}: $_")
    }
}

function Restore-RegistryKey {
    <#
    .SYNOPSIS
        Restore a registry key from a backup file
    
    .PARAMETER BackupPath
        Path to the .reg backup file
    
    .EXAMPLE
        Restore-RegistryKey -BackupPath 'C:\Backups\registry.reg'
    
    .NOTES
        Requires administrator privileges for system keys
    #>
    [CmdletBinding(SupportsShouldProcess=$true, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory=$true)]
        [ValidateScript({Test-Path $_})]
        [string]$BackupPath
    )
    
    Test-WindowsPlatform
    
    if ($PSCmdlet.ShouldProcess($BackupPath, "Restore registry from backup")) {
        try {
            Write-Verbose "Restoring registry from $BackupPath"
            
            # Use reg.exe for import
            $process = Start-Process -FilePath 'reg.exe' `
                                     -ArgumentList "import `"$BackupPath`"" `
                                     -Wait `
                                     -NoNewWindow `
                                     -PassThru
            
            if ($process.ExitCode -ne 0) {
                throw "reg.exe returned exit code $($process.ExitCode)"
            }
            
            Write-Verbose "Registry restore successful"
        }
        catch {
            Write-Error "Registry restore failed: $_"
            throw [SafetyError]::new("Unable to restore registry from ${BackupPath}: $_")
        }
    }
}

function Test-AdminPrivileges {
    <#
    .SYNOPSIS
        Check if running with administrator privileges
    
    .EXAMPLE
        if (Test-AdminPrivileges) {
            Write-Host "Running as admin"
        }
    
    .OUTPUTS
        bool - True if running as administrator
    #>
    [CmdletBinding()]
    [OutputType([bool])]
    param()
    
    $currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    return $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Assert-AdminPrivileges {
    <#
    .SYNOPSIS
        Ensure running with administrator privileges
    
    .PARAMETER Message
        Custom error message
    
    .EXAMPLE
        Assert-AdminPrivileges
    
    .NOTES
        Throws SafetyError if not administrator
    #>
    [CmdletBinding()]
    param(
        [string]$Message = "This operation requires administrator privileges. Please run as administrator."
    )
    
    if (-not (Test-AdminPrivileges)) {
        throw [SafetyError]::new($Message)
    }
}

# Export functions and classes
Export-ModuleMember -Function * -Cmdlet *
