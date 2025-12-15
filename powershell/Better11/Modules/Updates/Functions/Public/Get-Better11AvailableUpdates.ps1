function Get-Better11AvailableUpdates {
    <#
    .SYNOPSIS
        Gets available Windows updates.
    .DESCRIPTION
        Searches for available Windows updates using the Windows Update API.
    .PARAMETER IncludeHidden
        Include hidden updates in the results.
    .EXAMPLE
        Get-Better11AvailableUpdates
    #>
    [CmdletBinding()]
    param(
        [Parameter()]
        [switch]$IncludeHidden
    )

    try {
        Write-Verbose "Checking for available Windows updates..."
        
        $Session = New-Object -ComObject Microsoft.Update.Session
        $Searcher = $Session.CreateUpdateSearcher()
        
        $SearchQuery = "IsInstalled=0"
        if (-not $IncludeHidden) {
            $SearchQuery += " and IsHidden=0"
        }
        
        $SearchResult = $Searcher.Search($SearchQuery)
        
        $Updates = foreach ($Update in $SearchResult.Updates) {
            $KBArticle = ""
            if ($Update.KBArticleIDs.Count -gt 0) {
                $KBArticle = "KB$($Update.KBArticleIDs.Item(0))"
            }
            
            $SupportUrl = ""
            if ($Update.MoreInfoUrls.Count -gt 0) {
                $SupportUrl = $Update.MoreInfoUrls.Item(0)
            }
            
            $UpdateType = "Other"
            if ($Update.Categories.Count -gt 0) {
                $Category = $Update.Categories.Item(0).Name
                if ($Category -like "*Security*") { $UpdateType = "Security" }
                elseif ($Category -like "*Critical*") { $UpdateType = "Critical" }
                elseif ($Category -like "*Definition*") { $UpdateType = "Definition" }
                elseif ($Category -like "*Driver*") { $UpdateType = "Driver" }
                elseif ($Category -like "*Feature*") { $UpdateType = "Feature" }
            }
            
            [PSCustomObject]@{
                Id = $Update.Identity.UpdateID
                Title = $Update.Title
                Description = $Update.Description
                UpdateType = $UpdateType
                SizeMB = [math]::Round($Update.MaxDownloadSize / 1MB, 2)
                KBArticle = $KBArticle
                SupportUrl = $SupportUrl
                IsMandatory = $Update.IsMandatory
                RequiresRestart = $Update.RebootRequired
                IsDownloaded = $Update.IsDownloaded
                IsHidden = $Update.IsHidden
            }
        }
        
        Write-Verbose "Found $($Updates.Count) available updates"
        return $Updates
    }
    catch {
        Write-Error "Failed to check for updates: $_"
        return @()
    }
}
