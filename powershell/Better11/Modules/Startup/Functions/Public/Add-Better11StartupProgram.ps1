function Add-Better11StartupProgram {
    <#
    .SYNOPSIS
        Adds a new startup program.
    .DESCRIPTION
        Adds a program to run at Windows startup.
    .PARAMETER Name
        The entry name.
    .PARAMETER Command
        The command to execute.
    .PARAMETER Scope
        CurrentUser or AllUsers.
    .EXAMPLE
        Add-Better11StartupProgram -Name "MyApp" -Command "C:\MyApp\app.exe" -Scope CurrentUser
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,
        
        [Parameter(Mandatory = $true)]
        [string]$Command,
        
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
        
        Set-ItemProperty -Path $RegPath -Name $Name -Value $Command -Type String
        
        return [PSCustomObject]@{
            Success = $true
            Name = $Name
            Command = $Command
            Scope = $Scope
        }
    }
    catch {
        Write-Error "Failed to add startup program: $_"
        return [PSCustomObject]@{ Success = $false; Name = $Name; Error = $_.Exception.Message }
    }
}
