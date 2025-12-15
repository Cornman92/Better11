function Disable-Better11StartupProgram {
    <#
    .SYNOPSIS
        Disables a startup program.
    .DESCRIPTION
        Disables a startup program without removing it.
    .PARAMETER Name
        The startup program name.
    .PARAMETER Scope
        CurrentUser or AllUsers.
    .EXAMPLE
        Disable-Better11StartupProgram -Name "OneDrive" -Scope CurrentUser
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
        
        $ApprovedPath = if ($Scope -eq 'CurrentUser') {
            'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run'
        } else {
            'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run'
        }
        
        # Create path if not exists
        if (-not (Test-Path $ApprovedPath)) {
            New-Item -Path $ApprovedPath -Force | Out-Null
        }
        
        # Disable: set first bytes to 03 (disabled)
        $DisabledBytes = [byte[]](0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)
        Set-ItemProperty -Path $ApprovedPath -Name $Name -Value $DisabledBytes -Type Binary
        
        return [PSCustomObject]@{
            Success = $true
            Name = $Name
            Scope = $Scope
            State = 'Disabled'
        }
    }
    catch {
        Write-Error "Failed to disable startup program: $_"
        return [PSCustomObject]@{ Success = $false; Name = $Name; Error = $_.Exception.Message }
    }
}
