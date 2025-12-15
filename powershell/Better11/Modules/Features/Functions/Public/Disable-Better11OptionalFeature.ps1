function Disable-Better11OptionalFeature {
    <#
    .SYNOPSIS
        Disables a Windows optional feature.
    .DESCRIPTION
        Disables a Windows optional feature using DISM.
    .PARAMETER Name
        The feature name to disable.
    .PARAMETER NoRestart
        Suppress automatic restart.
    .EXAMPLE
        Disable-Better11OptionalFeature -Name "SMB1Protocol"
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
        
        if ($Feature.State -eq 'Disabled') {
            return [PSCustomObject]@{
                Success = $true
                Feature = $Name
                Message = "Feature already disabled"
                RestartRequired = $false
            }
        }
        
        $Params = @{
            Online = $true
            FeatureName = $Name
            NoRestart = $NoRestart.IsPresent
        }
        
        $Result = Disable-WindowsOptionalFeature @Params
        
        return [PSCustomObject]@{
            Success = $true
            Feature = $Name
            Message = "Feature disabled"
            RestartRequired = $Result.RestartNeeded
        }
    }
    catch {
        Write-Error "Failed to disable feature $Name: $_"
        return [PSCustomObject]@{ Success = $false; Feature = $Name; Error = $_.Exception.Message }
    }
}
