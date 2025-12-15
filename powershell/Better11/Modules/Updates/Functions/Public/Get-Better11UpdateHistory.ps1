function Get-Better11UpdateHistory {
    <#
    .SYNOPSIS
        Gets Windows Update history.
    .DESCRIPTION
        Retrieves the history of installed Windows updates.
    .PARAMETER Days
        Number of days of history to retrieve.
    .PARAMETER Count
        Maximum number of entries to return.
    .EXAMPLE
        Get-Better11UpdateHistory -Days 30
    #>
    [CmdletBinding()]
    param(
        [Parameter()]
        [int]$Days = 30,

        [Parameter()]
        [int]$Count = 50
    )

    try {
        $Session = New-Object -ComObject Microsoft.Update.Session
        $Searcher = $Session.CreateUpdateSearcher()
        $HistoryCount = $Searcher.GetTotalHistoryCount()
        
        if ($HistoryCount -eq 0) {
            return @()
        }
        
        $History = $Searcher.QueryHistory(0, [math]::Min($HistoryCount, $Count))
        $CutoffDate = (Get-Date).AddDays(-$Days)
        
        $Updates = foreach ($Entry in $History) {
            if ($Entry.Date -lt $CutoffDate) { continue }
            
            $KBMatch = [regex]::Match($Entry.Title, "KB(\d+)")
            $KBArticle = if ($KBMatch.Success) { "KB$($KBMatch.Groups[1].Value)" } else { "" }
            
            [PSCustomObject]@{
                Id = $Entry.UpdateIdentity.UpdateID
                Title = $Entry.Title
                Description = $Entry.Description
                InstallDate = $Entry.Date
                Status = switch ($Entry.ResultCode) {
                    0 { 'NotStarted' }
                    1 { 'InProgress' }
                    2 { 'Installed' }
                    3 { 'InstalledWithErrors' }
                    4 { 'Failed' }
                    5 { 'Aborted' }
                    default { 'Unknown' }
                }
                KBArticle = $KBArticle
                SupportUrl = $Entry.SupportUrl
            }
        }
        
        return $Updates
    }
    catch {
        Write-Error "Failed to get update history: $_"
        return @()
    }
}
