<#
.SYNOPSIS
    Windows bloatware removal and management.

.DESCRIPTION
    Provides functionality to identify and remove pre-installed Windows apps
    and bloatware that consume resources.
#>

using module .\Base.psm1
using module .\Safety.psm1

# Bloatware app information
class BloatwareApp {
    [string]$Name
    [string]$PackageName
    [string]$Category
    [string]$Description
    [bool]$SafeToRemove
    [bool]$IsInstalled
    
    BloatwareApp(
        [string]$Name,
        [string]$PackageName,
        [string]$Category,
        [string]$Description,
        [bool]$SafeToRemove
    ) {
        $this.Name = $Name
        $this.PackageName = $PackageName
        $this.Category = $Category
        $this.Description = $Description
        $this.SafeToRemove = $SafeToRemove
        $this.IsInstalled = $false
    }
}

# Bloatware Manager class
class BloatwareManager : SystemTool {
    [System.Collections.Generic.List[BloatwareApp]]$BloatwareApps
    
    BloatwareManager([hashtable]$Config = @{}, [bool]$DryRun = $false) : base($Config, $DryRun) {
        $this.BloatwareApps = [System.Collections.Generic.List[BloatwareApp]]::new()
        $this.InitializeBloatwareList()
    }
    
    [ToolMetadata] GetMetadata() {
        return [ToolMetadata]::new(
            "Bloatware Manager",
            "Remove unnecessary pre-installed Windows apps",
            "0.3.0"
        )
    }
    
    [void] ValidateEnvironment() {
        Test-WindowsPlatform
        Assert-AdminPrivileges "Bloatware removal requires administrator privileges"
    }
    
    [bool] Execute() {
        $apps = $this.ListInstalledBloatware()
        $this.Log("Found $($apps.Count) bloatware apps installed")
        return $true
    }
    
