function Get-Better11AllPermissions {
    <#
    .SYNOPSIS
        Gets the status of all app permissions.
    .DESCRIPTION
        Retrieves the current state of all available app permissions.
    .EXAMPLE
        Get-Better11AllPermissions
    #>
    [CmdletBinding()]
    param()

    $AllPermissions = @(
        'Location', 'Camera', 'Microphone', 'Notifications', 'AccountInfo', 
        'Contacts', 'Calendar', 'PhoneCalls', 'CallHistory', 'Email', 
        'Tasks', 'Messaging', 'Radios', 'OtherDevices', 'BackgroundApps',
        'AppDiagnostics', 'Documents', 'Pictures', 'Videos', 'FileSystem'
    )

    $Results = foreach ($Permission in $AllPermissions) {
        Get-Better11AppPermission -Permission $Permission
    }

    return $Results
}
