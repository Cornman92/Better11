# Better11 - Windows 11 Enhancement Toolkit

[![Version](https://img.shields.io/badge/version-0.3.0-blue.svg)](https://github.com/better11/better11)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%2011-blueviolet.svg)](https://www.microsoft.com/windows/windows-11)

A comprehensive Windows 11 system optimization, customization, and management toolkit built with native Windows technologies.

## 🏗️ Architecture

Better11 uses a modern three-tier architecture:

```
┌─────────────────────────────────────────────────────────────────┐
│                         WinUI 3 GUI                             │
│  (XAML Views, Pages, Navigation, User Controls)                │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   C# ViewModels (MVVM)                         │
│  (Data binding, Commands, Navigation, State management)        │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     C# Services Layer                          │
│  (Business logic, PowerShell execution, Data transformation)   │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                PowerShell Backend Modules                       │
│  (System operations, Registry, WMI, DISM, Services)            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Windows 11 APIs                             │
│  (Registry, WMI, COM, DISM, Task Scheduler, Windows Update)    │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Features

### Privacy & Security
- **Telemetry Control**: Manage Windows diagnostic data collection
- **App Permissions**: Control location, camera, microphone access
- **Advertising ID**: Disable personalized advertising
- **Cortana**: Enable/disable the voice assistant
- **Privacy Presets**: Apply recommended privacy settings with one click

### Performance Optimization
- **Visual Effects**: Balance appearance vs. performance
- **Processor Scheduling**: Optimize for programs or background services
- **Fast Startup**: Enable/disable hybrid shutdown
- **Virtual Memory**: Configure page file settings
- **Performance Presets**: Maximum, Balanced, or Default optimization

### Shell Customization
- **Taskbar Alignment**: Left or center alignment
- **Search Box**: Hide, show icon only, or full search box
- **Button Visibility**: Control Task View, Widgets, Copilot buttons
- **Classic Context Menu**: Restore Windows 10-style right-click menu
- **Shell Presets**: Windows 10 style, Minimal, or Default

### Gaming Optimization
- **Game Mode**: Optimize system resources during gaming
- **Xbox Game Bar**: Enable/disable in-game overlay
- **GPU Scheduling**: Hardware-accelerated GPU scheduling
- **Mouse Acceleration**: Raw input for consistent aim
- **Nagle's Algorithm**: Network latency optimization
- **Gaming Presets**: Maximum performance, Balanced, Default

### System Management
- **App Management**: View and uninstall applications
- **Network Tools**: Flush DNS, reset TCP/IP, reset Winsock
- **Backup & Restore**: System restore points, registry backups
- **Driver Management**: View, backup, and export drivers
- **Windows Updates**: Check, pause, and manage updates
- **Scheduled Tasks**: Manage and disable telemetry tasks
- **System Information**: Detailed hardware and software info

## 📁 Project Structure

```
/workspace/
├── csharp/
│   ├── Better11.sln           # Visual Studio solution
│   ├── Better11.Core/         # Core services and interfaces
│   │   ├── Interfaces/        # Service contracts
│   │   ├── Models/            # Data models
│   │   ├── Services/          # Service implementations
│   │   └── PowerShell/        # PowerShell executor
│   ├── Better11.CLI/          # Command-line interface
│   ├── Better11.GUI/          # WinUI 3 GUI application
│   │   ├── Views/             # XAML pages
│   │   ├── ViewModels/        # MVVM ViewModels
│   │   └── Controls/          # Custom controls
│   └── Better11.Tests/        # Unit tests
└── powershell/
    └── Better11/
        ├── Better11.psd1      # Module manifest
        ├── Better11.psm1      # Root module
        └── Modules/           # Sub-modules
            ├── AppManager/    # App management
            ├── Backup/        # Backup operations
            ├── Common/        # Shared utilities
            ├── Disk/          # Disk management
            ├── Drivers/       # Driver management
            ├── Features/      # Windows features
            ├── Gaming/        # Gaming optimization
            ├── Network/       # Network tools
            ├── Performance/   # Performance tuning
            ├── Power/         # Power management
            ├── Privacy/       # Privacy settings
            ├── Safety/        # Safety operations
            ├── Shell/         # Shell customization
            ├── Startup/       # Startup management
            ├── SysInfo/       # System information
            ├── SystemTools/   # System utilities
            ├── Tasks/         # Scheduled tasks
            └── Updates/       # Windows Update
```

## 🔧 Requirements

- **Operating System**: Windows 11 (22H2 or later recommended)
- **Framework**: .NET 8.0
- **PowerShell**: 5.1+ or PowerShell 7+
- **Privileges**: Administrator rights required for most operations

## 📦 Installation

### From Source

1. Clone the repository:
   ```powershell
   git clone https://github.com/better11/better11.git
   cd better11
   ```

2. Build the solution:
   ```powershell
   dotnet build csharp/Better11.sln
   ```

3. Run the GUI:
   ```powershell
   dotnet run --project csharp/Better11.GUI
   ```

### PowerShell Module Only

1. Copy the PowerShell module:
   ```powershell
   Copy-Item -Path .\powershell\Better11 -Destination "$env:USERPROFILE\Documents\PowerShell\Modules\Better11" -Recurse
   ```

2. Import the module:
   ```powershell
   Import-Module Better11
   ```

7. **Build the Better11 installer package** (reproducible wheel):
   ```bash
   python -m system_tools.package_builder --out dist
   ```

8. **Install the packaged wheel** (documents version/license):
   ```bash
   pip install dist/better11-0.3.0.dev0-py3-none-any.whl
   ```
   - Current Better11 version: `0.3.0.dev0` (MIT licensed).
   - Built wheel is MIT-compatible; see `LICENSE` for details.

9. **Rollback**: uninstall the package cleanly if needed:
   ```bash
   pip uninstall -y better11
   ```

### Application Manager

### PowerShell

```powershell
# Import the module
Import-Module Better11

# Privacy
Get-Better11TelemetryLevel
Set-Better11TelemetryLevel -Level Basic
Set-Better11PrivacyPreset -Preset Maximum

# Performance
Get-Better11PerformanceSettings
Optimize-Better11Performance -Preset Maximum
Set-Better11VisualEffects -Preset BestPerformance

# Gaming
Get-Better11GamingSettings
Set-Better11GamingPreset -Preset Maximum
Disable-Better11NagleAlgorithm

# Shell
Set-Better11TaskbarAlignment -Alignment Left
Enable-Better11ClassicContextMenu
Restart-Better11Explorer

# System Info
Get-Better11SystemSummary
Export-Better11SystemInfo -Path "C:\SystemInfo.json"

# Drivers
Get-Better11Drivers
Backup-Better11Drivers -Path "D:\DriverBackup"

# Backup
New-Better11RestorePoint -Description "Before changes"
Get-Better11RestorePoints
```

### Command-Line Interface

```bash
# Run the CLI
dotnet run --project csharp/Better11.CLI -- privacy status
dotnet run --project csharp/Better11.CLI -- performance optimize --preset maximum
dotnet run --project csharp/Better11.CLI -- backup create-restore-point "My Backup"
```

## 🛡️ Safety Features

- **Restore Points**: Automatically create system restore points before changes
- **Registry Backups**: Export registry keys before modifications
- **Administrator Check**: Verify privileges before system operations
- **Confirmation Prompts**: Confirm dangerous operations

## 📖 Documentation

- [API Reference](API_REFERENCE.md) - Complete API documentation
- [User Guide](USER_GUIDE.md) - End-user documentation
- [Architecture](ARCHITECTURE.md) - Technical architecture details
- [Contributing](CONTRIBUTING.md) - Contribution guidelines

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### Deployment

Better11 provides a deployment workflow powered by DISM and PowerShell for capturing, applying, and servicing Windows images.

```bash
# Capture a Windows volume into a WIM (use --esd for ESD compression)
python -m better11.cli deploy capture C:\\ D:\\images\\custom.wim --name "Custom Image" --description "Post-setup snapshot"

# Apply an image to a target partition
python -m better11.cli deploy apply D:\\images\\custom.wim D:\\target --index 1

# Mount and service an image (add drivers, enable features, and stage updates)
python -m better11.cli deploy service D:\\images\\custom.wim D:\\mount --driver D:\\drivers --feature NetFX3 --update D:\\updates\\kb123456.msu
```

Deployment commands gracefully report errors on non-Windows hosts and require DISM/PowerShell to be available in the system PATH.

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
- **[📊 Executive Summary](EXECUTIVE_SUMMARY.md)** - High-level overview for decision makers ⭐ LEADERS START HERE
- **[📋 Planning Index](PLANNING_INDEX.md)** - Navigation guide for all planning documents
- **[🚀 Forward Plan](FORWARD_PLAN.md)** - Comprehensive 12-week strategy for moving forward
- **[⚡ Quick Start Guide](QUICKSTART_IMPLEMENTATION.md)** - Start implementing v0.3.0 TODAY 💻
- **[🗺️ Visual Roadmap](ROADMAP_VISUAL.md)** - Timeline and milestone visualization
- **[Roadmap v0.3-v1.0](ROADMAP_V0.3-V1.0.md)** - Feature roadmap through v1.0
- **[Implementation Plan v0.3.0](IMPLEMENTATION_PLAN_V0.3.0.md)** - Detailed technical development plan
- **[What's Next?](WHATS_NEXT.md)** - Context and current state
- **[Setup Complete](SETUP_COMPLETE.md)** - Infrastructure setup summary
- **[Migration Plan](MIGRATION_PLAN_POWERSHELL_CSHARP_WINUI3.md)** - Optional long-term tech evolution

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
- **.NET 8.0 SDK**: Required for C# CLI
- **PowerShell**: 5.1+ or PowerShell 7
- **Privileges**: Administrator rights required for system modifications
- **Internet**: Required for downloading applications and updates
- **Disk Space**: 500MB for Better11, plus space for applications

**Optional**:
- **Python 3.8+**: Only if using Python backend libraries
- **DISM**: Only for offline image editing features

### Windows Image Formats

For offline image editing, Better11 supports:
- **WIM** (Windows Imaging Format)
- **ESD** (Electronic Software Download format)
- **ISO** (Optical disc image files)

## Project Structure

```
better11/
├── csharp/                # C# frontend and core
│   ├── Better11.Core/    # Core library
│   │   ├── Apps/         # Application management
│   │   ├── Deployment/   # Unattend.xml generation
│   │   └── Services/     # System services
│   ├── Better11.CLI/     # Command-line interface
│   └── Better11.GUI/     # WPF graphical interface
├── better11/              # Python backend (system tools)
│   └── apps/             # Application catalog (JSON)
│       └── catalog.json  # Application catalog
├── powershell/            # PowerShell modules
│   └── Better11/         # Better11 PowerShell module
├── system_tools/         # Python system enhancement tools
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

## 🙏 Acknowledgments

- Microsoft for Windows 11 and WinUI 3
- The open-source community

---

**Better11** - Making Windows 11 better, one tweak at a time.
