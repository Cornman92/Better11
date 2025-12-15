<#
.SYNOPSIS
    Better11 Privacy Module - Privacy and telemetry control
.DESCRIPTION
    Comprehensive control over Windows privacy settings, telemetry collection,
    app permissions, and privacy presets.
#>

$script:ModuleRoot = $PSScriptRoot

# Privacy settings registry paths
$script:TelemetryPath = 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\DataCollection'
$script:AdvertisingPath = 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo'
$script:CortanaPath = 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\Windows Search'
$script:ConsentStorePath = 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore'

# App permission mappings
$script:AppPermissions = @{
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

# Import public functions
$PublicFunctions = @(Get-ChildItem -Path "$PSScriptRoot\Functions\Public\*.ps1" -ErrorAction SilentlyContinue)
foreach ($Function in $PublicFunctions) {
    try {
        . $Function.FullName
        Export-ModuleMember -Function $Function.BaseName
    } catch {
        Write-Error "Failed to import function $($Function.FullName): $_"
    }
}

Write-Verbose "Better11 Privacy module loaded"
