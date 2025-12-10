function Remove-Better11Bloatware {
    <#
    .SYNOPSIS
        Removes bloatware AppX packages from Windows.
    
    .DESCRIPTION
        Removes unwanted pre-installed AppX packages (bloatware) with safety checks.
        Creates restore point before removal.
    
    .PARAMETER Packages
        Array of package names or patterns to remove.
    
    .PARAMETER Force
        Skip confirmation prompts.
    
    .PARAMETER Preset
        Use a predefined bloatware removal preset (Minimal, Moderate, Aggressive).
    
    .EXAMPLE
        Remove-Better11Bloatware -Packages 'Microsoft.BingWeather', 'Microsoft.GetHelp'
    
    .EXAMPLE
        Remove-Better11Bloatware -Preset Moderate
    
    .OUTPUTS
        PSCustomObject
        Removal results.
    #>
    
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(ParameterSetName = 'Manual')]
        [string[]]$Packages,
        
        [Parameter()]
        [switch]$Force,
        
        [Parameter(ParameterSetName = 'Preset')]
        [ValidateSet('Minimal', 'Moderate', 'Aggressive')]
        [string]$Preset
    )
    
    begin {
        Write-Better11Log -Message "Starting bloatware removal" -Level Info
        
        if (-not (Test-Better11Administrator)) {
            throw "Bloatware removal requires administrator privileges"
        }
        
        # Bloatware presets
        $presets = @{
            Minimal = @(
                'Microsoft.BingWeather',
                'Microsoft.GetHelp',
                'Microsoft.Getstarted',
                'Microsoft.ZuneMusic',
                'Microsoft.ZuneVideo'
            )
            Moderate = @(
                'Microsoft.BingWeather',
                'Microsoft.GetHelp',
                'Microsoft.Getstarted',
                'Microsoft.ZuneMusic',
                'Microsoft.ZuneVideo',
                'Microsoft.BingNews',
                'Microsoft.MicrosoftSolitaireCollection',
                'Microsoft.People',
                'Microsoft.WindowsMaps',
                'Microsoft.WindowsFeedbackHub'
            )
            Aggressive = @(
                'Microsoft.BingWeather',
                'Microsoft.GetHelp',
                'Microsoft.Getstarted',
                'Microsoft.ZuneMusic',
                'Microsoft.ZuneVideo',
                'Microsoft.BingNews',
                'Microsoft.MicrosoftSolitaireCollection',
                'Microsoft.People',
                'Microsoft.WindowsMaps',
                'Microsoft.WindowsFeedbackHub',
                'Microsoft.Xbox*',
                'Microsoft.MixedReality*',
                'Microsoft.3DBuilder',
                'Microsoft.Print3D'
            )
        }
        
        if ($Preset) {
            $Packages = $presets[$Preset]
        }
        
        if (-not $Packages -or $Packages.Count -eq 0) {
            throw "No packages specified for removal"
        }
    }
    
    process {
        try {
            # Confirm
            if (-not $Force) {
                $confirmed = Confirm-Better11Action -Prompt "Remove $($Packages.Count) bloatware packages?"
                if (-not $confirmed) {
                    throw "Bloatware removal cancelled by user"
                }
            }
            
            # Create restore point
            if ($PSCmdlet.ShouldProcess("System", "Create restore point")) {
                New-Better11RestorePoint -Description "Before bloatware removal" | Out-Null
            }
            
            $results = @()
            
            foreach ($packagePattern in $Packages) {
                try {
                    Write-Better11Log -Message "Removing package: $packagePattern" -Level Info
                    
                    if ($PSCmdlet.ShouldProcess($packagePattern, "Remove AppX package")) {
                        # Find and remove matching packages
                        $matchingPackages = Get-AppxPackage -Name $packagePattern -ErrorAction SilentlyContinue
                        
                        foreach ($package in $matchingPackages) {
                            Remove-AppxPackage -Package $package.PackageFullName -ErrorAction Stop
                            
                            $results += [PSCustomObject]@{
                                PackageName = $package.Name
                                Version = $package.Version
                                Success = $true
                            }
                        }
                        
                        if (-not $matchingPackages) {
                            Write-Better11Log -Message "No matching packages found for: $packagePattern" -Level Warning
                        }
                    }
                }
                catch {
                    Write-Better11Log -Message "Failed to remove package ${packagePattern}: $_" -Level Error
                    
                    $results += [PSCustomObject]@{
                        PackageName = $packagePattern
                        Success = $false
                        Error = $_.Exception.Message
                    }
                }
            }
            
            return [PSCustomObject]@{
                TotalPackages = $Packages.Count
                RemovedSuccessfully = ($results | Where-Object Success).Count
                Failed = ($results | Where-Object { -not $_.Success }).Count
                Details = $results
            }
        }
        catch {
            Write-Better11Log -Message "Bloatware removal failed: $_" -Level Error
            throw
        }
    }
}
