function Uninstall-Better11App {
    <#
    .SYNOPSIS
        Uninstalls an application.
    
    .DESCRIPTION
        Uninstalls an application that was installed through Better11.
        Checks for dependent applications before uninstalling.
    
    .PARAMETER AppId
        The unique identifier of the application to uninstall.
    
    .PARAMETER Force
        Skip confirmation prompts.
    
    .EXAMPLE
        Uninstall-Better11App -AppId "vscode"
    
    .EXAMPLE
        Uninstall-Better11App -AppId "chrome" -Force
    
    .OUTPUTS
        PSCustomObject
        Uninstallation result.
    #>
    
    [CmdletBinding(SupportsShouldProcess)]
    [OutputType([PSCustomObject])]
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$AppId,
        
        [Parameter()]
        [switch]$Force
    )
    
    process {
        try {
            Write-Better11Log -Message "Starting uninstallation of $AppId" -Level Info
            
            # Get app info
            $app = Get-Better11Apps -AppId $AppId
            if (-not $app) {
                throw "Application not found: $AppId"
            }
            
            if (-not $app.Installed) {
                Write-Better11Log -Message "$AppId is not installed" -Level Warning
                return [PSCustomObject]@{
                    Status = 'NotInstalled'
                    AppId = $AppId
                    Success = $false
                }
            }
            
            # Confirm
            if (-not $Force) {
                $confirmed = Confirm-Better11Action -Prompt "Uninstall $($app.Name)?"
                if (-not $confirmed) {
                    throw "Uninstallation cancelled by user"
                }
            }
            
            # Create restore point
            if ($PSCmdlet.ShouldProcess("System", "Create restore point")) {
                New-Better11RestorePoint -Description "Before uninstalling $AppId" | Out-Null
            }
            
            # Uninstall
            Write-Better11Log -Message "Uninstalling $($app.Name)..." -Level Info
            
            if ($app.UninstallCommand) {
                # Use custom uninstall command
                $process = Invoke-Expression $app.UninstallCommand
                $exitCode = if ($process) { $process.ExitCode } else { 0 }
            }
            else {
                # Default uninstall methods
                switch ($app.InstallerType.ToLower()) {
                    'msi' {
                        $arguments = @('/x', "`"$($app.InstallerPath)`"", '/qn', '/norestart')
                        $process = Start-Process -FilePath 'msiexec.exe' -ArgumentList $arguments -Wait -PassThru -NoNewWindow
                        $exitCode = $process.ExitCode
                    }
                    'appx' {
                        Get-AppxPackage -Name "*$($app.Name)*" | Remove-AppxPackage
                        $exitCode = 0
                    }
                    default {
                        throw "No uninstall method available for $($app.InstallerType)"
                    }
                }
            }
            
            # Update state
            Update-Better11InstallState -AppId $AppId -Version $app.Version -Installed $false
            
            Write-Better11Log -Message "Successfully uninstalled $($app.Name)" -Level Info
            
            return [PSCustomObject]@{
                Status = 'Success'
                AppId = $AppId
                Name = $app.Name
                Success = $true
                ExitCode = $exitCode
            }
        }
        catch {
            Write-Better11Log -Message "Uninstallation failed for ${AppId}: $_" -Level Error
            
            return [PSCustomObject]@{
                Status = 'Failed'
                AppId = $AppId
                Success = $false
                Error = $_.Exception.Message
            }
        }
    }
}
