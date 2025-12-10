function Get-Better11PowerPlans {
    <#
    .SYNOPSIS
        Lists all available power plans.
    
    .DESCRIPTION
        Retrieves all power plans from the system, including which plan is currently active.
    
    .EXAMPLE
        Get-Better11PowerPlans
        
        Lists all power plans with their status.
    
    .EXAMPLE
        Get-Better11PowerPlans | Where-Object IsActive
        
        Gets the currently active power plan.
    
    .OUTPUTS
        PSCustomObject[]
        Array of power plan objects
    #>
    
    [CmdletBinding()]
    [OutputType([PSCustomObject[]])]
    param()
    
    begin {
        Write-Better11Log -Message "Listing power plans" -Level Info -Component "Power"
    }
    
    process {
        try {
            # Get list of power plans using powercfg
            $output = & powercfg /list 2>&1
            
            if ($LASTEXITCODE -ne 0) {
                Write-Better11Log -Message "Failed to list power plans: $output" -Level Error -Component "Power"
                throw "Failed to list power plans"
            }
            
            $plans = @()
            $activeGuid = $null
            
            foreach ($line in $output) {
                if ($line -match 'Power Scheme GUID:\s+([0-9a-f\-]+)\s+\((.+?)\)\s*(\*)?') {
                    $guid = $matches[1]
                    $name = $matches[2]
                    $isActive = $matches[3] -eq '*'
                    
                    if ($isActive) {
                        $activeGuid = $guid
                    }
                    
                    # Determine plan type
                    $planType = switch ($guid) {
                        '381b4222-f694-41f0-9685-ff5bb260df2e' { 'Balanced' }
                        '8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c' { 'HighPerformance' }
                        'a1841308-3541-4fab-bc81-f71556f20b4a' { 'PowerSaver' }
                        'e9a42b02-d5df-448d-aa00-03f14749eb61' { 'UltimatePerformance' }
                        default { 'Custom' }
                    }
                    
                    $plans += [PSCustomObject]@{
                        Guid = $guid
                        Name = $name
                        Type = $planType
                        IsActive = $isActive
                    }
                }
            }
            
            Write-Better11Log -Message "Found $($plans.Count) power plan(s)" -Level Info -Component "Power"
            
            return $plans
        }
        catch {
            Write-Better11Log -Message "Error listing power plans: $_" -Level Error -Component "Power"
            throw
        }
    }
}
