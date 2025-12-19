# Better11 Quick Start Guide

Get up and running with Better11 in minutes!

## 🚀 Installation (5 minutes)

### Step 1: Clone Repository

```bash
git clone https://github.com/Cornman92/Better11.git
cd Better11
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

That's it! You're ready to go.

---

## 🎯 Choose Your Path

### Path 1: I Want a GUI (Easiest)

```bash
python -m better11 gui
```

Click around, explore all the tabs, and manage your Windows system with a point-and-click interface!

---

### Path 2: I Want a Terminal Interface

```bash
python -m better11 tui
```

Navigate with arrow keys and Enter. Access all features through beautiful terminal menus.

---

### Path 3: I Want to Run Examples

Pick a workflow and run it:

#### Fresh Windows Setup
```bash
python examples/fresh_install_optimization.py
```

**What it does:** Updates, drivers, apps, optimization, cleanup - complete automated setup!

#### Install Apps in Bulk
```bash
# Gaming apps
python examples/bulk_app_installation.py --profile gaming

# Development tools
python examples/bulk_app_installation.py --profile development

# Custom list
python examples/bulk_app_installation.py --custom my_apps.txt
```

#### Backup Drivers
```bash
python examples/driver_backup_update.py
```

#### Create Deployment Image
```bash
python examples/create_deployment_image.py \
    --source C:\install.wim \
    --output C:\custom.wim \
    --drivers C:\Drivers
```

---

## 🎓 Learn by Example

### Example 1: Install Chrome via WinGet

```python
from better11.package_manager import UnifiedPackageManager, PackageManager

manager = UnifiedPackageManager()
success = manager.install(PackageManager.WINGET, "Google.Chrome")

if success:
    print("Chrome installed!")
```

### Example 2: Optimize for Gaming

```python
from better11.system_optimizer import SystemOptimizer

optimizer = SystemOptimizer()
results = optimizer.optimize_for_gaming()

print(f"Applied {len([r for r in results if r.success])} optimizations")
```

### Example 3: Backup All Drivers

```python
from better11.driver_manager import DriverManager

manager = DriverManager()
count, backup_path = manager.backup_all_drivers()

print(f"Backed up {count} drivers to {backup_path}")
```

### Example 4: Check for Windows Updates

```python
from better11.update_manager import WindowsUpdateManager

manager = WindowsUpdateManager()
updates = manager.check_for_updates()

print(f"Found {len(updates)} updates")
for update in updates[:5]:
    print(f"  - {update.title}")
```

---

## ⚙️ Configuration Quick Start

### Use a Preset Profile

```python
from better11.config_manager import ConfigManager

# Load gaming profile
config = ConfigManager()
config.apply_profile("gaming")
config.save()

print("Gaming profile active!")
```

### Check Current Configuration

```python
from better11.config_manager import get_config

config = get_config()
print(f"Optimization level: {config.config.optimizer.default_level}")
print(f"Verbose mode: {config.config.ui.verbose}")
```

---

## 🛠️ Common Tasks

### Task: Find Large Files

```python
from better11.file_manager import find_large_files

large_files = find_large_files("C:\\Users", min_size_mb=100)

for file in large_files[:10]:
    size_gb = file.size / (1024**3)
    print(f"{file.name}: {size_gb:.2f} GB")
```

### Task: Find Duplicate Files

```python
from better11.file_manager import find_duplicates

duplicates = find_duplicates("C:\\Users\\Documents")

for hash_val, paths in duplicates.items():
    print(f"\nDuplicate group ({len(paths)} files):")
    for path in paths:
        print(f"  - {path}")
```

### Task: List USB Drives

```python
from better11.iso_manager import list_usb_drives

devices = list_usb_drives()

for device in devices:
    size_gb = device.size / (1024**3)
    print(f"{device.name}: {size_gb:.2f} GB (Drive {device.drive_letter})")
```

### Task: Get System Metrics

```python
from better11.system_optimizer import SystemOptimizer

optimizer = SystemOptimizer()
metrics = optimizer.get_system_metrics()

print(f"CPU: {metrics.cpu_percent}%")
print(f"Memory: {metrics.memory_percent}%")
print(f"Disk: {metrics.disk_usage_percent}%")
print(f"Processes: {metrics.running_processes}")
```

---

## 📝 Create Custom App List

Create `my_apps.txt`:

```
# Format: Name, Package ID, Manager
Visual Studio Code, Microsoft.VisualStudioCode, winget
Google Chrome, Google.Chrome, winget
Discord, Discord.Discord, winget
Spotify, Spotify.Spotify, winget
7-Zip, 7zip.7zip, winget
```

Then run:

```bash
python examples/bulk_app_installation.py --custom my_apps.txt
```

---

## 🎮 Gaming Setup (Complete Workflow)

```bash
# 1. Run fresh install optimization
python examples/fresh_install_optimization.py

