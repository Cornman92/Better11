function Install-Better11App {
    <#
    .SYNOPSIS
        Installs an application from the Better11 catalog.
    
    .DESCRIPTION
        Downloads, verifies, and installs an application along with its dependencies.
        Supports MSI, EXE, and AppX installers with automatic silent installation.
        Creates restore point and verifies signatures before installation.
    
    .PARAMETER AppId
        The unique identifier of the application to install.
    
    .PARAMETER Force
        Skip confirmation prompts.
    
    .PARAMETER SkipDependencies
        Do not automatically install dependencies.
    
    .PARAMETER DryRun
        Simulate installation without actually installing.
    
    .PARAMETER DownloadPath
        Custom download directory. Defaults to ~/.better11/downloads
    
    .EXAMPLE
        Install-Better11App -AppId "vscode"
        Installs Visual Studio Code with dependencies.
    
    .EXAMPLE
        Install-Better11App -AppId "chrome" -Force
        Installs Google Chrome without confirmation.
    
    .EXAMPLE
        Install-Better11App -AppId "firefox" -DryRun
        Simulates Firefox installation.
    
    .OUTPUTS
        PSCustomObject
        Installation result with status and details.
    #>
    
    [CmdletBinding(SupportsShouldProcess)]
    [OutputType([PSCustomObject])]
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$AppId,
        
        [Parameter()]
        [switch]$Force,
        
        [Parameter()]
        [switch]$SkipDependencies,
        
        [Parameter()]
        [switch]$DryRun,
        
        [Parameter()]
        [string]$DownloadPath = (Join-Path $env:USERPROFILE '.better11\downloads')
    )
    
    begin {
        Write-Better11Log -Message "Starting installation of $AppId" -Level Info
        
        # Check administrator privileges
        if (-not (Test-Better11Administrator)) {
            throw "Installation requires administrator privileges. Please run PowerShell as Administrator."
        }
        
        # Ensure download directory exists
        if (-not (Test-Path $DownloadPath)) {
            New-Item -Path $DownloadPath -ItemType Directory -Force | Out-Null
        }
    }
    
    process {
        try {
            # Get app metadata
            $app = Get-Better11Apps -AppId $AppId
            if (-not $app) {
                throw "Application not found: $AppId"
            }
            
            # Check if already installed
            if ($app.Installed -and -not $Force) {
                Write-Better11Log -Message "$AppId v$($app.InstalledVersion) is already installed" -Level Warning
                return [PSCustomObject]@{
                    Status = 'AlreadyInstalled'
                    AppId = $AppId
                    Version = $app.InstalledVersion
                    Success = $true
                }
            }
            
            # Confirm action
            if (-not $Force -and -not $DryRun) {
                $confirmed = Confirm-Better11Action -Prompt "Install $($app.Name) v$($app.Version)?"
                if (-not $confirmed) {
                    throw "Installation cancelled by user"
                }
            }
            
            # Create restore point
            if (-not $DryRun -and $PSCmdlet.ShouldProcess("System", "Create restore point")) {
                New-Better11RestorePoint -Description "Before installing $AppId" | Out-Null
            }
            
            # Install dependencies
            if (-not $SkipDependencies -and $app.Dependencies.Count -gt 0) {
                Write-Better11Log -Message "Installing $($app.Dependencies.Count) dependencies for $AppId" -Level Info
                foreach ($depId in $app.Dependencies) {
                    $depResult = Install-Better11App -AppId $depId -Force:$Force -DryRun:$DryRun
                    if (-not $depResult.Success) {
                        throw "Failed to install dependency: $depId"
                    }
                }
            }
            
            if ($DryRun) {
                Write-Better11Log -Message "[DRY RUN] Would install $AppId v$($app.Version)" -Level Info
                return [PSCustomObject]@{
                    Status = 'DryRun'
                    AppId = $AppId
                    Version = $app.Version
                    Success = $true
                }
            }
            
            # Download installer
            Write-Better11Log -Message "Downloading $($app.Name) from $($app.Uri)" -Level Info
            $installerFileName = [System.IO.Path]::GetFileName([Uri]::new($app.Uri).AbsolutePath)
            $installerPath = Join-Path $DownloadPath $installerFileName
            
            # Download file
            if ($PSCmdlet.ShouldProcess($installerPath, "Download installer")) {
                Invoke-WebRequest -Uri $app.Uri -OutFile $installerPath -UseBasicParsing
            }
            
            # Verify hash
            Write-Better11Log -Message "Verifying file hash..." -Level Info
            $hashResult = Verify-Better11FileHash -FilePath $installerPath -ExpectedHash $app.Sha256
            if (-not $hashResult.IsMatch) {
                Remove-Item $installerPath -Force
                throw "Hash verification failed. File may be corrupted or tampered with."
            }
            
            # Verify signature
            Write-Better11Log -Message "Verifying code signature..." -Level Info
            $sigResult = Test-Better11CodeSignature -FilePath $installerPath
            if (-not $sigResult.IsTrusted) {
                Write-Better11Log -Message "Warning: Installer signature is not trusted (Status: $($sigResult.Status))" -Level Warning
            }
            
            # Install
            Write-Better11Log -Message "Installing $($app.Name)..." -Level Info
            $installResult = Invoke-Better11Installer -App $app -InstallerPath $installerPath
            
            if ($installResult.Success) {
                # Update state
                Update-Better11InstallState -AppId $AppId -Version $app.Version -Installed $true -InstallerPath $installerPath
                
                Write-Better11Log -Message "Successfully installed $($app.Name) v$($app.Version)" -Level Info
                
                return [PSCustomObject]@{
                    Status = 'Success'
                    AppId = $AppId
                    Name = $app.Name
                    Version = $app.Version
                    Success = $true
                    ExitCode = $installResult.ExitCode
                    Output = $installResult.Output
                }
            }
            else {
                throw "Installation failed with exit code: $($installResult.ExitCode)"
            }
        }
        catch {
            Write-Better11Log -Message "Installation failed for ${AppId}: $_" -Level Error
            
            return [PSCustomObject]@{
                Status = 'Failed'
                AppId = $AppId
                Success = $false
                Error = $_.Exception.Message
            }
        }
    }
}
