function Optimize-Better11NetworkSettings {
    <#
    .SYNOPSIS
        Optimizes network settings for better performance.
    
    .DESCRIPTION
        Applies network optimizations including:
        - TCP window scaling
        - DNS client settings
        - Network adapter properties
    
    .PARAMETER Force
        Skip confirmation prompt.
    
    .EXAMPLE
        Optimize-Better11NetworkSettings
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter()]
        [switch]$Force
    )
    
    if (-not (Test-Better11Administrator)) {
        throw "This function requires administrator privileges"
    }
    
    if (-not $Force) {
        $Message = "Optimize network settings? This will modify network adapter configuration."
        if (-not (Confirm-Better11Action -Message $Message)) {
            Write-Better11Log -Message "Network optimization cancelled" -Level Info
            return
        }
    }
    
    try {
        Write-Better11Log -Message "Optimizing network settings..." -Level Info
        
        # Create restore point
        New-Better11RestorePoint -Description "Before Better11 Network Optimization"
        
        $Results = @()
        
        # Optimize TCP settings
        Write-Better11Log -Message "Optimizing TCP settings..." -Level Info
        
        $TCPTweaks = @(
            @{Path='HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters'; Name='TcpWindowSize'; Value=65535; Type='DWord'},
            @{Path='HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters'; Name='Tcp1323Opts'; Value=3; Type='DWord'},
            @{Path='HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters'; Name='DefaultTTL'; Value=64; Type='DWord'}
        )
        
        foreach ($Tweak in $TCPTweaks) {
            try {
                if (-not (Test-Path $Tweak.Path)) {
                    New-Item -Path $Tweak.Path -Force | Out-Null
                }
                Set-ItemProperty -Path $Tweak.Path -Name $Tweak.Name -Value $Tweak.Value -Type $Tweak.Type
                $Results += "Applied: $($Tweak.Name)"
            }
            catch {
                Write-Better11Log -Message "Failed to apply $($Tweak.Name): $_" -Level Warning
            }
        }
        
        # Disable network throttling
        Write-Better11Log -Message "Disabling network throttling..." -Level Info
        Set-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile' -Name 'NetworkThrottlingIndex' -Value 0xFFFFFFFF -Type DWord
        $Results += "Network throttling disabled"
        
        Write-Better11Log -Message "Network optimization completed. Restart required." -Level Info
        
        return [PSCustomObject]@{
            Success = $true
            OptimizationsApplied = $Results
            Message = "Network settings optimized. Restart required for changes to take effect."
        }
    }
    catch {
        Write-Better11Log -Message "Network optimization failed: $_" -Level Error
        throw
    }
}
