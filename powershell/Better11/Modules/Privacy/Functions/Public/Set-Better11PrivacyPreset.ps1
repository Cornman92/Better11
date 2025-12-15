function Set-Better11PrivacyPreset {
    <#
    .SYNOPSIS
        Applies a privacy preset.
    .DESCRIPTION
        Applies a predefined set of privacy settings based on the selected preset.
    .PARAMETER Preset
        The preset to apply: Maximum, Balanced, or Default.
    .EXAMPLE
        Set-Better11PrivacyPreset -Preset Maximum
    #>
    [CmdletBinding(SupportsShouldProcess)]
    param(
        [Parameter(Mandatory = $true)]
        [ValidateSet('Maximum', 'Balanced', 'Default')]
        [string]$Preset
    )

    if ($PSCmdlet.ShouldProcess("Privacy Settings", "Apply $Preset preset")) {
        $Results = @{
            Preset = $Preset
            Changes = @()
            Success = $true
        }

        try {
            switch ($Preset) {
                'Maximum' {
                    # Maximum privacy
                    $Results.Changes += Set-Better11TelemetryLevel -Level Basic
                    $Results.Changes += Disable-Better11AdvertisingId
                    $Results.Changes += Disable-Better11Cortana
                    
                    # Disable all permissions
                    $Permissions = @('Location', 'Camera', 'Microphone', 'Contacts', 'Calendar', 
                                     'PhoneCalls', 'CallHistory', 'Email', 'Messaging', 'Radios',
                                     'AppDiagnostics', 'Documents', 'Pictures', 'Videos', 'FileSystem')
                    foreach ($Perm in $Permissions) {
                        $Results.Changes += Set-Better11AppPermission -Permission $Perm -Enabled $false
                    }
                }
                'Balanced' {
                    # Reasonable privacy
                    $Results.Changes += Set-Better11TelemetryLevel -Level Basic
                    $Results.Changes += Disable-Better11AdvertisingId
                    $Results.Changes += Enable-Better11Cortana
                    
                    # Enable essential permissions, disable tracking
                    Set-Better11AppPermission -Permission Location -Enabled $true | Out-Null
                    Set-Better11AppPermission -Permission Notifications -Enabled $true | Out-Null
                    Set-Better11AppPermission -Permission BackgroundApps -Enabled $true | Out-Null
                    
                    $DisablePerms = @('PhoneCalls', 'CallHistory', 'AppDiagnostics')
                    foreach ($Perm in $DisablePerms) {
                        $Results.Changes += Set-Better11AppPermission -Permission $Perm -Enabled $false
                    }
                }
                'Default' {
                    # Windows defaults
                    $Results.Changes += Set-Better11TelemetryLevel -Level Full
                    $Results.Changes += Enable-Better11AdvertisingId
                    $Results.Changes += Enable-Better11Cortana
                    
                    # Enable all permissions
                    $AllPerms = @('Location', 'Camera', 'Microphone', 'Notifications', 'AccountInfo', 
                                  'Contacts', 'Calendar', 'PhoneCalls', 'CallHistory', 'Email', 
                                  'Tasks', 'Messaging', 'Radios', 'OtherDevices', 'BackgroundApps',
                                  'AppDiagnostics', 'Documents', 'Pictures', 'Videos', 'FileSystem')
                    foreach ($Perm in $AllPerms) {
                        $Results.Changes += Set-Better11AppPermission -Permission $Perm -Enabled $true
                    }
                }
            }

            Write-Verbose "$Preset privacy preset applied"
            return [PSCustomObject]$Results
        }
        catch {
            Write-Error "Failed to apply privacy preset: $_"
            $Results.Success = $false
            $Results.Error = $_.Exception.Message
            return [PSCustomObject]$Results
        }
    }
}
