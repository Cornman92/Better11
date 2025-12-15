function Get-Better11AppPermission {
    <#
    .SYNOPSIS
        Gets the status of an app permission.
    .DESCRIPTION
        Retrieves whether a specific app permission is allowed or denied.
    .PARAMETER Permission
        The permission to check.
    .EXAMPLE
        Get-Better11AppPermission -Permission Camera
    #>
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet('Location', 'Camera', 'Microphone', 'Notifications', 'AccountInfo', 
                     'Contacts', 'Calendar', 'PhoneCalls', 'CallHistory', 'Email', 
                     'Tasks', 'Messaging', 'Radios', 'OtherDevices', 'BackgroundApps',
                     'AppDiagnostics', 'Documents', 'Pictures', 'Videos', 'FileSystem')]
        [string]$Permission
    )

    try {
        $ConsentStore = 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore'
        
        $Mappings = @{
            'Location' = 'location'
            'Camera' = 'webcam'
            'Microphone' = 'microphone'
            'Notifications' = 'userNotificationListener'
            'AccountInfo' = 'userAccountInformation'
            'Contacts' = 'contacts'
            'Calendar' = 'appointments'
            'PhoneCalls' = 'phoneCall'
            'CallHistory' = 'phoneCallHistory'
            'Email' = 'email'
            'Tasks' = 'userDataTasks'
            'Messaging' = 'chat'
            'Radios' = 'radios'
            'OtherDevices' = 'bluetoothSync'
            'BackgroundApps' = 'backgroundApps'
            'AppDiagnostics' = 'appDiagnostics'
            'Documents' = 'documentsLibrary'
            'Pictures' = 'picturesLibrary'
            'Videos' = 'videosLibrary'
            'FileSystem' = 'broadFileSystemAccess'
        }

        $CapabilityName = $Mappings[$Permission]
        $Path = Join-Path $ConsentStore $CapabilityName

        if ($Permission -eq 'BackgroundApps') {
            $Path = 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications'
            $Value = Get-ItemProperty -Path $Path -Name 'GlobalUserDisabled' -ErrorAction SilentlyContinue
            $Enabled = if ($Value) { $Value.GlobalUserDisabled -eq 0 } else { $true }
        } else {
            $Value = Get-ItemProperty -Path $Path -Name 'Value' -ErrorAction SilentlyContinue
            $Enabled = if ($Value) { $Value.Value -eq 'Allow' } else { $true }
        }

        return [PSCustomObject]@{
            Permission = $Permission
            Enabled = $Enabled
            Status = if ($Enabled) { 'Allowed' } else { 'Denied' }
        }
    }
    catch {
        Write-Warning "Failed to get permission $Permission`: $_"
        return [PSCustomObject]@{ Permission = $Permission; Enabled = $true; Status = 'Unknown' }
    }
}
