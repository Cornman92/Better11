function New-Better11RestorePoint {
    <#
    .SYNOPSIS
        Creates a system restore point before making system changes.
    
    .DESCRIPTION
        Creates a Windows system restore point with a descriptive name.
        This provides a recovery option if system changes cause issues.
    
    .PARAMETER Description
        Description for the restore point.
    
    .EXAMPLE
        New-Better11RestorePoint -Description "Before registry tweaks"
    
    .OUTPUTS
        PSCustomObject
        Returns restore point information if successful.
    #>
    
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$Description
    )
    
    begin {
        if (-not (Test-Better11Administrator)) {
            throw "Creating restore points requires administrator privileges"
        }
    }
    
    process {
        try {
            Write-Better11Log -Message "Creating restore point: $Description" -Level Info
            
            if ($PSCmdlet.ShouldProcess($Description, "Create restore point")) {
                # Enable System Restore if not already enabled
                $restoreEnabled = (Get-ComputerRestorePoint -ErrorAction SilentlyContinue) -ne $null
                
                if (-not $restoreEnabled) {
                    Write-Better11Log -Message "System Restore is not enabled. Attempting to enable..." -Level Warning
                    Enable-ComputerRestore -Drive "$env:SystemDrive" -ErrorAction Stop
                }
                
                # Create restore point
                Checkpoint-Computer -Description $Description -RestorePointType 'MODIFY_SETTINGS' -ErrorAction Stop
                
                Write-Better11Log -Message "Restore point created successfully" -Level Info
                
                return [PSCustomObject]@{
                    Success = $true
                    Description = $Description
                    Timestamp = Get-Date
                }
            }
        }
        catch {
            $errorMsg = "Failed to create restore point: $_"
            Write-Better11Log -Message $errorMsg -Level Error
            
            return [PSCustomObject]@{
                Success = $false
                Description = $Description
                Error = $_.Exception.Message
            }
        }
    }
}
