function Clear-Better11TempFiles {
    <#
    .SYNOPSIS
        Cleans temporary files from common locations.
    
    .DESCRIPTION
        Removes temporary files from Windows Temp, User Temp, and other
        common temporary file locations. Can filter by file age.
    
    .PARAMETER AgeDays
        Delete files older than this many days. Default is 7 days.
    
    .PARAMETER WhatIf
        Shows what would be deleted without actually deleting.
    
    .PARAMETER Confirm
        Prompts for confirmation before deleting files.
    
    .EXAMPLE
        Clear-Better11TempFiles
        
        Cleans temp files older than 7 days.
    
    .EXAMPLE
        Clear-Better11TempFiles -AgeDays 30
        
        Cleans temp files older than 30 days.
    
    .EXAMPLE
        Clear-Better11TempFiles -WhatIf
        
        Shows what would be cleaned without actually deleting.
    
    .OUTPUTS
        PSCustomObject
        Cleanup result with files removed and space freed
    #>
    
    [CmdletBinding(SupportsShouldProcess)]
    [OutputType([PSCustomObject])]
    param(
        [Parameter()]
        [ValidateRange(1, 365)]
        [int]$AgeDays = 7
    )
    
    begin {
        Write-Better11Log -Message "Starting temp file cleanup (age: $AgeDays days)" -Level Info -Component "Disk"
        
        # Temp locations to clean
        $tempLocations = @(
            "$env:TEMP",
            "$env:SystemRoot\Temp",
            "$env:SystemRoot\Prefetch",
            "$env:LOCALAPPDATA\Microsoft\Windows\INetCache",
            "$env:SystemRoot\SoftwareDistribution\Download"
        )
        
        $cutoffDate = (Get-Date).AddDays(-$AgeDays)
        $filesRemoved = 0
        $spaceFreedBytes = 0
        $locationsProcessed = @()
    }
    
    process {
        foreach ($location in $tempLocations) {
            if (-not (Test-Path $location)) {
                Write-Better11Log -Message "Skipping non-existent location: $location" -Level Debug -Component "Disk"
                continue
            }
            
            Write-Better11Log -Message "Cleaning: $location" -Level Info -Component "Disk"
            
            try {
                $files = Get-ChildItem -Path $location -File -Recurse -ErrorAction SilentlyContinue |
                         Where-Object { $_.LastWriteTime -lt $cutoffDate }
                
                foreach ($file in $files) {
                    try {
                        if ($PSCmdlet.ShouldProcess($file.FullName, "Delete temporary file")) {
                            $size = $file.Length
                            Remove-Item -Path $file.FullName -Force -ErrorAction Stop
                            $filesRemoved++
                            $spaceFreedBytes += $size
                        }
                    }
                    catch {
                        Write-Better11Log -Message "Cannot delete $($file.FullName): $_" -Level Debug -Component "Disk"
                    }
                }
                
                $locationsProcessed += $location
            }
            catch {
                Write-Better11Log -Message "Error processing $location: $_" -Level Warning -Component "Disk"
            }
        }
        
        $spaceFreedMB = [math]::Round($spaceFreedBytes / 1MB, 2)
        
        Write-Better11Log -Message "Cleanup complete: $filesRemoved files, $spaceFreedMB MB freed" -Level Info -Component "Disk"
        
        return [PSCustomObject]@{
            LocationsCleaned = $locationsProcessed
            FilesRemoved = $filesRemoved
            SpaceFreedMB = $spaceFreedMB
            SpaceFreedGB = [math]::Round($spaceFreedBytes / 1GB, 2)
        }
    }
}
