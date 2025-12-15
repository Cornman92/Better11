function Get-Better11OptionalFeatures {
    <#
    .SYNOPSIS
        Gets all optional Windows features.
    .DESCRIPTION
        Lists all optional features and their current state.
    .PARAMETER Name
        Filter by feature name pattern.
    .EXAMPLE
        Get-Better11OptionalFeatures
        Get-Better11OptionalFeatures -Name "*Hyper*"
    #>
    [CmdletBinding()]
    param(
        [Parameter()]
        [string]$Name = "*"
    )

    try {
        $Features = Get-WindowsOptionalFeature -Online | Where-Object { $_.FeatureName -like $Name }
        
        $Results = foreach ($Feature in $Features) {
            [PSCustomObject]@{
                Name = $Feature.FeatureName
                State = $Feature.State
                RestartRequired = $Feature.RestartNeeded
                Description = $Feature.Description
            }
        }
        
        return $Results
    }
    catch {
        Write-Error "Failed to get optional features: $_"
        return @()
    }
}
