function Optimize-Better11Performance {
    <#
    .SYNOPSIS
        Performs one-click system performance optimization.
    
    .DESCRIPTION
        Applies a set of performance optimizations including:
        - Disk cleanup
        - Temporary file removal
        - Disable unnecessary services
        - Optimize visual effects
        - Clear system caches
    
    .PARAMETER Level
        Optimization level: Light, Moderate, Aggressive
    
    .PARAMETER Force
        Skip confirmation prompts.
    
    .EXAMPLE
        Optimize-Better11Performance -Level Moderate
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter()]
        [ValidateSet('Light', 'Moderate', 'Aggressive')]
        [string]$Level = 'Moderate',
        
        [Parameter()]
        [switch]$Force
    )
    
    if (-not (Test-Better11Administrator)) {
        throw "This function requires administrator privileges"
    }
    
    if (-not $Force) {
        $Message = "Apply $Level performance optimization? This will modify system settings."
        if (-not (Confirm-Better11Action -Message $Message)) {
            Write-Better11Log -Message "Optimization cancelled" -Level Info
            return
        }
    }
    
    try {
        Write-Better11Log -Message "Starting $Level performance optimization" -Level Info
        
        # Create restore point
        New-Better11RestorePoint -Description "Before Better11 Performance Optimization"
        
        $Results = @{
            Level = $Level
            OptimizationsApplied = @()
            SpaceFreedMB = 0
        }
        
        # Clean temporary files
        Write-Better11Log -Message "Cleaning temporary files..." -Level Info
        $TempPaths = @(
            "$env:TEMP\*",
            "$env:WINDIR\Temp\*",
            "$env:USERPROFILE\AppData\Local\Temp\*"
        )
        
        foreach ($Path in $TempPaths) {
            try {
                $BeforeSize = (Get-ChildItem $Path -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
                Remove-Item $Path -Recurse -Force -ErrorAction SilentlyContinue
                $AfterSize = (Get-ChildItem $Path -Recurse -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
                $Results.SpaceFreedMB += [math]::Round(($BeforeSize - $AfterSize) / 1MB, 2)
            }
            catch {
                Write-Better11Log -Message "Failed to clean $Path : $_" -Level Warning
            }
        }
        $Results.OptimizationsApplied += "Temporary files cleaned"
        
        # Disable unnecessary services (based on level)
        if ($Level -in @('Moderate', 'Aggressive')) {
            Write-Better11Log -Message "Optimizing services..." -Level Info
            
            $ServicesToDisable = @(
                'DiagTrack',  # Diagnostics Tracking Service
                'dmwappushservice',  # WAP Push Message Routing Service
                'WSearch'  # Windows Search (if Aggressive)
            )
            
            if ($Level -eq 'Light') {
                $ServicesToDisable = $ServicesToDisable[0..1]
            }
            
            foreach ($ServiceName in $ServicesToDisable) {
                try {
                    Stop-Service -Name $ServiceName -Force -ErrorAction SilentlyContinue
                    Set-Service -Name $ServiceName -StartupType Disabled -ErrorAction SilentlyContinue
                    $Results.OptimizationsApplied += "Disabled service: $ServiceName"
                }
                catch {
                    Write-Better11Log -Message "Failed to disable service $ServiceName : $_" -Level Warning
                }
            }
        }
        
        # Optimize visual effects
        Write-Better11Log -Message "Optimizing visual effects..." -Level Info
        $VisualEffectsTweaks = @(
            @{Path='HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects'; Name='VisualFXSetting'; Value=2; Type='DWord'}
        )
        
        foreach ($Tweak in $VisualEffectsTweaks) {
            try {
                if (-not (Test-Path $Tweak.Path)) {
                    New-Item -Path $Tweak.Path -Force | Out-Null
                }
                Set-ItemProperty -Path $Tweak.Path -Name $Tweak.Name -Value $Tweak.Value -Type $Tweak.Type
            }
            catch {
                Write-Better11Log -Message "Failed to apply visual effects tweak: $_" -Level Warning
            }
        }
        $Results.OptimizationsApplied += "Visual effects optimized"
        
        Write-Better11Log -Message "Performance optimization completed" -Level Info
        
        return [PSCustomObject]$Results
    }
    catch {
        Write-Better11Log -Message "Performance optimization failed: $_" -Level Error
        throw
    }
}
