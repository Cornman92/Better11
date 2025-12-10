function Invoke-Better11Installer {
    <#
    .SYNOPSIS
        Executes an installer with appropriate arguments.
    
    .DESCRIPTION
        Internal function to run MSI, EXE, or AppX installers with silent arguments.
    
    .PARAMETER App
        Application metadata object.
    
    .PARAMETER InstallerPath
        Path to the installer file.
    
    .OUTPUTS
        PSCustomObject
        Installation result with exit code and output.
    #>
    
    [CmdletBinding()]
    [OutputType([PSCustomObject])]
    param(
        [Parameter(Mandatory = $true)]
        [PSCustomObject]$App,
        
        [Parameter(Mandatory = $true)]
        [string]$InstallerPath
    )
    
    process {
        try {
            $exitCode = 0
            $output = ""
            
            switch ($App.InstallerType.ToLower()) {
                'msi' {
                    Write-Verbose "Installing MSI package: $InstallerPath"
                    $arguments = @('/i', "`"$InstallerPath`"", '/qn', '/norestart')
                    $process = Start-Process -FilePath 'msiexec.exe' -ArgumentList $arguments -Wait -PassThru -NoNewWindow
                    $exitCode = $process.ExitCode
                }
                
                'exe' {
                    Write-Verbose "Installing EXE package: $InstallerPath"
                    $arguments = if ($App.SilentArgs -and $App.SilentArgs.Count -gt 0) {
                        $App.SilentArgs
                    } else {
                        @('/S', '/VERYSILENT', '/NORESTART')
                    }
                    $process = Start-Process -FilePath $InstallerPath -ArgumentList $arguments -Wait -PassThru -NoNewWindow
                    $exitCode = $process.ExitCode
                }
                
                'appx' {
                    Write-Verbose "Installing AppX package: $InstallerPath"
                    Add-AppxPackage -Path $InstallerPath -ErrorAction Stop
                    $exitCode = 0
                }
                
                default {
                    throw "Unsupported installer type: $($App.InstallerType)"
                }
            }
            
            $success = ($exitCode -eq 0) -or ($exitCode -eq 3010) # 0 = success, 3010 = success with restart required
            
            return [PSCustomObject]@{
                Success = $success
                ExitCode = $exitCode
                Output = $output
                RestartRequired = ($exitCode -eq 3010)
            }
        }
        catch {
            Write-Better11Log -Message "Installer execution failed: $_" -Level Error
            
            return [PSCustomObject]@{
                Success = $false
                ExitCode = -1
                Output = $_.Exception.Message
                RestartRequired = $false
            }
        }
    }
}
