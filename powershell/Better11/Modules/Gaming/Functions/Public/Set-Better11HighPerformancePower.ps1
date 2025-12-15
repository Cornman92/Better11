function Set-Better11HighPerformancePower {
    <#
    .SYNOPSIS
        Sets the High Performance power plan.
    .DESCRIPTION
        Activates the High Performance or Ultimate Performance power plan.
    .EXAMPLE
        Set-Better11HighPerformancePower
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param()

    if ($PSCmdlet.ShouldProcess("Power Plan", "Set to High Performance")) {
        try {
            # High Performance GUID
            $HighPerf = "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"
            # Ultimate Performance GUID
            $Ultimate = "e9a42b02-d5df-448d-aa00-03f14749eb61"
            
            # Try Ultimate first, fall back to High Performance
            $Result = & powercfg /setactive $Ultimate 2>&1
            if ($LASTEXITCODE -ne 0) {
                $Result = & powercfg /setactive $HighPerf 2>&1
                if ($LASTEXITCODE -eq 0) {
                    Write-Verbose "High Performance power plan activated"
                    return [PSCustomObject]@{ Success = $true; PowerPlan = "High Performance" }
                }
            } else {
                Write-Verbose "Ultimate Performance power plan activated"
                return [PSCustomObject]@{ Success = $true; PowerPlan = "Ultimate Performance" }
            }
            
            throw "Failed to set power plan"
        }
        catch {
            Write-Error "Failed to set power plan: $_"
            return [PSCustomObject]@{ Success = $false; Error = $_.Exception.Message }
        }
    }
}