# 2. Install gaming apps
python examples/bulk_app_installation.py --profile gaming

# 3. Apply gaming config
python -c "from better11.config_manager import ConfigManager; c=ConfigManager(); c.apply_profile('gaming'); c.save()"

# 4. Reboot
shutdown /r /t 0
```

---

## 💻 Developer Setup (Complete Workflow)

```bash
# 1. Install development tools
python examples/bulk_app_installation.py --profile development

# 2. Apply developer config
python -c "from better11.config_manager import ConfigManager; c=ConfigManager(); c.apply_profile('developer'); c.save()"

# 3. Install additional tools
python -c "from better11.package_manager import UnifiedPackageManager, PackageManager; m=UnifiedPackageManager(); m.install(PackageManager.WINGET, 'Postman.Postman')"
```

---

## 🏢 IT Admin: Create Deployment Image

```bash
# 1. Prepare directories
mkdir C:\ImageBuild
mkdir C:\ImageBuild\Drivers
mkdir C:\ImageBuild\Updates

# 2. Copy your source WIM
copy D:\sources\install.wim C:\ImageBuild\

# 3. Add drivers to C:\ImageBuild\Drivers

# 4. Add updates to C:\ImageBuild\Updates

# 5. Create custom image
python examples/create_deployment_image.py \
    --source C:\ImageBuild\install.wim \
    --output C:\ImageBuild\custom.wim \
    --drivers C:\ImageBuild\Drivers \
    --updates C:\ImageBuild\Updates \
    --optimize

# 6. Test in VM before deployment!
```

---

## 🧪 Testing Your Installation

```bash
# Run tests
pytest

# Run specific test
pytest tests/test_image_manager.py -v

# Check coverage
pytest --cov=better11 --cov-report=term
```

---

## 🆘 Troubleshooting

### "Module not found" error

```bash
# Ensure you're in the Better11 directory
cd Better11

# Reinstall dependencies
pip install -r requirements.txt
```

### "DISM not found" error

```powershell
# Check if DISM is available
dism /?

# If not, ensure you're on Windows 11
```

### "Permission denied" error

```powershell
# Run PowerShell as Administrator
# Right-click PowerShell -> Run as Administrator
```

### GUI not launching

```bash
# Install tkinter (usually included with Python on Windows)
# If missing, reinstall Python with tkinter option checked
```

---

## 📚 Next Steps

1. **Explore Documentation**
   - [FEATURES.md](FEATURES.md) - Complete feature list
   - [TESTING.md](TESTING.md) - Testing guide
   - [examples/README.md](examples/README.md) - Example documentation

2. **Try Advanced Features**
   - Create custom deployment images
   - Set up automated optimization
   - Build custom app deployment lists

3. **Customize Configuration**
   - Modify existing profiles
   - Create your own profiles
   - Export/import configurations

4. **Contribute**
   - Report issues
   - Submit pull requests
   - Share your workflows

---

## 💡 Pro Tips

1. **Always backup first**: Create restore points before major changes
2. **Test in VM**: Try workflows in a virtual machine first
3. **Use dry-run**: Many operations support dry-run mode
4. **Check logs**: Enable verbose mode for debugging
5. **Save configs**: Export your configurations for reuse

---

## 🎯 Quick Reference

| Task | Command |
|------|---------|
| Launch TUI | `python -m better11 tui` |
| Launch GUI | `python -m better11 gui` |
| Fresh install | `python examples/fresh_install_optimization.py` |
| Install apps | `python examples/bulk_app_installation.py --profile <name>` |
| Backup drivers | `python examples/driver_backup_update.py` |
| Create image | `python examples/create_deployment_image.py <options>` |
| Run tests | `pytest` |
| Load config | `python -c "from better11.config_manager import ConfigManager; c=ConfigManager(); c.apply_profile('<name>'); c.save()"` |

---

## ✅ You're Ready!

You now know how to:
- ✅ Install Better11
- ✅ Launch TUI and GUI
- ✅ Run example workflows
- ✅ Use Python API
- ✅ Configure the system
- ✅ Troubleshoot issues

**Happy optimizing!** 🚀

---

**Need more help?**
- 📖 [Full Documentation](FEATURES.md)
- 🐛 [Report Issues](https://github.com/Cornman92/Better11/issues)
- 💬 [Ask Questions](https://github.com/Cornman92/Better11/discussions)
