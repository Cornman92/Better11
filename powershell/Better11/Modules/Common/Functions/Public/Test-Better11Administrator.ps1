function Test-Better11Administrator {
    <#
    .SYNOPSIS
        Checks if the current PowerShell session is running with administrator privileges.
    
    .DESCRIPTION
        Returns true if the current user has administrator rights, false otherwise.
        Essential for operations that require elevated permissions.
    
    .EXAMPLE
        if (-not (Test-Better11Administrator)) {
            throw "This operation requires administrator privileges"
        }
    
    .OUTPUTS
        Boolean
        Returns $true if running as administrator, $false otherwise.
    #>
    
    [CmdletBinding()]
    [OutputType([bool])]
    param()
    
    process {
        try {
            $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
            $principal = New-Object Security.Principal.WindowsPrincipal($identity)
            $isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
            
            Write-Verbose "Administrator check: $isAdmin"
            return $isAdmin
        }
        catch {
            Write-Better11Log -Message "Failed to check administrator status: $_" -Level Error
            return $false
        }
    }
}
