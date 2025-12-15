function Get-Better11InstalledApps {
    <#
    .SYNOPSIS
        Lists installed applications.

    .DESCRIPTION
        Retrieves a list of installed applications from the Windows Registry (HKLM and HKCU).

    .EXAMPLE
        Get-Better11InstalledApps
        Lists all installed applications.
    #>
    [CmdletBinding()]
    param()

    process {
        Write-Better11Log -Message "Listing installed applications..." -Level "INFO"

        $apps = @()
        $paths = @(
            "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*",
            "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*",
            "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*"
        )

        foreach ($path in $paths) {
            $keys = Get-ItemProperty $path -ErrorAction SilentlyContinue
            foreach ($key in $keys) {
                if ($key.DisplayName) {
                    $apps += [PSCustomObject]@{
                        DisplayName = $key.DisplayName
                        DisplayVersion = $key.DisplayVersion
                        Publisher = $key.Publisher
                        InstallDate = $key.InstallDate
                        UninstallString = $key.UninstallString
                        InstallLocation = $key.InstallLocation
                    }
                }
            }
        }

        # Remove duplicates
        $apps = $apps | Sort-Object DisplayName -Unique

        Write-Better11Log -Message "Found $(@($apps).Count) installed applications" -Level "INFO"
        return $apps
    }
}
