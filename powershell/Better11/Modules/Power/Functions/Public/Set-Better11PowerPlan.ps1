function Set-Better11PowerPlan {
    <#
    .SYNOPSIS
        Sets the active power plan.
    
    .DESCRIPTION
        Activates a specified power plan by GUID or name.
    
    .PARAMETER Guid
        GUID of the power plan to activate.
    
    .PARAMETER Name
        Name of the power plan to activate (e.g., "Balanced", "High Performance").
    
    .PARAMETER Force
        Skip confirmation prompt.
    
    .EXAMPLE
        Set-Better11PowerPlan -Name "High Performance"
        
        Activates the High Performance power plan.
    
    .EXAMPLE
        Set-Better11PowerPlan -Guid "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"
        
        Activates power plan by GUID.
    
    .OUTPUTS
        Boolean
        True if successful
    #>
    
    [CmdletBinding(SupportsShouldProcess)]
    [OutputType([bool])]
    param(
        [Parameter(Mandatory = $true, ParameterSetName = 'ByGuid')]
        [string]$Guid,
        
        [Parameter(Mandatory = $true, ParameterSetName = 'ByName')]
        [string]$Name,
        
        [Parameter()]
        [switch]$Force
    )
    
    begin {
        Write-Better11Log -Message "Setting active power plan" -Level Info -Component "Power"
        
        # Check admin privileges
        if (-not (Test-Better11Administrator)) {
            Write-Better11Log -Message "Setting power plan requires administrator privileges" -Level Error -Component "Power"
            throw "Administrator privileges required"
        }
    }
    
    process {
        try {
            # If name provided, find the GUID
            if ($PSCmdlet.ParameterSetName -eq 'ByName') {
                $plans = Get-Better11PowerPlans
                $plan = $plans | Where-Object { $_.Name -like "*$Name*" } | Select-Object -First 1
                
                if (-not $plan) {
                    Write-Better11Log -Message "Power plan not found: $Name" -Level Error -Component "Power"
                    throw "Power plan not found: $Name"
                }
                
                $Guid = $plan.Guid
                Write-Better11Log -Message "Found power plan: $($plan.Name) ($Guid)" -Level Info -Component "Power"
            }
            
            # Confirm action
            if (-not $Force -and -not (Confirm-Better11Action "Set active power plan to $Name ($Guid)?")) {
                Write-Better11Log -Message "Power plan change cancelled by user" -Level Warning -Component "Power"
                return $false
            }
            
            if ($PSCmdlet.ShouldProcess($Guid, "Set active power plan")) {
                # Set active power plan
                $result = & powercfg /setactive $Guid 2>&1
                
                if ($LASTEXITCODE -eq 0) {
                    Write-Better11Log -Message "Power plan activated: $Guid" -Level Info -Component "Power"
                    return $true
                }
                else {
                    Write-Better11Log -Message "Failed to set power plan: $result" -Level Error -Component "Power"
                    return $false
                }
            }
            
            return $true
        }
        catch {
            Write-Better11Log -Message "Error setting power plan: $_" -Level Error -Component "Power"
            throw
        }
    }
}
