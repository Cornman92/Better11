# Better11 Examples

This directory contains practical examples demonstrating how to use Better11's features.

## Examples Overview

### 1. Fresh Install Optimization (`fresh_install_optimization.py`)

Optimizes a fresh Windows 11 installation for gaming and performance.

**Features:**
- System metrics collection
- Windows Update check and installation
- Driver verification and backup
- Essential application installation
- Gaming mode optimization
- System cleanup

**Usage:**
```bash
python examples/fresh_install_optimization.py
```

**When to use:**
- After clean Windows installation
- When setting up a new PC
- For performance optimization

---

### 2. Create Deployment Image (`create_deployment_image.py`)

Creates a customized Windows installation image with drivers, updates, and optimizations.

**Features:**
- Export/copy Windows image
- Inject drivers into offline image
- Inject Windows updates
- Image optimization and compression

**Usage:**
```bash
# Basic usage
python examples/create_deployment_image.py --source install.wim --output custom.wim

# With drivers and updates
python examples/create_deployment_image.py \
    --source install.wim \
    --output custom.wim \
    --drivers C:\Drivers \
    --updates C:\Updates \
    --optimize

# Specify index
python examples/create_deployment_image.py \
    --source install.wim \
    --output custom.wim \
    --index 2 \
    --drivers C:\Drivers
```

**When to use:**
- Creating standardized deployment images
- Enterprise deployment scenarios
- Including drivers/updates in base image

---

### 3. Driver Backup and Update (`driver_backup_update.py`)

Backs up all installed drivers and checks for missing drivers.

**Features:**
- List all installed drivers
- Driver breakdown by class
- Complete driver backup
- Missing driver detection
- Backup logging

**Usage:**
```bash
python examples/driver_backup_update.py
```

**When to use:**
- Before major system changes
- Before Windows reinstallation
- For disaster recovery preparation
- When troubleshooting driver issues

---

### 4. Bulk App Installation (`bulk_app_installation.py`)

Installs multiple applications using predefined profiles or custom lists.

**Features:**
- Predefined app profiles (gaming, development, productivity, media)
- Custom app list support
- Multi-package manager support (WinGet, Chocolatey, NPM, Pip)
- Dry-run mode
- Installation progress tracking

**Usage:**
```bash
# Use predefined profile
python examples/bulk_app_installation.py --profile gaming
python examples/bulk_app_installation.py --profile development

# Use custom app list
python examples/bulk_app_installation.py --custom my_apps.txt

# Dry run (preview only)
python examples/bulk_app_installation.py --profile gaming --dry-run
```

**Custom app list format (`my_apps.txt`):**
```
# Application Name, Package ID, Manager
Visual Studio Code, Microsoft.VisualStudioCode, winget
Chrome, Google.Chrome, winget
Slack, Slack.Slack, winget
```

**Available profiles:**
- `gaming`: Steam, Discord, OBS Studio, MSI Afterburner
- `development`: Git, VSCode, Python, Node.js, Docker
- `productivity`: 7-Zip, Notepad++, Chrome, VLC, Zoom
- `media`: VLC, Spotify, Audacity, HandBrake

**When to use:**
- Setting up new development environment
- Installing apps on multiple machines
- Standardizing software deployment

---

## General Usage Tips

### Prerequisites

All examples require:
- Windows 11 (build 22621+)
- Python 3.8+
- Administrator privileges (for most operations)
- Better11 installed: `pip install -r requirements.txt`

### Running Examples

1. **Navigate to Better11 directory:**
   ```bash
   cd Better11
   ```

2. **Run example:**
   ```bash
   python examples/example_name.py
   ```

3. **Follow on-screen prompts**

### Common Options

Most examples support:
- Interactive prompts (y/n)
- Verbose output
- Error handling and recovery
- Progress indicators

### Error Handling

If an example fails:
1. Check you have administrator privileges
2. Verify required tools are installed (DISM, package managers, etc.)
3. Check error messages for specific issues
4. Consult the main documentation

---

## Creating Custom Examples

You can create your own examples using Better11's modules:

```python
import sys
from pathlib import Path

# Add Better11 to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import modules
from better11.system_optimizer import SystemOptimizer
from better11.package_manager import UnifiedPackageManager
# ... etc

# Your code here
```

### Available Modules

- `better11.image_manager` - Image management
- `better11.iso_manager` - ISO/USB creation
- `better11.update_manager` - Windows updates
- `better11.driver_manager` - Driver management
- `better11.package_manager` - Package management
- `better11.system_optimizer` - System optimization
- `better11.file_manager` - File operations

---

## Contributing

Have a useful workflow? Create an example and submit a PR!

**Example template:**
```python
"""
Example: Your Example Name

Brief description of what this example does.

Usage:
    python examples/your_example.py

Requirements:
    - List requirements here
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Your imports and code

def main():
    # Your main logic
    pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: {e}")
        sys.exit(1)
```

---

## Support

For issues or questions:
- Check the main [README.md](../README.md)
- Review [FEATURES.md](../FEATURES.md) for module documentation
- Open an issue on GitHub

---

**Version:** 0.3.0
**Last Updated:** 2024-12-19
