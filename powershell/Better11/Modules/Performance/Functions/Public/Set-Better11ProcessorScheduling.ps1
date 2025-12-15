function Set-Better11ProcessorScheduling {
    <#
    .SYNOPSIS
        Sets processor scheduling priority.
    .DESCRIPTION
        Configures whether to optimize for programs or background services.
    .PARAMETER Priority
        Programs or BackgroundServices.
    .EXAMPLE
        Set-Better11ProcessorScheduling -Priority Programs
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet('Programs', 'BackgroundServices')]
        [string]$Priority
    )

    try {
        if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
            throw "Administrator privileges required"
        }
        
        $RegPath = 'HKLM:\SYSTEM\CurrentControlSet\Control\PriorityControl'
        
        # Win32PrioritySeparation values:
        # 38 (0x26) = Short, Fixed, High foreground boost (best for programs)
        # 24 (0x18) = Long, Variable, No foreground boost (best for background services)
        $Value = if ($Priority -eq 'Programs') { 38 } else { 24 }
        
        Set-ItemProperty -Path $RegPath -Name 'Win32PrioritySeparation' -Value $Value -Type DWord
        
        return [PSCustomObject]@{
            Success = $true
            Priority = $Priority
            Win32PrioritySeparation = $Value
        }
    }
    catch {
        Write-Error "Failed to set processor scheduling: $_"
        return [PSCustomObject]@{ Success = $false; Error = $_.Exception.Message }
    }
}
