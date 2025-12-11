# Better11 - Windows 11 Enhancement Toolkit

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform: Windows 11](https://img.shields.io/badge/platform-Windows%2011-blue.svg)](https://www.microsoft.com/windows)

**Comprehensive Windows 11 system management and optimization toolkit with Python, PowerShell, and planned C# WinUI 3 GUI.**

---

## 🌟 What's New in v0.3.0-dev

### ✨ Major Additions

- **🖥️ Text User Interface (TUI)** - Modern terminal interface built with Textual
- **💾 Disk Management** - Space analysis, cleanup, optimization
- **🌐 Network Tools** - DNS configuration, diagnostics, connectivity tests
- **💼 Backup & Restore** - System restore points, registry backup, settings export
- **⚡ Power Management** - Power plans, hibernation, battery reports
- **📜 PowerShell Backend** - Native Windows PowerShell modules (in progress)

### 📊 Statistics

```
System Modules:    10 (doubled!)
Interfaces:         3 (CLI, GUI, TUI)
PowerShell Modules: 7 (partial implementation)
Total Code:        ~12,000+ lines
```

---

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/better11.git
cd better11

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-tui.txt

# Run TUI (recommended)
python -m better11.tui
```

### Try It Now!

```bash
# Modern TUI interface
python -m better11.tui

# Classic CLI
python -m better11.cli list

# Graphical GUI
python -m better11.gui
```

---

## 🎯 Features

### 🚀 Application Management
- Secure installation with hash verification
- HMAC signature verification
- Automatic dependency resolution
- Multiple installer formats (MSI, EXE, AppX)
- Silent installation
- State tracking

### 🛠️ System Optimization
- **Registry Tweaks** - Apply performance customizations with automatic backup
- **Bloatware Removal** - Remove unwanted AppX packages safely
- **Service Management** - Control Windows services
- **Startup Manager** - Manage startup programs ⭐ NEW
- **Performance Presets** - Apply curated optimization profiles

### 💾 Disk & Storage ⭐ NEW
- **Disk Space Analysis** - View usage for all drives
- **Temp File Cleanup** - Remove old temporary files
- **Usage Reports** - Folder-level disk usage analysis
- Support for HDD, SSD, removable, and network drives

### 🌐 Network Tools ⭐ NEW
- **Adapter Management** - List and configure network adapters
- **DNS Configuration** - Quick setup for popular DNS providers
- **DNS Cache Flush** - Clear DNS resolver cache
- **TCP/IP Reset** - Reset network stack
- **Connectivity Tests** - Ping and network diagnostics

### 🔒 Privacy & Security
- **Telemetry Control** - Manage Windows telemetry levels
- **Privacy Settings** - Control app permissions
- **Cortana Disable** - Disable Cortana voice assistant
- **Advertising ID** - Disable tracking advertising ID
- **Privacy Presets** - Apply common privacy configurations

### 💼 Backup & Restore ⭐ NEW
- **System Restore Points** - Create and list restore points
- **Registry Backup** - Backup registry hives
- **Settings Export** - Export Better11 configuration
- **Settings Import** - Restore saved configurations

### ⚡ Power Management ⭐ NEW
- **Power Plans** - List and switch power plans
- **Hibernation Control** - Enable/disable hibernation
- **Battery Reports** - Generate detailed battery health reports
- Support for all Windows power plans

### 📱 Windows Updates
- Update checking and installation
- Pause/resume updates
- Active hours configuration
- Update history viewing

### 🎛️ Windows Features
- Enable/disable optional features
- Feature presets (Developer, Minimal)
- DISM integration

### 🖥️ Multiple Interfaces

#### 1. Text User Interface (TUI) ⭐ NEW
**Modern terminal interface with:**
- Keyboard and mouse navigation
- Real-time data loading
- Interactive data tables
- Light/Dark theme support
- Organized category screens
- Progress indicators

```bash
python -m better11.tui
```

#### 2. Command Line Interface (CLI)
```bash
# List applications
python -m better11.cli list

# Install application
python -m better11.cli install app-id

# Generate unattend.xml
python -m better11.cli deploy unattend --product-key KEY --output file.xml
```

#### 3. Graphical User Interface (GUI)
```bash
python -m better11.gui
```

### 📜 PowerShell Backend ⭐ NEW

Native Windows PowerShell modules for system operations:

```powershell
# Import Better11 module
Import-Module ./powershell/Better11/Better11.psd1

# Use PowerShell functions
Get-Better11DiskSpace
Clear-Better11TempFiles -AgeDays 30
Test-Better11Administrator
Write-Better11Log -Message "Started" -Level Info
```

**Available Modules:**
- **Common** - Logging, admin checks, confirmations
- **Disk** - Disk space analysis and cleanup
- **Network** - Network configuration (planned)
- **Backup** - Backup and restore (planned)
- **Power** - Power management (planned)
- **More modules in development...**

---

## 🏗️ Architecture

### Current (Python)
```
better11/
├── better11/              # Python application
│   ├── apps/             # Application management
│   ├── cli.py            # Command-line interface
│   ├── gui.py            # Tkinter GUI
│   └── tui.py            # Textual TUI ⭐ NEW
├── system_tools/         # System management
│   ├── disk.py           # Disk management ⭐ NEW
│   ├── network.py        # Network tools ⭐ NEW
│   ├── backup.py         # Backup/restore ⭐ NEW
│   ├── power.py          # Power management ⭐ NEW
│   └── ...
```

### Future (Hybrid)
```
better11/
├── python/               # Python implementation (preserved)
├── powershell/           # PowerShell backend ⭐ NEW
│   └── Better11/
│       ├── Better11.psd1
│       └── Modules/
├── csharp/              # C# frontend (planned)
│   ├── Better11.Core/
│   ├── Better11.WinUI/  # WinUI 3 GUI (planned)
│   └── Better11.Tests/
```

---

## 📖 Documentation

### Quick Access
- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Start here! ⭐
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - What's been done
- **[IMPLEMENTATION_PLAN_TUI_AND_MIGRATION.md](IMPLEMENTATION_PLAN_TUI_AND_MIGRATION.md)** - Complete 20-week plan

### User Documentation
- [Installation Guide](INSTALL.md)
- [User Guide](USER_GUIDE.md)
- [Security](SECURITY.md)

### Developer Documentation
- [API Reference](API_REFERENCE.md)
- [Contributing](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)

### Planning Documents
- [Executive Summary](EXECUTIVE_SUMMARY.md)
- [Forward Plan](FORWARD_PLAN.md)
- [Roadmap v0.3-v1.0](ROADMAP_V0.3-V1.0.md)

---

## 🔐 Security Features

- ✅ **Hash Verification** - SHA-256 for all downloads
- ✅ **HMAC Signatures** - Optional signature verification
- ✅ **Domain Vetting** - Only approved download domains
- ✅ **Restore Points** - Automatic system restore points
- ✅ **Registry Backup** - Automatic backup before modifications
- ✅ **User Confirmation** - Interactive prompts for destructive operations
- ✅ **Dry-Run Mode** - Test operations without changes

---

## 📊 Roadmap

### ✅ Phase 1-2: TUI & Additional Modules (COMPLETE)
- [x] Modern TUI interface
- [x] Disk management module
- [x] Network tools module
- [x] Backup & restore module
- [x] Power management module
- [x] All functionality wired up

### 🔄 Phase 3: PowerShell Backend (IN PROGRESS)
- [x] Module structure created
- [x] Common utilities (complete)
- [x] Disk module (partial)
- [ ] Network module
- [ ] All 17 modules complete
- [ ] Pester tests for all modules

### 📋 Phase 4: C# Frontend (Weeks 9-12)
- [ ] Solution structure
- [ ] PowerShell executor
- [ ] 15+ service classes
- [ ] Unit tests (>80% coverage)

### 🎨 Phase 5: WinUI 3 GUI (Weeks 13-18)
- [ ] WinUI 3 project
- [ ] MVVM architecture
- [ ] 18 functional pages
- [ ] Beautiful native Windows 11 UI

**Full Timeline**: 20 weeks total, currently week 5

See [IMPLEMENTATION_PLAN_TUI_AND_MIGRATION.md](IMPLEMENTATION_PLAN_TUI_AND_MIGRATION.md) for complete details.

---

## 💻 Requirements

- **Operating System**: Windows 11 (22H2 or newer recommended)
- **Python**: 3.8 or higher
- **PowerShell**: 5.1+ or PowerShell 7
- **Privileges**: Administrator rights for system modifications
- **Internet**: Required for downloading applications
- **Disk Space**: Several gigabytes for operations

### Python Dependencies
```bash
pip install -r requirements.txt      # Core dependencies
pip install -r requirements-tui.txt  # TUI dependencies (textual, rich)
```

---

## 🎯 Usage Examples

### TUI Navigation
```
Press '1' - Application Management
Press '2' - System Tools  
Press '6' - Disk Management
Press '7' - Network Tools
Press '8' - Backup & Restore
Press '9' - Power Management
Press 'Q' - Quit
Press 'D' - Toggle Dark Mode
```

### Python API
```python
# Disk management
from system_tools.disk import DiskManager
manager = DiskManager()
disks = manager.analyze_disk_space()
result = manager.cleanup_temp_files(age_days=7)

# Network tools
from system_tools.network import NetworkManager
manager = NetworkManager()
manager.flush_dns_cache()
manager.configure_dns("Ethernet", NetworkManager.GOOGLE_DNS)

# Backup & restore
from system_tools.backup import BackupManager
manager = BackupManager()
point = manager.create_restore_point("Before changes")
points = manager.list_restore_points()
```

### PowerShell API
```powershell
# Disk operations
Get-Better11DiskSpace
Clear-Better11TempFiles -AgeDays 30 -Confirm:$false

# Utilities
Test-Better11Administrator
Write-Better11Log -Message "Operation started" -Level Info
Confirm-Better11Action "Proceed with operation?"
```

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Setting up development environment
- Coding standards
- Submitting pull requests
- Running tests

---

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

---

## 🎉 Acknowledgments

Better11 was created to simplify Windows 11 customization and management while maintaining security and safety standards.

### Special Thanks
- **Textual** - For the amazing TUI framework
- **Rich** - For beautiful terminal formatting
- **Community** - For feedback and contributions

---

## 📞 Support

- 📖 **Documentation**: See [docs/](docs/) directory
- 🐛 **Issues**: [GitHub Issues](https://github.com/yourusername/better11/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/better11/discussions)

---

## ⚠️ Disclaimer

Better11 modifies system settings. While safety features are built-in:
- **Back up first** - Create system restore point
- **Test in VM** - Try in virtual machine first
- **Review operations** - Always review before confirming
- **Use at own risk** - Authors not responsible for damage

---

## 🚀 Get Started Now!

```bash
# 1. Clone and install
git clone https://github.com/yourusername/better11.git
cd better11
pip install -r requirements.txt -r requirements-tui.txt

# 2. Run TUI
python -m better11.tui

# 3. Explore!
Press '6' for Disk Management
Press '7' for Network Tools
Press 'Q' to quit
```

**For detailed instructions, see [GETTING_STARTED.md](GETTING_STARTED.md)**

---

**Version**: 0.3.0-dev  
**Status**: Active Development  
**Last Updated**: December 10, 2025

*Transforming Windows 11 management, one module at a time.* 🚀
