function Get-Better11StartupImpact {
    <#
    .SYNOPSIS
        Gets startup impact analysis.
    .DESCRIPTION
        Analyzes startup programs and their impact on boot time.
    .EXAMPLE
        Get-Better11StartupImpact
    #>
    [CmdletBinding()]
    param()

    try {
        # Get startup apps from WMI/CIM
        $StartupApps = Get-CimInstance -ClassName Win32_StartupCommand
        
        $Results = foreach ($App in $StartupApps) {
            # Estimate impact based on location and type
            $Impact = 'Medium'
            if ($App.Location -like '*Run*') {
                $Impact = 'Low'
            }
            if ($App.Command -match 'services|svchost') {
                $Impact = 'High'
            }
            
            [PSCustomObject]@{
                Name = $App.Name
                Command = $App.Command
                Location = $App.Location
                User = $App.User
                EstimatedImpact = $Impact
            }
        }
        
        return $Results
    }
    catch {
        Write-Error "Failed to get startup impact: $_"
        return @()
    }
}
