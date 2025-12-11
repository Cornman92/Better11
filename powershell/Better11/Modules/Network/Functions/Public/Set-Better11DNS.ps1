function Set-Better11DNS {
    <#
    .SYNOPSIS
        Configures DNS servers for a network adapter.
    
    .DESCRIPTION
        Sets the DNS server addresses for a specified network adapter.
        Supports setting primary and secondary DNS servers.
    
    .PARAMETER AdapterName
        Name of the network adapter to configure.
    
    .PARAMETER PrimaryDNS
        Primary DNS server IP address.
    
    .PARAMETER SecondaryDNS
        Optional secondary DNS server IP address.
    
    .PARAMETER Preset
        Use a predefined DNS configuration (Google, Cloudflare, Quad9, OpenDNS).
    
    .PARAMETER Force
        Skip confirmation prompt.
    
    .EXAMPLE
        Set-Better11DNS -AdapterName "Ethernet" -Preset Google
        
        Sets DNS to Google DNS (8.8.8.8, 8.8.4.4).
    
    .EXAMPLE
        Set-Better11DNS -AdapterName "Wi-Fi" -PrimaryDNS "1.1.1.1" -SecondaryDNS "1.0.0.1"
        
        Sets DNS to Cloudflare DNS manually.
    
    .OUTPUTS
        Boolean
        True if successful
    #>
    
    [CmdletBinding(SupportsShouldProcess)]
    [OutputType([bool])]
    param(
        [Parameter(Mandatory = $true)]
        [string]$AdapterName,
        
        [Parameter(ParameterSetName = 'Manual')]
        [string]$PrimaryDNS,
        
        [Parameter(ParameterSetName = 'Manual')]
        [string]$SecondaryDNS,
        
        [Parameter(ParameterSetName = 'Preset')]
        [ValidateSet('Google', 'Cloudflare', 'Quad9', 'OpenDNS')]
        [string]$Preset,
        
        [Parameter()]
        [switch]$Force
    )
    
    begin {
        Write-Better11Log -Message "Configuring DNS for adapter: $AdapterName" -Level Info -Component "Network"
        
        # Check admin privileges
        if (-not (Test-Better11Administrator)) {
            Write-Better11Log -Message "DNS configuration requires administrator privileges" -Level Error -Component "Network"
            throw "Administrator privileges required"
        }
        
        # Define DNS presets
        $DNSPresets = @{
            Google = @{
                Primary = "8.8.8.8"
                Secondary = "8.8.4.4"
            }
            Cloudflare = @{
                Primary = "1.1.1.1"
                Secondary = "1.0.0.1"
            }
            Quad9 = @{
                Primary = "9.9.9.9"
                Secondary = "149.112.112.112"
            }
            OpenDNS = @{
                Primary = "208.67.222.222"
                Secondary = "208.67.220.220"
            }
        }
    }
    
    process {
        try {
            # Determine DNS servers to use
            if ($Preset) {
                $PrimaryDNS = $DNSPresets[$Preset].Primary
                $SecondaryDNS = $DNSPresets[$Preset].Secondary
                Write-Better11Log -Message "Using $Preset DNS preset" -Level Info -Component "Network"
            }
            
            # Confirm action
            $message = "Set DNS for '$AdapterName' to $PrimaryDNS"
            if ($SecondaryDNS) {
                $message += ", $SecondaryDNS"
            }
            
            if (-not $Force -and -not (Confirm-Better11Action $message)) {
                Write-Better11Log -Message "DNS configuration cancelled by user" -Level Warning -Component "Network"
                return $false
            }
            
            if ($PSCmdlet.ShouldProcess($AdapterName, "Configure DNS")) {
                # Set primary DNS
                $result = & netsh interface ip set dns name="$AdapterName" static $PrimaryDNS 2>&1
                
                if ($LASTEXITCODE -ne 0) {
                    Write-Better11Log -Message "Failed to set primary DNS: $result" -Level Error -Component "Network"
                    return $false
                }
                
                Write-Better11Log -Message "Set primary DNS: $PrimaryDNS" -Level Info -Component "Network"
                
                # Set secondary DNS if provided
                if ($SecondaryDNS) {
                    $result = & netsh interface ip add dns name="$AdapterName" addr=$SecondaryDNS index=2 2>&1
                    
                    if ($LASTEXITCODE -ne 0) {
                        Write-Better11Log -Message "Failed to set secondary DNS: $result" -Level Warning -Component "Network"
                    }
                    else {
                        Write-Better11Log -Message "Set secondary DNS: $SecondaryDNS" -Level Info -Component "Network"
                    }
                }
                
                Write-Better11Log -Message "DNS configuration completed successfully" -Level Info -Component "Network"
                return $true
            }
            
            return $true
        }
        catch {
            Write-Better11Log -Message "Error configuring DNS: $_" -Level Error -Component "Network"
            throw
        }
    }
}
