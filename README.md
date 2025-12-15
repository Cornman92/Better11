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

## 💻 Usage

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

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Microsoft for Windows 11 and WinUI 3
- The open-source community

---

**Better11** - Making Windows 11 better, one tweak at a time.
