function Install-Better11Updates {
    <#
    .SYNOPSIS
        Installs Windows updates.
    .DESCRIPTION
        Downloads and installs available Windows updates.
    .PARAMETER UpdateIds
        Specific update IDs to install. If not specified, installs all available.
    .PARAMETER NoRestart
        Prevent automatic restart after installation.
    .EXAMPLE
        Install-Better11Updates
    .EXAMPLE
        Install-Better11Updates -UpdateIds @("update-id-1", "update-id-2")
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter()]
        [string[]]$UpdateIds,

        [Parameter()]
        [switch]$NoRestart
    )

    if ($PSCmdlet.ShouldProcess("Windows Updates", "Install")) {
        try {
            Write-Verbose "Installing Windows updates..."
            
            $Session = New-Object -ComObject Microsoft.Update.Session
            $Searcher = $Session.CreateUpdateSearcher()
            $SearchResult = $Searcher.Search("IsInstalled=0 and IsHidden=0")
            
            $UpdatesToInstall = New-Object -ComObject Microsoft.Update.UpdateColl
            
            foreach ($Update in $SearchResult.Updates) {
                if ($UpdateIds -and $UpdateIds.Count -gt 0) {
                    if ($Update.Identity.UpdateID -in $UpdateIds) {
                        $UpdatesToInstall.Add($Update) | Out-Null
                    }
                } else {
                    $UpdatesToInstall.Add($Update) | Out-Null
                }
            }
            
            if ($UpdatesToInstall.Count -eq 0) {
                Write-Verbose "No updates to install"
                return [PSCustomObject]@{
                    Success = $true
                    Message = "No updates to install"
                    UpdatesInstalled = 0
                    RebootRequired = $false
                }
            }
            
            Write-Verbose "Downloading $($UpdatesToInstall.Count) updates..."
            $Downloader = $Session.CreateUpdateDownloader()
            $Downloader.Updates = $UpdatesToInstall
            $DownloadResult = $Downloader.Download()
            
            if ($DownloadResult.ResultCode -ne 2) {
                throw "Download failed with result code: $($DownloadResult.ResultCode)"
            }
            
            Write-Verbose "Installing $($UpdatesToInstall.Count) updates..."
            $Installer = $Session.CreateUpdateInstaller()
            $Installer.Updates = $UpdatesToInstall
            $InstallResult = $Installer.Install()
            
            return [PSCustomObject]@{
                Success = ($InstallResult.ResultCode -eq 2)
                Message = if ($InstallResult.ResultCode -eq 2) { "Installation successful" } else { "Installation completed with warnings" }
                UpdatesInstalled = $UpdatesToInstall.Count
                RebootRequired = $InstallResult.RebootRequired
            }
        }
        catch {
            Write-Error "Failed to install updates: $_"
            return [PSCustomObject]@{
                Success = $false
                Message = $_.Exception.Message
                UpdatesInstalled = 0
                RebootRequired = $false
            }
        }
    }
}
