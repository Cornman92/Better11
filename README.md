# Better11

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform: Windows 11](https://img.shields.io/badge/platform-Windows%2011-blue.svg)](https://www.microsoft.com/windows)

An all-around Windows 11 system enhancement toolkit providing secure application management and system optimization tools.

## Current Version

**Version**: 0.3.0-dev (In Development)  
**Status**: Infrastructure complete, implementation in progress

See [ROADMAP_V0.3-V1.0.md](ROADMAP_V0.3-V1.0.md) for detailed feature roadmap and [IMPLEMENTATION_PLAN_V0.3.0.md](IMPLEMENTATION_PLAN_V0.3.0.md) for development plan.

## Features

### 🚀 Application Manager
- **Secure Installation**: Download and install vetted applications with hash and HMAC signature verification
- **Dependency Management**: Automatic dependency resolution and installation
- **Multiple Formats**: Support for MSI, EXE, and AppX installers
- **Silent Installation**: Automated silent installation with proper arguments
- **State Tracking**: Persistent tracking of installed applications

### 🛠️ System Tools
- **Registry Tweaks**: Apply performance and customization tweaks with automatic backup
- **Bloatware Removal**: Remove unwanted AppX packages safely
- **Service Management**: Control Windows services (start, stop, enable, disable)
- **Performance Presets**: Apply curated performance optimization profiles
- **Safety Features**: Automatic restore point creation and registry backups

### 🖥️ Interfaces
- **CLI**: Full-featured command-line interface
- **GUI**: User-friendly Tkinter-based graphical interface

## Quick Start

### Installation

Better11 is designed for Windows 11 and requires administrator privileges for system modifications.

#### Prerequisites

Before installation, ensure you have:
- **Supported OS**: Windows 11 (build 22621/22H2 or newer). Earlier builds may have limited DISM feature support.
- **Python**: Version 3.8 or higher with pip
- **PowerShell**: PowerShell 5.1+ (or PowerShell 7) with execution policy allowing local scripts
- **DISM**: Deployment Image Servicing and Management available in the system PATH
- **Permissions**: Administrator rights for system modifications
- **Internet Access**: Required for downloading application installers
- **Disk Space**: Several gigabytes of free space for mounting images and staging installers

#### Installation Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/better11.git
   cd better11
   ```

2. **Open PowerShell as Administrator**:
   - Right-click on PowerShell
   - Select "Run as Administrator"
   - Navigate to the project directory

3. **Configure PowerShell execution policy** (if needed):
   ```powershell
   Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

4. **Verify DISM availability**:
   ```powershell
   dism /?
   ```

5. **Review and unblock scripts** (if needed):
   ```powershell
   Get-ChildItem -Recurse | Unblock-File
   ```

6. **Install Python dependencies** (if any):
   ```bash
   pip install -r requirements.txt
   ```

### Application Manager

#### Command Line

```bash
# List available applications
python -m better11.cli list

# Install an application
python -m better11.cli install demo-app

# Check installation status
python -m better11.cli status

# Uninstall an application
python -m better11.cli uninstall demo-app

# Use a custom catalog
python -m better11.cli --catalog /path/to/catalog.json list
```

#### Media catalog and deployment helpers

Media required for deployments (drivers, cumulative updates, and application installers) can be described in a JSON catalog and pre-staged for offline environments. Each entry captures a source URL, optional SHA-256 checksum, target path within the shared repository, and an install type (`driver`, `update`, or `application`).

```json
{
  "drivers": [
    {
      "id": "gpu",
      "source": "https://example.com/drivers/gpu.exe",
      "target": "drivers/gpu.exe",
      "checksum": "<sha256>",
      "install_type": "driver"
    }
  ],
  "updates": [
    {
      "id": "kb5030211",
      "source": "https://example.com/updates/kb5030211.msu",
      "target": "updates/kb5030211.msu",
      "install_type": "update"
    }
  ],
  "applications": [
    {
      "id": "winget",
      "source": "https://example.com/apps/winget.msixbundle",
      "target": "apps/winget.msixbundle",
      "checksum": "<sha256>",
      "install_type": "application"
    }
  ]
}
```

Validate or fetch media using the deploy helper:

```bash
# Validate catalog structure
python -m better11.media_cli validate ./catalog.json

# Download media into a shared repository (checksums enforced by default)
python -m better11.media_cli fetch-media ./catalog.json ./media-repository

# Skip checksum verification when mirroring from a trusted staging cache
python -m better11.media_cli fetch-media ./catalog.json ./media-repository --skip-checksums
```

To pre-stage media for offline deployments:

1. Author or export a catalog on a connected machine.
2. Run `fetch-media` to populate a repository directory with all referenced installers, drivers, and updates.
3. Transfer the repository to the offline environment (e.g., removable drive or network share).
4. Point deployment scripts at the staged repository to reuse the verified binaries without re-downloading them.

#### GUI

```bash
# Launch the graphical interface
python -m better11.gui
```

The GUI provides an intuitive interface for browsing, installing, and managing applications.

### System Tools

```python
from system_tools.registry import RegistryTweak, apply_tweaks
from system_tools.bloatware import remove_bloatware
from system_tools.performance import PerformancePreset, apply_performance_preset

# Apply registry tweaks
tweaks = [
    RegistryTweak(
        hive="HKEY_CURRENT_USER",
        path=r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
        name="HideFileExt",
        value=0,
        value_type=4
    )
]
apply_tweaks(tweaks)

# Remove bloatware
remove_bloatware(["Microsoft.BingWeather", "Microsoft.GetHelp"])

# Apply performance preset
preset = PerformancePreset(
    name="Gaming",
    registry_tweaks=[...],
    service_actions=[...]
)
apply_performance_preset(preset)
```

## Documentation

### User Documentation
- **[Installation Guide](INSTALL.md)** - Detailed setup instructions
- **[User Guide](USER_GUIDE.md)** - Comprehensive usage documentation
- **[Security](SECURITY.md)** - Security policies and reporting

### Developer Documentation
- **[API Reference](API_REFERENCE.md)** - Complete API documentation
- **[Architecture](ARCHITECTURE.md)** - System design and architecture
- **[Contributing](CONTRIBUTING.md)** - Development guidelines
- **[Changelog](CHANGELOG.md)** - Version history and changes

### Planning & Roadmap (v0.3.0+)
- **[Roadmap v0.3-v1.0](ROADMAP_V0.3-V1.0.md)** - Feature roadmap through v1.0
- **[Implementation Plan v0.3.0](IMPLEMENTATION_PLAN_V0.3.0.md)** - Detailed development plan
- **[Setup Complete](SETUP_COMPLETE.md)** - Infrastructure setup summary

## Security Features

Better11 takes security seriously:

- ✅ **Hash Verification**: SHA-256 hash checking for all downloads
- ✅ **HMAC Signatures**: Optional HMAC-SHA256 signature verification
- ✅ **Domain Vetting**: Only download from pre-approved domains
- ✅ **Restore Points**: Automatic system restore point creation
- ✅ **Registry Backup**: Automatic backup before registry modifications
- ✅ **User Confirmation**: Interactive prompts for destructive operations
- ✅ **Dry-Run Mode**: Test operations without making changes

## Requirements

- **Operating System**: Windows 11 (build 22621/22H2 or newer recommended)
- **Python**: 3.8 or higher with pip
- **PowerShell**: 5.1+ or PowerShell 7
- **DISM**: Available and accessible in system PATH
- **Privileges**: Administrator rights required for system modifications
- **Internet**: Required for downloading applications and updates
- **Disk Space**: Several gigabytes recommended for operations

### Windows Image Formats

For offline image editing, Better11 supports:
- **WIM** (Windows Imaging Format)
- **ESD** (Electronic Software Download format)
- **ISO** (Optical disc image files)

## Project Structure

```
better11/
├── better11/              # Main application package
│   ├── apps/             # Application management
│   │   ├── catalog.py    # Catalog management
│   │   ├── download.py   # Download functionality
│   │   ├── manager.py    # Main application manager
│   │   ├── models.py     # Data models
│   │   ├── runner.py     # Installer execution
│   │   ├── state_store.py # Installation state
│   │   └── verification.py # Security verification
│   ├── cli.py            # Command-line interface
│   └── gui.py            # Graphical interface
├── system_tools/         # System enhancement tools
│   ├── bloatware.py      # Bloatware removal
│   ├── performance.py    # Performance optimization
│   ├── registry.py       # Registry management
│   ├── safety.py         # Safety utilities
│   └── services.py       # Service management
└── tests/                # Test suite
```

## Catalog Format

Applications are defined in `better11/apps/catalog.json`:

```json
{
  "applications": [
    {
      "app_id": "example-app",
      "name": "Example Application",
      "version": "1.0.0",
      "uri": "https://example.com/installer.msi",
      "sha256": "abc123...",
      "installer_type": "msi",
      "vetted_domains": ["example.com"],
      "signature": "base64_signature",
      "signature_key": "base64_key",
      "dependencies": ["dependency-app"],
      "silent_args": ["/quiet", "/norestart"],
      "uninstall_command": "msiexec /x {GUID} /qn"
    }
  ]
}
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:
- Setting up your development environment
- Coding standards and best practices
- Submitting pull requests
- Running tests

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Usage Notes

### Live System Editing

Run from an elevated PowerShell session to make changes to the currently running Windows installation:

```powershell
# Add a Windows capability live
DISM /Online /Add-Capability /CapabilityName:Rsat.ActiveDirectory.DS-LDS.Tools~~~~0.0.1.0

# Enable a Windows feature live
DISM /Online /Enable-Feature /FeatureName:NetFx3 /All
```

### Offline Image Editing

Mount a Windows image, apply changes, and commit them:

```powershell
# Mount the image
$dismMount = "C:\Mount"
$imagePath = "D:\sources\install.wim"
DISM /Mount-WIM /WimFile:$imagePath /Index:1 /MountDir:$dismMount

# Add packages, drivers, or registry tweaks to the mounted image
DISM /Image:$dismMount /Add-Package /PackagePath:"D:\updates\kb.msu"
DISM /Image:$dismMount /Add-Driver /Driver:"D:\drivers" /Recurse

# Commit changes and unmount
DISM /Unmount-WIM /MountDir:$dismMount /Commit
```

### Application Download and Install

Use PowerShell to download and run installers with proper verification:

```powershell
# Download installer
$installer = "C:\Temp\app-setup.exe"
Invoke-WebRequest -Uri "https://example.com/app-setup.exe" -OutFile $installer

# Verify checksum (optional but recommended)
Get-FileHash $installer -Algorithm SHA256

# Install silently if supported
Start-Process -FilePath $installer -ArgumentList "/quiet" -Wait -Verb RunAs
```

## Disclaimer

⚠️ **Important**: Better11 modifies system settings and installs software. While safety features are built-in:

### Safety Recommendations
- **Back up first**: Create a system restore point or full image backup before modifying live systems
- **Offline images**: Keep a copy of the original WIM/ESD before servicing; work on duplicates where possible
- **Administrator context**: Running without elevation will cause many operations to fail or partially apply
- **Disk space**: Mounting images and staging installers requires several gigabytes of free space
- **Integrity**: Verify installer authenticity (hash/signature) and only use trusted download sources
- **Test environment**: Test in a virtual machine first before applying to production systems
- **Review operations**: Always review all operations before confirming
- **Use at your own risk**: The authors are not responsible for any system damage or data loss

## Support

- 📖 [Documentation](docs/)
- 🐛 [Issue Tracker](https://github.com/yourusername/better11/issues)
- 💬 [Discussions](https://github.com/yourusername/better11/discussions)

## Acknowledgments

Better11 was created to simplify Windows 11 customization and application management while maintaining security and safety standards.
