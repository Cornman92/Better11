function Enable-Better11StartupProgram {
    <#
    .SYNOPSIS
        Enables a startup program.
    .DESCRIPTION
        Re-enables a previously disabled startup program.
    .PARAMETER Name
        The startup program name.
    .PARAMETER Scope
        CurrentUser or AllUsers.
    .EXAMPLE
        Enable-Better11StartupProgram -Name "OneDrive" -Scope CurrentUser
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
        # Check approved/disabled locations
        $ApprovedPath = if ($Scope -eq 'CurrentUser') {
            'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run'
        } else {
            'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run'
        }
        
        if (Test-Path $ApprovedPath) {
            $CurrentValue = Get-ItemProperty -Path $ApprovedPath -Name $Name -ErrorAction SilentlyContinue
            if ($CurrentValue) {
                # Enable: set first byte to 02 (enabled) or 06 (enabled)
                $EnabledBytes = [byte[]](0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00)
                Set-ItemProperty -Path $ApprovedPath -Name $Name -Value $EnabledBytes -Type Binary
                
                return [PSCustomObject]@{
                    Success = $true
                    Name = $Name
                    Scope = $Scope
                    State = 'Enabled'
                }
            }
        }
        
        return [PSCustomObject]@{
            Success = $false
            Name = $Name
            Scope = $Scope
            Error = 'Program not found in startup approval list'
        }
    }
    catch {
        Write-Error "Failed to enable startup program: $_"
        return [PSCustomObject]@{ Success = $false; Name = $Name; Error = $_.Exception.Message }
    }
}