    # Initialize bloatware list
    [void] InitializeBloatwareList() {
        # Microsoft apps
        $this.BloatwareApps.Add([BloatwareApp]::new(
            "3D Builder",
            "Microsoft.3DBuilder",
            "3d",
            "3D modeling app",
            $true
        ))
        
        $this.BloatwareApps.Add([BloatwareApp]::new(
            "3D Viewer",
            "Microsoft.Microsoft3DViewer",
            "3d",
            "3D file viewer",
            $true
        ))
        
        $this.BloatwareApps.Add([BloatwareApp]::new(
            "Bing Weather",
            "Microsoft.BingWeather",
            "microsoft",
            "Weather app",
            $true
        ))
        
        $this.BloatwareApps.Add([BloatwareApp]::new(
            "Bing News",
            "Microsoft.BingNews",
            "microsoft",
            "News aggregator",
            $true
        ))
        
        $this.BloatwareApps.Add([BloatwareApp]::new(
            "Bing Finance",
            "Microsoft.BingFinance",
            "microsoft",
            "Finance tracker",
            $true
        ))
        
        $this.BloatwareApps.Add([BloatwareApp]::new(
            "Bing Sports",
            "Microsoft.BingSports",
            "microsoft",
            "Sports news",
            $true
        ))
        
        $this.BloatwareApps.Add([BloatwareApp]::new(
            "Get Help",
            "Microsoft.GetHelp",
            "microsoft",
            "Help app",
            $true
        ))
        
        $this.BloatwareApps.Add([BloatwareApp]::new(
            "Get Started",
            "Microsoft.Getstarted",
            "microsoft",
            "Welcome app",
            $true
        ))
        
        $this.BloatwareApps.Add([BloatwareApp]::new(
            "Messaging",
            "Microsoft.Messaging",
            "microsoft",
            "Messaging app",
            $true
        ))
        
        $this.BloatwareApps.Add([BloatwareApp]::new(
            "Office Hub",
            "Microsoft.MicrosoftOfficeHub",
            "microsoft",
            "Office launcher",
            $true
        ))
        
        $this.BloatwareApps.Add([BloatwareApp]::new(
            "OneNote",
            "Microsoft.Office.OneNote",
            "microsoft",
            "Note taking app",
            $true
        ))
        
        $this.BloatwareApps.Add([BloatwareApp]::new(
            "People",
            "Microsoft.People",
            "microsoft",
            "Contacts app",
            $true
        ))
        
        $this.BloatwareApps.Add([BloatwareApp]::new(
            "Print 3D",
            "Microsoft.Print3D",
            "3d",
            "3D printing app",
            $true
        ))
        
        $this.BloatwareApps.Add([BloatwareApp]::new(
            "Skype",
            "Microsoft.SkypeApp",
            "microsoft",
            "Skype UWP app",
            $true
        ))
        
        $this.BloatwareApps.Add([BloatwareApp]::new(
            "Solitaire Collection",
            "Microsoft.MicrosoftSolitaireCollection",
            "games",
            "Card games",
            $true
        ))
        
        $this.BloatwareApps.Add([BloatwareApp]::new(
            "Sticky Notes",
            "Microsoft.MicrosoftStickyNotes",
            "microsoft",
            "Sticky notes app",
            $true
        ))
        
        $this.BloatwareApps.Add([BloatwareApp]::new(
            "Tips",
            "Microsoft.WindowsFeedbackHub",
            "microsoft",
            "Feedback app",
            $true
        ))
        
        $this.BloatwareApps.Add([BloatwareApp]::new(
            "Voice Recorder",
            "Microsoft.WindowsSoundRecorder",
            "microsoft",
            "Sound recorder",
            $true
        ))
        
        $this.BloatwareApps.Add([BloatwareApp]::new(
            "Mixed Reality Portal",
            "Microsoft.MixedReality.Portal",
            "microsoft",
            "VR/AR portal",
            $true
        ))
        
        # Xbox apps
        $this.BloatwareApps.Add([BloatwareApp]::new(
            "Xbox",
            "Microsoft.XboxApp",
            "xbox",
            "Xbox app",
            $true
        ))
        
        $this.BloatwareApps.Add([BloatwareApp]::new(
            "Xbox Game Bar",
            "Microsoft.XboxGamingOverlay",
            "xbox",
            "Game overlay",
            $true
        ))
        
        $this.BloatwareApps.Add([BloatwareApp]::new(
            "Xbox Identity Provider",
            "Microsoft.XboxIdentityProvider",
            "xbox",
            "Xbox auth",
            $true
        ))
        
        $this.BloatwareApps.Add([BloatwareApp]::new(
            "Xbox Speech",
            "Microsoft.XboxSpeechToTextOverlay",
            "xbox",
            "Xbox voice",
            $true
        ))
        
        # Third-party bloatware (OEM)
        $this.BloatwareApps.Add([BloatwareApp]::new(
            "Candy Crush",
            "king.com.CandyCrushSaga",
            "games",
            "Game (ads)",
            $true
        ))
        
        $this.BloatwareApps.Add([BloatwareApp]::new(
            "Candy Crush Soda",
            "king.com.CandyCrushSodaSaga",
            "games",
            "Game (ads)",
            $true
        ))
        
        $this.BloatwareApps.Add([BloatwareApp]::new(
            "Disney Magic Kingdoms",
            "*.DisneyMagicKingdoms",
            "games",
            "Game (ads)",
            $true
        ))
        
        $this.BloatwareApps.Add([BloatwareApp]::new(
            "March of Empires",
            "*.MarchofEmpires",
            "games",
            "Game (ads)",
            $true
        ))
        
        $this.BloatwareApps.Add([BloatwareApp]::new(
            "Spotify",
            "SpotifyAB.SpotifyMusic",
            "media",
            "Music (ads in free version)",
            $true
        ))
    }
    
    # List installed bloatware
    [BloatwareApp[]] ListInstalledBloatware() {
        $installed = [System.Collections.Generic.List[BloatwareApp]]::new()
        
        foreach ($app in $this.BloatwareApps) {
            try {
                $package = Get-AppxPackage -Name $app.PackageName -ErrorAction SilentlyContinue
                
                if ($package) {
                    $app.IsInstalled = $true
                    $installed.Add($app)
                }
            }
            catch {
                # Package doesn't exist
            }
        }
        
        $this.Log("Found $($installed.Count) bloatware apps installed")
        return $installed.ToArray()
    }
    
