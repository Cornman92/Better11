function Remove-Better11StartupProgram {
    <#
    .SYNOPSIS
        Removes a startup program.
    .DESCRIPTION
        Removes a program from Windows startup.
    .PARAMETER Name
        The entry name.
    .PARAMETER Scope
        CurrentUser or AllUsers.
    .EXAMPLE
        Remove-Better11StartupProgram -Name "MyApp" -Scope CurrentUser
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,
        
        [Parameter()]
        [ValidateSet('CurrentUser', 'AllUsers')]
        [string]$Scope = 'CurrentUser'
    )

    try {
        if ($Scope -eq 'AllUsers') {
            if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
                throw "Administrator privileges required for AllUsers scope"
            }
        }
        
        $RegPath = if ($Scope -eq 'CurrentUser') {
            $script:StartupRegistryPaths.CurrentUserRun
        } else {
            $script:StartupRegistryPaths.LocalMachineRun
        }
        
        Remove-ItemProperty -Path $RegPath -Name $Name -ErrorAction Stop
        
        # Also remove from approval list if present
        $ApprovedPath = if ($Scope -eq 'CurrentUser') {
            'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run'
        } else {
            'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run'
        }
        
        if (Test-Path $ApprovedPath) {
            Remove-ItemProperty -Path $ApprovedPath -Name $Name -ErrorAction SilentlyContinue
        }
        
        return [PSCustomObject]@{
            Success = $true
            Name = $Name
            Scope = $Scope
            Message = 'Removed'
        }
    }
    catch {
        Write-Error "Failed to remove startup program: $_"
        return [PSCustomObject]@{ Success = $false; Name = $Name; Error = $_.Exception.Message }
    }
}
