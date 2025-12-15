function Test-Better11Administrator {
    <#
    .SYNOPSIS
        Tests if the current session has administrator privileges.
    .DESCRIPTION
        Checks whether the current PowerShell session is running with elevated privileges.
    .EXAMPLE
        if (Test-Better11Administrator) { "Running as admin" }
    #>
    [CmdletBinding()]
    [OutputType([bool])]
    param()

    try {
        $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
        $principal = New-Object Security.Principal.WindowsPrincipal($identity)
        return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    }
    catch {
        Write-Warning "Failed to check administrator status: $_"
        return $false
    }
}
