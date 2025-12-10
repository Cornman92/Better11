function Set-Better11RegistryTweak {
    <#
    .SYNOPSIS
        Applies registry tweaks with automatic backup.
    
    .DESCRIPTION
        Applies one or more registry modifications with safety features including
        automatic backup, restore point creation, and user confirmation.
    
    .PARAMETER Tweaks
        Array of registry tweak hashtables. Each tweak should have:
        - Hive: Registry hive (HKLM, HKCU, etc.)
        - Path: Registry path
        - Name: Value name
        - Value: Value data
        - Type: Value type (String, DWord, QWord, etc.)
    
    .PARAMETER Force
        Skip confirmation prompts.
    
    .PARAMETER NoBackup
        Skip registry backup (not recommended).
    
    .PARAMETER NoRestorePoint
        Skip restore point creation (not recommended).
    
    .EXAMPLE
        $tweak = @{
            Hive = 'HKCU'
            Path = 'Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced'
            Name = 'HideFileExt'
            Value = 0
            Type = 'DWord'
        }
        Set-Better11RegistryTweak -Tweaks $tweak
    
    .EXAMPLE
        $tweaks = @(
            @{Hive='HKCU'; Path='Control Panel\Desktop'; Name='MenuShowDelay'; Value=0; Type='String'},
            @{Hive='HKCU'; Path='Control Panel\Mouse'; Name='MouseSpeed'; Value=0; Type='String'}
        )
        Set-Better11RegistryTweak -Tweaks $tweaks -Force
    
    .OUTPUTS
        PSCustomObject
        Result of the operation with applied tweaks.
    #>
    
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory = $true, ValueFromPipeline = $true)]
        [hashtable[]]$Tweaks,
        
        [Parameter()]
        [switch]$Force,
        
        [Parameter()]
        [switch]$NoBackup,
        
        [Parameter()]
        [switch]$NoRestorePoint
    )
    
    begin {
        Write-Better11Log -Message "Applying registry tweaks" -Level Info
        
        if (-not (Test-Better11Administrator)) {
            throw "Registry modifications require administrator privileges"
        }
        
        if (-not $NoRestorePoint -and $PSCmdlet.ShouldProcess("System", "Create restore point")) {
            New-Better11RestorePoint -Description "Before registry tweaks" | Out-Null
        }
        
        $appliedTweaks = @()
        $backedUpPaths = @{}
    }
    
    process {
        foreach ($tweak in $Tweaks) {
            try {
                $fullPath = "$($tweak.Hive):\$($tweak.Path)"
                
                if (-not $Force) {
                    $confirmed = Confirm-Better11Action -Prompt "Apply tweak to $fullPath\$($tweak.Name)?"
                    if (-not $confirmed) {
                        Write-Better11Log -Message "Tweak cancelled for $fullPath" -Level Warning
                        continue
                    }
                }
                
                if (-not $NoBackup -and -not $backedUpPaths.ContainsKey($fullPath) -and $PSCmdlet.ShouldProcess($fullPath, "Backup registry key")) {
                    Backup-Better11Registry -KeyPath $fullPath | Out-Null
                    $backedUpPaths[$fullPath] = $true
                }
                
                if ($PSCmdlet.ShouldProcess("$fullPath\$($tweak.Name)", "Set registry value")) {
                    # Ensure path exists
                    if (-not (Test-Path $fullPath)) {
                        New-Item -Path $fullPath -Force | Out-Null
                    }
                    
                    # Set value
                    $valueType = switch ($tweak.Type) {
                        'String' { 'String' }
                        'DWord' { 'DWord' }
                        'QWord' { 'QWord' }
                        'Binary' { 'Binary' }
                        'MultiString' { 'MultiString' }
                        'ExpandString' { 'ExpandString' }
                        default { 'String' }
                    }
                    
                    Set-ItemProperty -Path $fullPath -Name $tweak.Name -Value $tweak.Value -Type $valueType -Force
                    
                    Write-Better11Log -Message "Applied tweak: $fullPath\$($tweak.Name) = $($tweak.Value)" -Level Info
                    
                    $appliedTweaks += [PSCustomObject]@{
                        Path = $fullPath
                        Name = $tweak.Name
                        Value = $tweak.Value
                        Type = $valueType
                        Success = $true
                    }
                }
            }
            catch {
                Write-Better11Log -Message "Failed to apply tweak: $_" -Level Error
                
                $appliedTweaks += [PSCustomObject]@{
                    Path = $fullPath
                    Name = $tweak.Name
                    Success = $false
                    Error = $_.Exception.Message
                }
            }
        }
    }
    
    end {
        return [PSCustomObject]@{
            TotalTweaks = $Tweaks.Count
            AppliedSuccessfully = ($appliedTweaks | Where-Object Success).Count
            Failed = ($appliedTweaks | Where-Object { -not $_.Success }).Count
            Details = $appliedTweaks
        }
    }
}
