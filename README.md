# Better11

Better11 is an all-around Windows 11 system enhancer that provides tools for live system customization, offline image editing, and streamlined application downloads/installs.

## Prerequisites
- **Supported OS:** Windows 11 (build 22621/22H2 or newer). Earlier builds may have limited DISM feature support.
- **Permissions:** Run shells and scripts as an administrator to access DISM, registry, and protected file system locations.
- **Required components:**
  - PowerShell 5.1+ (or PowerShell 7) with execution policy that allows running local scripts.
  - Deployment Image Servicing and Management (**DISM**) available in the system PATH.
  - Access to Windows image formats (WIM/ESD/ISO) for offline editing.
  - Internet access for downloading application installers.

## Installation
1. Clone or download the repository onto the Windows machine that will run the tools.
2. Open **PowerShell as Administrator** in the project directory.
3. Review scripts before running them and unblock if needed (`Unblock-File .\script.ps1`).
4. Adjust the PowerShell execution policy if required (e.g., `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`).
5. Confirm DISM is available by running `dism /?` and verifying the help output.

## Usage Examples
These sample commands illustrate the expected flows. Replace placeholders with actual file paths.

### Live image editing
Run from an elevated PowerShell session to make changes to the currently running Windows installation:
```powershell
# Add a capability or package live
DISM /Online /Add-Capability /CapabilityName:Rsat.ActiveDirectory.DS-LDS.Tools~~~~0.0.1.0

# Enable a Windows feature live
DISM /Online /Enable-Feature /FeatureName:NetFx3 /All
```

### Offline image editing
Mount a Windows image, apply changes, and commit them:
```powershell
# Mount the image
$dismMount = "C:\\Mount"
$imagePath = "D:\\sources\\install.wim"
DISM /Mount-WIM /WimFile:$imagePath /Index:1 /MountDir:$dismMount

# Add packages, drivers, or registry tweaks to the mounted image
DISM /Image:$dismMount /Add-Package /PackagePath:"D:\\updates\\kb.msu"
DISM /Image:$dismMount /Add-Driver /Driver:"D:\\drivers" /Recurse

# Commit changes and unmount
DISM /Unmount-WIM /MountDir:$dismMount /Commit
```

### Application download and install flow
Use PowerShell to download and run installers. Validate sources and checksums before execution:
```powershell
# Download installer
$installer = "C:\\Temp\\app-setup.exe"
Invoke-WebRequest -Uri "https://example.com/app-setup.exe" -OutFile $installer

# (Optional) Verify checksum
Get-FileHash $installer -Algorithm SHA256

# Install silently if supported
Start-Process -FilePath $installer -ArgumentList "/quiet" -Wait -Verb RunAs
```

## Warnings and backups
- **Back up first:** Create a system restore point or full image backup before modifying live systems.
- **Offline images:** Keep a copy of the original WIM/ESD before servicing; work on duplicates where possible.
- **Administrator context:** Running without elevation will cause many operations to fail or partially apply.
- **Disk space:** Mounting images and staging installers requires several gigabytes of free space.
- **Integrity:** Verify installer authenticity (hash/signature) and only use trusted download sources.

## Module and script references
Links to modules or scripts will be added here as they are introduced (e.g., `docs/`, `scripts/`, or PowerShell module paths) to provide quick navigation to tooling once available.
