# Better11 User Guide

Complete guide to using Better11 for Windows 11 system enhancement and application management.

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Application Manager](#application-manager)
4. [System Tools](#system-tools)
5. [Advanced Usage](#advanced-usage)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)
8. [FAQ](#faq)

## Introduction

Better11 is a comprehensive Windows 11 enhancement toolkit that provides:

- **Secure application installation** with verification
- **System optimization** through registry tweaks
- **Bloatware removal** for a cleaner system
- **Service management** for better performance
- **Safety features** including automatic backups

### What You'll Learn

This guide covers:
- Installing and managing applications
- Optimizing system performance
- Customizing Windows 11
- Using safety features
- Creating custom configurations

## Getting Started

### Prerequisites

Before using Better11:

1. ✅ Windows 11 installed
2. ✅ Python 3.8+ installed
3. ✅ Administrator access available
4. ✅ Better11 downloaded and set up (see [INSTALL.md](INSTALL.md))

### Quick Start

Open Command Prompt or PowerShell as Administrator:

```bash
# Navigate to Better11 directory
cd C:\path\to\better11

# List available applications
python -m better11.cli list

# Launch GUI
python -m better11.gui
```

## Application Manager

The Application Manager provides secure installation and management of applications.

### Using the Command Line Interface

#### List Available Applications

```bash
python -m better11.cli list
```

Output example:
```
demo-appx: Demo AppX Package v1.0.0 (appx)
demo-exe: Demo EXE Installer v1.0.0 (exe)
demo-app: Demo MSI Installer v1.0.0 (msi)
```

#### Download an Application

Download without installing:

```bash
python -m better11.cli download demo-app
```

Output:
```
Downloaded to C:\Users\Username\.better11\downloads\demo-app.msi
```

#### Install an Application

Download, verify, and install in one command:

```bash
python -m better11.cli install demo-app
```

What happens:
1. ✅ Downloads installer from vetted source
2. ✅ Verifies SHA-256 hash
3. ✅ Checks HMAC signature (if configured)
4. ✅ Installs dependencies (if any)
5. ✅ Runs silent installation
6. ✅ Records installation state

#### Check Installation Status

```bash
# Status of all applications
python -m better11.cli status

# Status of specific application
python -m better11.cli status demo-app
```

Output:
```
demo-app v1.0.0: installed
```

#### Uninstall an Application

```bash
python -m better11.cli uninstall demo-app
```

The uninstall process:
1. ✅ Checks for dependent applications
2. ✅ Runs uninstall command
3. ✅ Updates installation state

#### Using Custom Catalog

```bash
python -m better11.cli --catalog my-catalog.json list
python -m better11.cli --catalog my-catalog.json install my-app
```

### Using the Graphical Interface

#### Launch GUI

```bash
python -m better11.gui
```

Or create a desktop shortcut (see [INSTALL.md](INSTALL.md)).

#### GUI Features

The GUI provides:

- **Application List**: Browse available applications
- **Download Button**: Download selected application
- **Install Button**: Download and install selected application
- **Uninstall Button**: Remove installed application
- **Status Bar**: Shows operation status and messages

#### GUI Workflow

1. **Select Application**: Click on an application in the list
2. **Choose Action**: Click Download, Install, or Uninstall
3. **Wait for Completion**: Operations run asynchronously
4. **Check Status**: Status bar shows progress and results

### Application Catalog

#### Catalog Format

Applications are defined in `better11/apps/catalog.json`:

```json
{
  "applications": [
    {
      "app_id": "7zip",
      "name": "7-Zip",
      "version": "23.01",
      "uri": "https://www.7-zip.org/a/7z2301-x64.msi",
      "sha256": "abc123...",
      "installer_type": "msi",
      "vetted_domains": ["7-zip.org"],
      "dependencies": [],
      "silent_args": ["/quiet"],
      "uninstall_command": "msiexec /x {23170F69-40C1-2702-2301-000001000000} /qn"
    }
  ]
}
```

#### Creating Custom Catalog

1. **Copy Default Catalog**:
   ```bash
   copy better11\apps\catalog.json my-catalog.json
   ```

2. **Add Your Application**:
   ```json
   {
     "app_id": "my-app",
     "name": "My Application",
     "version": "1.0.0",
     "uri": "https://example.com/installer.msi",
     "sha256": "compute_this_hash",
     "installer_type": "msi",
     "vetted_domains": ["example.com"],
     "silent_args": ["/quiet", "/norestart"]
   }
   ```

3. **Compute SHA-256 Hash**:
   ```bash
   certutil -hashfile installer.msi SHA256
   ```

4. **Use Custom Catalog**:
   ```bash
   python -m better11.cli --catalog my-catalog.json install my-app
   ```

#### Installer Types

**MSI (Microsoft Installer)**:
```json
{
  "installer_type": "msi",
  "silent_args": ["/quiet", "/norestart"],
  "uninstall_command": "msiexec /x {GUID} /qn"
}
```

**EXE (Executable)**:
```json
{
  "installer_type": "exe",
  "silent_args": ["/S", "/silent"],
  "uninstall_command": "C:\\Program Files\\App\\uninstall.exe /S"
}
```

**AppX (Windows Store App)**:
```json
{
  "installer_type": "appx",
  "silent_args": [],
  "uninstall_command": "powershell -Command \"Get-AppxPackage -Name 'PackageName' | Remove-AppxPackage\""
}
```

## System Tools

System tools require administrator privileges. Always run as Administrator.

### Registry Tweaks

#### Apply Single Registry Tweak

```python
from system_tools.registry import RegistryTweak, apply_tweak
import winreg

# Show file extensions in Explorer
tweak = RegistryTweak(
    hive="HKEY_CURRENT_USER",
    path=r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
    name="HideFileExt",
    value=0,
    value_type=winreg.REG_DWORD
)

apply_tweak(tweak)
```

#### Apply Multiple Tweaks

```python
from system_tools.registry import RegistryTweak, apply_tweaks
import winreg

tweaks = [
    # Show file extensions
    RegistryTweak(
        hive="HKEY_CURRENT_USER",
        path=r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
        name="HideFileExt",
        value=0,
        value_type=winreg.REG_DWORD
    ),
    # Show hidden files
    RegistryTweak(
        hive="HKEY_CURRENT_USER",
        path=r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
        name="Hidden",
        value=1,
        value_type=winreg.REG_DWORD
    ),
    # Disable Windows animations
    RegistryTweak(
        hive="HKEY_CURRENT_USER",
        path=r"Control Panel\Desktop\WindowMetrics",
        name="MinAnimate",
        value="0",
        value_type=winreg.REG_SZ
    )
]

apply_tweaks(tweaks, confirm=True, create_backup=True)
```

#### Registry Value Types

```python
import winreg

# Common registry types
REG_SZ = winreg.REG_SZ           # String
REG_DWORD = winreg.REG_DWORD     # 32-bit number
REG_QWORD = winreg.REG_QWORD     # 64-bit number
REG_BINARY = winreg.REG_BINARY   # Binary data
```

#### Safety Features

Registry tweaks automatically:
- ✅ Create system restore point
- ✅ Backup affected registry keys
- ✅ Prompt for user confirmation
- ✅ Log all operations

### Bloatware Removal

#### Remove Specific Packages

```python
from system_tools.bloatware import remove_bloatware

# Remove specified bloatware
packages = [
    "Microsoft.BingWeather",
    "Microsoft.GetHelp",
    "Microsoft.Getstarted",
    "Microsoft.WindowsMaps"
]

remove_bloatware(packages, confirm=True)
```

#### Common Bloatware Packages

```python
# News and Weather
bloatware_news = [
    "Microsoft.BingNews",
    "Microsoft.BingWeather"
]

# Gaming
bloatware_gaming = [
    "Microsoft.XboxApp",
    "Microsoft.XboxGameOverlay",
    "Microsoft.XboxGamingOverlay"
]

# Mixed Reality
bloatware_mixed_reality = [
    "Microsoft.MixedReality.Portal"
]

# Office
bloatware_office = [
    "Microsoft.Office.OneNote",
    "Microsoft.SkypeApp"
]

# Remove all
all_bloatware = (
    bloatware_news +
    bloatware_gaming +
    bloatware_mixed_reality +
    bloatware_office
)

remove_bloatware(all_bloatware)
```

#### Finding Package Names

To find installed AppX package names:

```powershell
# List all installed packages
Get-AppxPackage | Select-Object Name | Sort-Object Name

# Search for specific package
Get-AppxPackage | Where-Object Name -like "*Bing*"
```

### Service Management

#### Control Windows Services

```python
from system_tools.services import ServiceAction, apply_service_actions

# Define service actions
actions = [
    # Disable Windows Search
    ServiceAction(name="WSearch", action="disable"),
    
    # Stop and disable Superfetch
    ServiceAction(name="SysMain", action="stop"),
    ServiceAction(name="SysMain", action="disable"),
    
    # Disable Xbox services
    ServiceAction(name="XblAuthManager", action="disable"),
    ServiceAction(name="XblGameSave", action="disable"),
]

apply_service_actions(actions, confirm=True)
```

#### Service Actions

Available actions:
- `start` - Start the service
- `stop` - Stop the service
- `enable` - Set to start automatically
- `disable` - Prevent automatic start

#### Finding Service Names

To find service names:

```cmd
# List all services
sc query

# Get service details
sc query WSearch

# Or use PowerShell
Get-Service | Select-Object Name, DisplayName, Status
```

### Performance Presets

#### Create Performance Preset

```python
from system_tools.performance import PerformancePreset, apply_performance_preset
from system_tools.registry import RegistryTweak
from system_tools.services import ServiceAction
import winreg

# Create gaming performance preset
gaming_preset = PerformancePreset(
    name="Gaming Performance",
    description="Optimize system for gaming",
    registry_tweaks=[
        # Disable visual effects
        RegistryTweak(
            hive="HKEY_CURRENT_USER",
            path=r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects",
            name="VisualFXSetting",
            value=2,
            value_type=winreg.REG_DWORD
        ),
        # Disable transparency
        RegistryTweak(
            hive="HKEY_CURRENT_USER",
            path=r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
            name="EnableTransparency",
            value=0,
            value_type=winreg.REG_DWORD
        ),
    ],
    service_actions=[
        # Disable unnecessary services
        ServiceAction(name="WSearch", action="disable"),
        ServiceAction(name="SysMain", action="disable"),
    ]
)

# Apply preset
apply_performance_preset(gaming_preset, confirm=True)
```

#### Predefined Presets

```python
# Privacy-focused preset
privacy_preset = PerformancePreset(
    name="Privacy Enhanced",
    registry_tweaks=[
        # Disable telemetry
        RegistryTweak(
            hive="HKEY_LOCAL_MACHINE",
            path=r"SOFTWARE\Policies\Microsoft\Windows\DataCollection",
            name="AllowTelemetry",
            value=0,
            value_type=winreg.REG_DWORD
        ),
    ]
)

# Performance preset
performance_preset = PerformancePreset(
    name="Maximum Performance",
    service_actions=[
        ServiceAction(name="WSearch", action="disable"),
        ServiceAction(name="Themes", action="disable"),
    ]
)
```

### Safety Utilities

#### Ensure Windows Platform

```python
from system_tools.safety import ensure_windows

try:
    ensure_windows()
    print("Running on Windows")
except SafetyError:
    print("Not running on Windows")
```

#### User Confirmation

```python
from system_tools.safety import confirm_action

if confirm_action("Apply these changes?"):
    # Proceed with operation
    print("User confirmed")
else:
    print("User cancelled")
```

#### Create Restore Point

```python
from system_tools.safety import create_restore_point

create_restore_point("Before Better11 modifications")
```

#### Backup Registry Key

```python
from system_tools.safety import backup_registry_key
from pathlib import Path

# Backup to temporary file
backup_path = backup_registry_key(r"HKCU\Software\Microsoft\Windows")

# Backup to specific location
backup_path = backup_registry_key(
    r"HKCU\Software\Microsoft\Windows",
    destination=Path("C:/Backups/registry_backup.reg")
)

print(f"Registry backed up to: {backup_path}")
```

## Advanced Usage

### Scripting and Automation

#### Automated Application Installation

```python
from pathlib import Path
from better11.apps.manager import AppManager

# Initialize manager
catalog_path = Path("better11/apps/catalog.json")
manager = AppManager(catalog_path)

# Install multiple applications
apps_to_install = ["7zip", "notepadpp", "vlc"]

for app_id in apps_to_install:
    try:
        print(f"Installing {app_id}...")
        status, result = manager.install(app_id)
        print(f"✓ Installed {app_id} v{status.version}")
    except Exception as e:
        print(f"✗ Failed to install {app_id}: {e}")
```

#### Batch System Optimization

```python
from system_tools.registry import RegistryTweak, apply_tweaks
from system_tools.services import ServiceAction, apply_service_actions
from system_tools.bloatware import remove_bloatware
import winreg

# Define all optimizations
registry_tweaks = [
    RegistryTweak("HKEY_CURRENT_USER", r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "HideFileExt", 0, winreg.REG_DWORD),
    RegistryTweak("HKEY_CURRENT_USER", r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "Hidden", 1, winreg.REG_DWORD),
]

service_actions = [
    ServiceAction("WSearch", "disable"),
    ServiceAction("SysMain", "disable"),
]

bloatware = [
    "Microsoft.BingWeather",
    "Microsoft.BingNews",
]

# Apply all at once
print("Applying registry tweaks...")
apply_tweaks(registry_tweaks, confirm=False, create_backup=True)

print("Configuring services...")
apply_service_actions(service_actions, confirm=False)

print("Removing bloatware...")
remove_bloatware(bloatware, confirm=False)

print("Optimization complete!")
```

### Custom Download Verification

```python
from pathlib import Path
from better11.apps.verification import DownloadVerifier
from better11.apps.models import AppMetadata, InstallerType

# Create verifier
verifier = DownloadVerifier()

# Verify hash only
file_path = Path("downloads/installer.msi")
expected_hash = "abc123..."
verifier.verify_hash(file_path, expected_hash)

# Verify with signature
metadata = AppMetadata(
    app_id="custom-app",
    name="Custom App",
    version="1.0",
    uri="https://example.com/installer.msi",
    sha256="abc123...",
    installer_type=InstallerType.MSI,
    signature="base64_signature",
    signature_key="base64_key"
)
verifier.verify(metadata, file_path)
```

### Working with Installation State

```python
from pathlib import Path
from better11.apps.state_store import InstallationStateStore

# Initialize state store
state_file = Path.home() / ".better11" / "installed.json"
state_store = InstallationStateStore(state_file)

# Mark application as installed
status = state_store.mark_installed(
    app_id="my-app",
    version="1.0.0",
    installer_path=Path("downloads/installer.msi"),
    dependencies=["dependency-app"]
)

# Check installation status
status = state_store.get("my-app")
if status and status.installed:
    print(f"{status.app_id} v{status.version} is installed")

# List all installed applications
all_status = state_store.list()
for status in all_status:
    if status.installed:
        print(f"- {status.app_id} v{status.version}")

# Mark as uninstalled
state_store.mark_uninstalled("my-app")
```

## Best Practices

### Safety First

1. **Create Backups**: Always create system restore point before major changes
2. **Test in VM**: Test new configurations in a virtual machine first
3. **One Change at a Time**: Apply changes incrementally for easier troubleshooting
4. **Document Changes**: Keep track of modifications made

### Application Management

1. **Verify Hashes**: Always verify SHA-256 hashes match expected values
2. **Use Vetted Sources**: Only download from trusted, vetted domains
3. **Check Dependencies**: Review dependencies before installation
4. **Keep Catalog Updated**: Regularly update catalog with new versions

### System Modifications

1. **Backup Registry**: Let Better11 create automatic backups
2. **User Confirmation**: Keep confirmation prompts enabled for destructive operations
3. **Review Actions**: Review all registry tweaks and service changes before applying
4. **Restore Points**: Create restore points before major system changes

### Performance

1. **Start Conservative**: Begin with minimal changes
2. **Monitor Impact**: Observe system behavior after changes
3. **Revert if Needed**: Use restore points if issues occur
4. **Document Baseline**: Note system performance before modifications

## Troubleshooting

### Application Installation Issues

**Problem**: Download fails

```
Solution:
1. Check internet connection
2. Verify URL in catalog is correct
3. Check domain is in vetted_domains list
4. Try downloading manually to test URL
```

**Problem**: Hash verification fails

```
Solution:
1. Re-download the file
2. Verify the SHA-256 hash in catalog is correct
3. Check for file corruption
4. Update catalog with current hash
```

**Problem**: Installation fails

```
Solution:
1. Run as Administrator
2. Check installer type is correct (msi/exe/appx)
3. Verify silent_args are correct for installer
4. Check installer logs (usually in %TEMP%)
5. Try manual installation to test installer
```

### System Tools Issues

**Problem**: Registry tweak fails

```
Solution:
1. Run as Administrator
2. Verify registry path is correct
3. Check value_type matches expected type
4. Ensure registry key exists (create if needed)
5. Check for Group Policy restrictions
```

**Problem**: Service modification fails

```
Solution:
1. Run as Administrator
2. Verify service name is correct
3. Check service exists: sc query ServiceName
4. Verify service is not protected by system
5. Check for dependencies that prevent changes
```

**Problem**: Bloatware removal fails

```
Solution:
1. Run as Administrator
2. Verify package name is correct
3. Check package is installed: Get-AppxPackage
4. Some packages may be protected (system apps)
5. Use verbose output to see detailed error
```

### General Issues

**Problem**: Permission denied errors

```
Solution:
Always run Command Prompt or PowerShell as Administrator:
1. Right-click on icon
2. Select "Run as Administrator"
3. Navigate to Better11 directory
4. Run commands
```

**Problem**: Module not found

```
Solution:
1. Verify you're in Better11 directory
2. Check Python path is correct
3. Try: python -c "import better11"
4. Reinstall if needed
```

## FAQ

### General Questions

**Q: Is Better11 safe to use?**

A: Better11 includes multiple safety features including hash verification, automatic backups, restore point creation, and user confirmation prompts. However, always test in a VM first and create backups.

**Q: Does Better11 require internet?**

A: Internet is required for downloading applications. System tools work offline.

**Q: Can I use Better11 on Windows 10?**

A: Some features may work on Windows 10 21H2+, but Better11 is designed for Windows 11.

**Q: Is administrator access required?**

A: Yes, for most features including application installation and system modifications.

### Application Manager Questions

**Q: How do I add my own applications?**

A: Create a custom catalog JSON file with your application details including SHA-256 hash and use `--catalog` flag.

**Q: Can Better11 update installed applications?**

A: Currently, you need to uninstall the old version and install the new version. Automatic updates are planned.

**Q: What happens if installation fails mid-way?**

A: Better11 tracks installation state. You can retry installation or manually clean up using Windows Settings.

### System Tools Questions

**Q: Can I undo registry changes?**

A: Yes, Better11 creates registry backups (`.reg` files) that can be imported to restore previous values. System restore points can also revert changes.

**Q: Will removed bloatware come back after Windows updates?**

A: Some Windows updates may reinstall removed packages. You may need to run bloatware removal again after major updates.

**Q: Can service changes break my system?**

A: Disabling critical services can cause issues. Better11 includes safety checks, but research services before disabling them.

### Technical Questions

**Q: Where are downloaded installers stored?**

A: Downloaded files are stored in `C:\Users\YourUsername\.better11\downloads\`

**Q: Where is installation state tracked?**

A: Installation state is stored in `C:\Users\YourUsername\.better11\installed.json`

**Q: Can I run Better11 from a USB drive?**

A: Yes, Better11 is portable. Copy the directory to USB and run from there. State files will still be in `~/.better11/` unless configured otherwise.

**Q: Does Better11 collect data?**

A: No, Better11 does not collect or transmit any user data. All operations are local.

## Support and Resources

- **Documentation**: [API_REFERENCE.md](API_REFERENCE.md), [ARCHITECTURE.md](ARCHITECTURE.md)
- **Installation**: [INSTALL.md](INSTALL.md)
- **Contributing**: [CONTRIBUTING.md](CONTRIBUTING.md)
- **Security**: [SECURITY.md](SECURITY.md)
- **Issues**: [GitHub Issues](https://github.com/owner/better11/issues)
- **Discussions**: [GitHub Discussions](https://github.com/owner/better11/discussions)

## Next Steps

Now that you've learned the basics:

1. Try installing an application using the CLI
2. Launch the GUI and explore the interface
3. Test a simple registry tweak in a VM
4. Create a custom application catalog
5. Build a performance preset for your needs
6. Contribute improvements back to the project

Happy customizing! 🚀
