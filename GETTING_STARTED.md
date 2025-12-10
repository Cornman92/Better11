# Getting Started with Better11

**Welcome to Better11!** This guide will help you get up and running quickly.

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install TUI dependencies
pip install textual rich

# Install existing dependencies
pip install -r requirements.txt
```

### 2. Run the TUI

```bash
# From workspace root
python -m better11.tui
```

### 3. Explore Features

The TUI provides access to:
- **Application Management** - Install/uninstall applications
- **System Optimization** - Startup manager, registry tweaks, services
- **Privacy & Security** - Telemetry control, privacy settings
- **Windows Updates** - Update management (coming soon)
- **Disk & Storage** - Disk space analysis, cleanup
- **Network Tools** - DNS configuration, network diagnostics
- **Backup & Restore** - System restore points, registry backup
- **Power Management** - Power plans, hibernation

---

## 📚 Available Interfaces

### 1. Command Line Interface (CLI)

```bash
# List applications
python -m better11.cli list

# Install an application
python -m better11.cli install demo-app

# Check status
python -m better11.cli status

# Generate unattend.xml
python -m better11.cli deploy unattend --product-key KEY --output unattend.xml
```

### 2. Text User Interface (TUI) ⭐ NEW

```bash
python -m better11.tui
```

**Features**:
- Modern terminal UI with keyboard/mouse support
- Real-time data loading with async workers
- Organized into logical categories
- Light/Dark theme support (press 'D')
- Interactive data tables
- Progress indicators

**Navigation**:
- Use number keys (1-9) or mouse clicks
- Press 'Escape' to go back
- Press 'Q' to quit
- Press 'D' to toggle dark mode

### 3. Graphical User Interface (GUI)

```bash
python -m better11.gui
```

---

## 🔧 Module Usage Examples

### Disk Management

```python
from system_tools.disk import DiskManager

# Create manager
manager = DiskManager(dry_run=False)

# Analyze disk space
disks = manager.analyze_disk_space()
for drive, info in disks.items():
    print(f"{drive}: {info.free_gb:.2f} GB free ({info.usage_percent:.1f}% used)")

# Cleanup temp files
result = manager.cleanup_temp_files(age_days=7)
print(f"Removed {result.files_removed} files, freed {result.space_freed_mb:.2f} MB")
```

### Network Tools

```python
from system_tools.network import NetworkManager, DNSConfiguration

manager = NetworkManager(dry_run=False)

# Flush DNS cache
manager.flush_dns_cache()

# Configure Google DNS
manager.configure_dns("Ethernet", NetworkManager.GOOGLE_DNS)

# Test connectivity
if manager.test_connectivity("8.8.8.8"):
    print("Internet connectivity OK")
```

### Backup & Restore

```python
from system_tools.backup import BackupManager

manager = BackupManager(dry_run=False)

# Create restore point
point = manager.create_restore_point("Before Better11 changes")
print(f"Restore point created: {point.description}")

# List restore points
points = manager.list_restore_points()
for point in points:
    print(f"{point.sequence_number}: {point.description} ({point.creation_time})")

# Export settings
manager.export_settings(Path("better11-settings.json"))
```

### Power Management

```python
from system_tools.power import PowerManager

manager = PowerManager(dry_run=False)

# List power plans
plans = manager.list_power_plans()
for plan in plans:
    status = "ACTIVE" if plan.is_active else ""
    print(f"{plan.name} [{plan.plan_type.value}] {status}")

# Switch to High Performance
manager.set_active_plan(PowerManager.HIGH_PERFORMANCE_GUID)

# Generate battery report
report_path = manager.generate_battery_report()
print(f"Battery report: {report_path}")
```

### Startup Management

```python
from system_tools.startup import StartupManager

manager = StartupManager(dry_run=False)

# List startup items
items = manager.list_startup_items()
for item in items:
    print(f"{item.name}: {item.location.value} ({'Enabled' if item.enabled else 'Disabled'})")

# Disable an item
for item in items:
    if "OneDrive" in item.name:
        manager.disable_startup_item(item)
        print(f"Disabled {item.name}")
```

### Privacy Controls

```python
from system_tools.privacy import PrivacyManager, TelemetryLevel

manager = PrivacyManager(dry_run=False)

# Check current telemetry level
level = manager.get_telemetry_level()
print(f"Current telemetry: {level.name}")

# Set to basic
manager.set_telemetry_level(TelemetryLevel.BASIC)

# Disable Cortana
manager.disable_cortana()

# Disable advertising ID
manager.disable_advertising_id()
```

---

## 💻 PowerShell Module (NEW)

### Import the Module

```powershell
# Import Better11 PowerShell module
Import-Module ./powershell/Better11/Better11.psd1

# List available commands
Get-Command -Module Better11
```

### Use PowerShell Functions

```powershell
# Disk management
Get-Better11DiskSpace
Clear-Better11TempFiles -AgeDays 30