    # Remove a bloatware app
    [bool] RemoveApp([BloatwareApp]$App) {
        if ($this.DryRun) {
            $this.Log("DRY RUN: Would remove $($App.Name)")
            return $true
        }
        
        if (-not $App.SafeToRemove) {
            $this.LogWarning("App $($App.Name) is not marked as safe to remove")
            return $false
        }
        
        try {
            $this.Log("Removing bloatware app: $($App.Name)")
            
            # Remove for current user
            Get-AppxPackage -Name $App.PackageName -ErrorAction Stop | Remove-AppxPackage -ErrorAction Stop
            
            # Remove provisioned package (prevents reinstall for new users)
            try {
                Get-AppxProvisionedPackage -Online -ErrorAction SilentlyContinue |
                    Where-Object { $_.DisplayName -eq $App.PackageName } |
                    Remove-AppxProvisionedPackage -Online -ErrorAction Stop
            }
            catch {
                $this.LogWarning("Could not remove provisioned package: $_")
            }
            
            $this.Log("Removed: $($App.Name)")
            return $true
        }
        catch {
            $this.LogError("Failed to remove $($App.Name): $_")
            return $false
        }
    }
    
    # Remove multiple apps
    [hashtable] RemoveApps([string[]]$AppNames = $null, [string]$Category = $null) {
        $results = @{
            Success = [System.Collections.Generic.List[string]]::new()
            Failed = [System.Collections.Generic.List[string]]::new()
            Skipped = [System.Collections.Generic.List[string]]::new()
        }
        
        $installedApps = $this.ListInstalledBloatware()
        
        foreach ($app in $installedApps) {
            # Filter by app names if specified
            if ($AppNames -and $app.Name -notin $AppNames) {
                $results.Skipped.Add($app.Name)
                continue
            }
            
            # Filter by category if specified
            if ($Category -and $app.Category -ne $Category) {
                $results.Skipped.Add($app.Name)
                continue
            }
            
            if ($this.RemoveApp($app)) {
                $results.Success.Add($app.Name)
            }
            else {
                $results.Failed.Add($app.Name)
            }
        }
        
        return $results
    }
    
    # Remove all safe bloatware
    [hashtable] RemoveAllBloatware() {
        return $this.RemoveApps()
    }
}

# Convenience functions
function Get-BloatwareApps {
    <#
    .SYNOPSIS
        List installed bloatware apps
    
    .PARAMETER Category
        Filter by category (microsoft, xbox, games, etc.)
    
    .EXAMPLE
        Get-BloatwareApps
        Get-BloatwareApps -Category xbox
    #>
    [CmdletBinding()]
    param(
        [string]$Category
    )
    
    $manager = [BloatwareManager]::new()
    $apps = $manager.ListInstalledBloatware()
    
    if ($Category) {
        $apps = $apps | Where-Object { $_.Category -eq $Category }
    }
    
    return $apps
}

function Remove-BloatwareApp {
    <#
    .SYNOPSIS
        Remove a specific bloatware app
    
    .PARAMETER Name
        Name of the app to remove
    
    .EXAMPLE
        Remove-BloatwareApp -Name "Candy Crush"
    #>
    [CmdletBinding(SupportsShouldProcess=$true, ConfirmImpact='High')]
    param(
        [Parameter(Mandatory=$true)]
        [string]$Name
    )
    
    $manager = [BloatwareManager]::new()
    $apps = $manager.ListInstalledBloatware()
    $app = $apps | Where-Object { $_.Name -eq $Name } | Select-Object -First 1
    
    if (-not $app) {
        throw "Bloatware app not found: $Name"
    }
    
    if ($PSCmdlet.ShouldProcess($app.Name, "Remove bloatware app")) {
        return $manager.RemoveApp($app)
    }
}

function Remove-AllBloatware {
    <#
    .SYNOPSIS
        Remove all detected bloatware apps
    
    .PARAMETER Category
        Only remove apps from specific category
    
    .EXAMPLE
        Remove-AllBloatware
        Remove-AllBloatware -Category xbox
    #>
    [CmdletBinding(SupportsShouldProcess=$true, ConfirmImpact='High')]
    param(
        [string]$Category
    )
    
    if ($PSCmdlet.ShouldProcess("All bloatware apps", "Remove")) {
        $manager = [BloatwareManager]::new()
        return $manager.RemoveApps($null, $Category)
    }
}

Export-ModuleMember -Function Get-BloatwareApps, Remove-BloatwareApp, Remove-AllBloatware
