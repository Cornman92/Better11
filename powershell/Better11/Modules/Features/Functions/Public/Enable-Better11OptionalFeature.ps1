function Enable-Better11OptionalFeature {
    <#
    .SYNOPSIS
        Enables a Windows optional feature.
    .DESCRIPTION
        Enables a Windows optional feature using DISM.
    .PARAMETER Name
        The feature name to enable.
    .PARAMETER NoRestart
        Suppress automatic restart.
    .EXAMPLE
        Enable-Better11OptionalFeature -Name "Microsoft-Hyper-V-All"
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,
        
        [Parameter()]
        [switch]$NoRestart
    )

    try {
        # Check for admin rights
        if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
            throw "Administrator privileges required"
        }
        
        # Check if feature exists
        $Feature = Get-WindowsOptionalFeature -Online -FeatureName $Name -ErrorAction Stop
        
        if ($Feature.State -eq 'Enabled') {
            return [PSCustomObject]@{
                Success = $true
                Feature = $Name
                Message = "Feature already enabled"
                RestartRequired = $false
            }
        }
        
        $Params = @{
            Online = $true
            FeatureName = $Name
            NoRestart = $NoRestart.IsPresent
        }
        
        $Result = Enable-WindowsOptionalFeature @Params
        
        return [PSCustomObject]@{
            Success = $true
            Feature = $Name
            Message = "Feature enabled"
            RestartRequired = $Result.RestartNeeded
        }
    }
    catch {
        Write-Error "Failed to enable feature $Name: $_"
        return [PSCustomObject]@{ Success = $false; Feature = $Name; Error = $_.Exception.Message }
    }
}
