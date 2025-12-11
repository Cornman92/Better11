function Clear-Better11DNSCache {
    <#
    .SYNOPSIS
        Clears the DNS resolver cache.
    
    .DESCRIPTION
        Flushes the DNS client resolver cache, removing all cached DNS records.
        This can help resolve DNS-related connectivity issues.
    
    .PARAMETER Force
        Skips confirmation prompt.
    
    .EXAMPLE
        Clear-Better11DNSCache
        
        Flushes DNS cache with confirmation.
    
    .EXAMPLE
        Clear-Better11DNSCache -Force
        
        Flushes DNS cache without confirmation.
    
    .OUTPUTS
        Boolean
        True if successful
    #>
    
    [CmdletBinding(SupportsShouldProcess)]
    [OutputType([bool])]
    param(
        [Parameter()]
        [switch]$Force
    )
    
    begin {
        Write-Better11Log -Message "Flushing DNS cache" -Level Info -Component "Network"
        
        # Check admin privileges
        if (-not (Test-Better11Administrator)) {
            Write-Better11Log -Message "DNS cache flush requires administrator privileges" -Level Error -Component "Network"
            throw "Administrator privileges required"
        }
    }
    
    process {
        try {
            # Confirm action
            if (-not $Force -and -not (Confirm-Better11Action "Flush DNS resolver cache?")) {
                Write-Better11Log -Message "DNS cache flush cancelled by user" -Level Warning -Component "Network"
                return $false
            }
            
            if ($PSCmdlet.ShouldProcess("DNS Cache", "Flush")) {
                # Execute ipconfig /flushdns
                $result = & ipconfig /flushdns 2>&1
                
                if ($LASTEXITCODE -eq 0) {
                    Write-Better11Log -Message "DNS cache flushed successfully" -Level Info -Component "Network"
                    return $true
                }
                else {
                    Write-Better11Log -Message "Failed to flush DNS cache: $result" -Level Error -Component "Network"
                    return $false
                }
            }
            
            return $true
        }
        catch {
            Write-Better11Log -Message "Error flushing DNS cache: $_" -Level Error -Component "Network"
            throw
        }
    }
}
