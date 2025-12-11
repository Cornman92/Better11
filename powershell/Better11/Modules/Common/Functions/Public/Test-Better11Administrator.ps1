function Test-Better11Administrator {
    <#
    .SYNOPSIS
        Tests if the current session is running with administrator privileges.
    
    .DESCRIPTION
        Checks if the current PowerShell session is running as an administrator.
        This is required for many system-level operations.
    
    .EXAMPLE
        Test-Better11Administrator
        
        Returns True if running as administrator, False otherwise.
    
    .EXAMPLE
        if (-not (Test-Better11Administrator)) {
            throw "This script requires administrator privileges"
        }
    
    .OUTPUTS
        Boolean
        True if running as administrator, False otherwise
    #>
    
    [CmdletBinding()]
    [OutputType([bool])]
    param()
    
    process {
        try {
            $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
            $principal = New-Object Security.Principal.WindowsPrincipal($identity)
            $adminRole = [Security.Principal.WindowsBuiltInRole]::Administrator
            
            $isAdmin = $principal.IsInRole($adminRole)
            
            Write-Better11Log -Message "Administrator check: $isAdmin" -Level Debug
            
            return $isAdmin
        }
        catch {
            Write-Better11Log -Message "Failed to check administrator status: $_" -Level Error
            return $false
        }
    }
}
