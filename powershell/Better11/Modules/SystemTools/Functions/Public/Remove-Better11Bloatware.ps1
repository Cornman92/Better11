function Remove-Better11Bloatware {
    <#
    .SYNOPSIS
        Removes bloatware package.

    .DESCRIPTION
        Removes a specific Appx package identified as bloatware.
        Requires administrative privileges.

    .PARAMETER PackageName
        Name or pattern of the package to remove.

    .EXAMPLE
        Remove-Better11Bloatware -PackageName "*Microsoft.3DBuilder*"
        Removes 3D Builder.
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory=$true)]
        [string]$PackageName
    )

    process {
        if (-not (Test-Better11Administrator)) {
            Write-Better11Log -Message "Administrator privileges required" -Level "ERROR"
            throw "Administrator privileges required"
        }

        if ($PSCmdlet.ShouldProcess($PackageName, "Remove Appx Package")) {
            Write-Better11Log -Message "Removing package '$PackageName'..." -Level "INFO"

            try {
                Get-AppxPackage -Name $PackageName -AllUsers | Remove-AppxPackage -AllUsers -ErrorAction Stop
                Get-AppxProvisionedPackage -Online | Where-Object {$_.DisplayName -like $PackageName} | Remove-AppxProvisionedPackage -Online -ErrorAction Stop
                
                Write-Better11Log -Message "Package removed successfully" -Level "SUCCESS"
            }
            catch {
                Write-Better11Log -Message "Failed to remove package: $_" -Level "ERROR"
                # Don't throw, just log error as some packages might not exist
            }
        }
    }
}
