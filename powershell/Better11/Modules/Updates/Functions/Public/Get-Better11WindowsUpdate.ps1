function Get-Better11WindowsUpdate {
    <#
    .SYNOPSIS
        Gets available Windows updates.
    
    .DESCRIPTION
        Retrieves a list of available Windows updates including security updates,
        feature updates, and driver updates.
    
    .PARAMETER IncludeInstalled
        If specified, includes updates that are already installed.
    
    .PARAMETER UpdateType
        Filter by update type: All, Security, Critical, Feature, Driver
    
    .EXAMPLE
        Get-Better11WindowsUpdate
        Gets all available updates.
    
    .EXAMPLE
        Get-Better11WindowsUpdate -UpdateType Security
        Gets only security updates.
    
    .OUTPUTS
        PSCustomObject[]
        Array of update information objects.
    #>
    
    [CmdletBinding()]
    [OutputType([PSCustomObject[]])]
    param(
        [Parameter()]
        [switch]$IncludeInstalled,
        
        [Parameter()]
        [ValidateSet('All', 'Security', 'Critical', 'Feature', 'Driver')]
        [string]$UpdateType = 'All'
    )
    
    begin {
        Write-Better11Log -Message "Checking for Windows updates" -Level Info
        
        if (-not (Test-Better11Administrator)) {
            throw "Checking for Windows updates requires administrator privileges"
        }
    }
    
    process {
        try {
            Write-Better11Log -Message "Creating Windows Update session..." -Level Info
            
            # Create Windows Update session
            $session = New-Object -ComObject Microsoft.Update.Session
            $searcher = $session.CreateUpdateSearcher()
            
            # Build search criteria
            $criteria = if ($IncludeInstalled) {
                "IsInstalled=0 or IsInstalled=1"
            } else {
                "IsInstalled=0"
            }
            
            Write-Better11Log -Message "Searching for updates with criteria: $criteria" -Level Debug
            
            # Search for updates
            $searchResult = $searcher.Search($criteria)
            
            if ($searchResult.Updates.Count -eq 0) {
                Write-Better11Log -Message "No updates found" -Level Info
                return @()
            }
            
            # Process updates
            $updates = @()
            foreach ($update in $searchResult.Updates) {
                # Determine update type
                $type = if ($update.MsrcSeverity -eq 'Critical') { 'Critical' }
                        elseif ($update.Categories | Where-Object { $_.Name -eq 'Security Updates' }) { 'Security' }
                        elseif ($update.Categories | Where-Object { $_.Name -eq 'Feature Packs' }) { 'Feature' }
                        elseif ($update.Categories | Where-Object { $_.Name -eq 'Drivers' }) { 'Driver' }
                        else { 'Other' }
                
                # Apply type filter
                if ($UpdateType -ne 'All' -and $type -ne $UpdateType) {
                    continue
                }
                
                $updates += [PSCustomObject]@{
                    Title = $update.Title
                    Description = $update.Description
                    UpdateId = $update.Identity.UpdateID
                    Type = $type
                    SizeMB = [math]::Round($update.MaxDownloadSize / 1MB, 2)
                    IsInstalled = $update.IsInstalled
                    IsMandatory = $update.IsMandatory
                    IsDownloaded = $update.IsDownloaded
                    RebootRequired = $update.RebootRequired
                    SupportUrl = $update.SupportUrl
                    KBArticleIDs = $update.KBArticleIDs
                }
            }
            
            Write-Better11Log -Message "Found $($updates.Count) updates" -Level Info
            return $updates
        }
        catch {
            Write-Better11Log -Message "Failed to check for Windows updates: $_" -Level Error
            throw
        }
    }
}
