function Set-Better11AppPermission {
    <#
    .SYNOPSIS
        Sets an app permission.
    .DESCRIPTION
        Enables or disables a specific app permission.
    .PARAMETER Permission
        The permission to configure.
    .PARAMETER Enabled
        Whether to enable or disable the permission.
    .EXAMPLE
        Set-Better11AppPermission -Permission Camera -Enabled $false
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet('Location', 'Camera', 'Microphone', 'Notifications', 'AccountInfo', 
                     'Contacts', 'Calendar', 'PhoneCalls', 'CallHistory', 'Email', 
                     'Tasks', 'Messaging', 'Radios', 'OtherDevices', 'BackgroundApps',
                     'AppDiagnostics', 'Documents', 'Pictures', 'Videos', 'FileSystem')]
        [string]$Permission,

        [Parameter(Mandatory = $true)]
        [bool]$Enabled
    )

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

    $Action = if ($Enabled) { "Enable" } else { "Disable" }

    if ($PSCmdlet.ShouldProcess($Permission, $Action)) {
        try {
            $ConsentStore = 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore'
            
            if ($Permission -eq 'BackgroundApps') {
                $Path = 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications'
                if (-not (Test-Path $Path)) {
                    New-Item -Path $Path -Force | Out-Null
                }
                Set-ItemProperty -Path $Path -Name 'GlobalUserDisabled' -Value $(if ($Enabled) { 0 } else { 1 }) -Type DWord
            } else {
                $CapabilityName = $Mappings[$Permission]
                $Path = Join-Path $ConsentStore $CapabilityName
                
                if (-not (Test-Path $Path)) {
                    New-Item -Path $Path -Force | Out-Null
                }
                
                Set-ItemProperty -Path $Path -Name 'Value' -Value $(if ($Enabled) { 'Allow' } else { 'Deny' })
            }

            Write-Verbose "$Permission permission set to $($Enabled)"
            return [PSCustomObject]@{
                Success = $true
                Permission = $Permission
                Enabled = $Enabled
            }
        }
        catch {
            Write-Error "Failed to set permission $Permission`: $_"
            return [PSCustomObject]@{ Success = $false; Permission = $Permission; Error = $_.Exception.Message }
        }
    }
}