# Common utilities
Test-Better11Administrator
Write-Better11Log -Message "Operation started" -Level Info
Confirm-Better11Action "Proceed with changes?"
```

---

## 🎯 What's New

### Recently Added ✨

1. **TUI Interface** - Modern terminal UI with textual
2. **Disk Management Module** - Space analysis and cleanup
3. **Network Tools Module** - DNS config and diagnostics
4. **Backup Module** - Restore points and settings
5. **Power Management Module** - Power plans and hibernation
6. **PowerShell Backend** - Native Windows PowerShell modules

### Module Statistics

```
System Modules: 10
- registry.py
- bloatware.py
- services.py
- performance.py
- startup.py (enhanced)
- privacy.py (enhanced)
- updates.py (enhanced)
- features.py (enhanced)
- disk.py (NEW)
- network.py (NEW)
- backup.py (NEW)
- power.py (NEW)

Interfaces: 3
- CLI (existing)
- GUI (existing)
- TUI (NEW)

PowerShell Modules: 7 (partial)
- Common (complete)
- Disk (partial)
- Network (planned)
- Backup (planned)
- Power (planned)
- AppManager (planned)
- SystemTools (planned)
```

---

## 📖 Documentation

### For Users
- [README.md](README.md) - Project overview
- [USER_GUIDE.md](USER_GUIDE.md) - Comprehensive user guide
- [GETTING_STARTED.md](GETTING_STARTED.md) - This file
- [INSTALL.md](INSTALL.md) - Installation instructions

### For Developers
- [API_REFERENCE.md](API_REFERENCE.md) - Complete API documentation
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development guidelines
- [IMPLEMENTATION_PLAN_TUI_AND_MIGRATION.md](IMPLEMENTATION_PLAN_TUI_AND_MIGRATION.md) - Full implementation plan
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Summary of completed work

### Planning Documents
- [EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md) - High-level overview
- [FORWARD_PLAN.md](FORWARD_PLAN.md) - Strategic planning
- [ROADMAP_V0.3-V1.0.md](ROADMAP_V0.3-V1.0.md) - Feature roadmap

---

## 🛠️ Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_disk.py

# Run with coverage
pytest --cov=better11 --cov=system_tools
```

### Dry-Run Mode

All modules support dry-run mode for testing:

```python
# Won't actually make changes
manager = DiskManager(dry_run=True)
manager.cleanup_temp_files()  # Simulates cleanup
```

### Logging

All operations are logged:

```python
from better11 import Config

config = Config()
config.logging_level = "DEBUG"  # Enable debug logging
```

Logs are stored in: `~/.better11/logs/`

---

## 🚧 Roadmap

### Current Phase: PowerShell Backend (Weeks 5-8)
- [x] PowerShell module structure
- [x] Common utilities module
- [x] Disk management module (partial)
- [ ] Network module
- [ ] Backup module
- [ ] Power module
- [ ] AppManager module
- [ ] SystemTools module

### Next: C# Frontend (Weeks 9-12)
- [ ] Solution structure
- [ ] Models and interfaces
- [ ] Service layer
- [ ] PowerShell executor
- [ ] Unit tests

### Future: WinUI 3 GUI (Weeks 13-18)
- [ ] WinUI 3 project
- [ ] MVVM architecture
- [ ] 18 functional pages
- [ ] Theme support
- [ ] Polished UI/UX

---

## ❓ FAQ

### Q: Do I need administrator privileges?

**A:** Most operations require administrator privileges, especially:
- Registry modifications
- Service management
- System restore points
- Network configuration
- Windows Update control

### Q: Is it safe to use?

**A:** Yes! Better11 includes multiple safety features:
- Automatic backups before changes
- Restore point creation
- Dry-run mode for testing
- User confirmation prompts
- Comprehensive logging

### Q: Can I use this on Windows 10?

**A:** Better11 is designed for Windows 11, but many features work on Windows 10.
Some features may have limited functionality on older versions.

### Q: How do I uninstall?

**A:** Simply delete the directory. Better11 stores minimal data:
- Configuration: `~/.better11/config.json`
- Logs: `~/.better11/logs/`
- Backups: `~/.better11/backups/`

### Q: Can I contribute?

**A:** Yes! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 🐛 Troubleshooting

### TUI won't start

```bash
# Install/update textual
pip install --upgrade textual rich

# Try running directly
python better11/tui.py
```

### Permission denied errors

```bash
# Run with administrator privileges
# Right-click PowerShell -> "Run as Administrator"

# Or use sudo (if configured)
sudo python -m better11.tui
```

### Import errors

```bash
# Ensure you're in the workspace root
cd /workspace

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-tui.txt
```

---

## 📞 Support

- **Documentation**: See [docs/](docs/) directory
- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Use GitHub Discussions for questions

---

## 🎉 Next Steps

1. **Try the TUI**: `python -m better11.tui`
2. **Explore Modules**: Check individual module documentation
3. **Read the Plan**: Review [IMPLEMENTATION_PLAN_TUI_AND_MIGRATION.md](IMPLEMENTATION_PLAN_TUI_AND_MIGRATION.md)
4. **Contribute**: See [CONTRIBUTING.md](CONTRIBUTING.md)

---

**Happy optimizing! 🚀**

*For the full implementation plan, see [IMPLEMENTATION_PLAN_TUI_AND_MIGRATION.md](IMPLEMENTATION_PLAN_TUI_AND_MIGRATION.md)*
