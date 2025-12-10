# Installation Guide

This guide provides detailed instructions for installing and setting up Better11 on your Windows 11 system.

## Table of Contents

- [System Requirements](#system-requirements)
- [Installation Methods](#installation-methods)
- [Post-Installation Setup](#post-installation-setup)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Uninstallation](#uninstallation)

## System Requirements

### Operating System
- **Windows 11** (most features)
- Windows 10 21H2 or later (limited compatibility)
- Administrator privileges required for system modifications

### Software Requirements
- **Python**: 3.8 or higher
  - Python 3.9, 3.10, or 3.11 recommended
  - Python 3.12 supported
- **Git**: For cloning the repository (optional)

### Hardware Requirements
- **CPU**: Any modern x64 processor
- **RAM**: 2GB minimum (4GB recommended)
- **Disk Space**: 100MB for Better11 + space for downloaded applications
- **Network**: Internet connection for downloading applications

### Permissions
- Administrator rights required for:
  - Installing applications
  - Modifying registry
  - Managing Windows services
  - Removing bloatware packages
  - Creating system restore points

## Installation Methods

### Method 1: Git Clone (Recommended)

**Step 1: Install Python**

1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. **Important**: Check "Add Python to PATH"
4. Choose "Install Now" or customize installation

**Step 2: Install Git** (if not already installed)

1. Download Git from [git-scm.com](https://git-scm.com/)
2. Run the installer with default options

**Step 3: Clone Repository**

```bash
# Open Command Prompt or PowerShell
cd C:\Users\YourUsername\Documents
git clone https://github.com/yourusername/better11.git
cd better11
```

**Step 4: Verify Installation**

```bash
# Check Python version
python --version

# List available applications
python -m better11.cli list
```

### Method 2: Download ZIP

**Step 1: Download**

1. Go to the Better11 repository on GitHub
2. Click the green "Code" button
3. Select "Download ZIP"
4. Extract the ZIP file to your desired location

**Step 2: Open Terminal**

```bash
cd C:\path\to\extracted\better11
```

**Step 3: Verify Installation**

```bash
python -m better11.cli list
```

### Method 3: Development Installation

For contributors and developers:

**Step 1: Clone and Setup**

```bash
# Clone the repository
git clone https://github.com/yourusername/better11.git
cd better11

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install development dependencies (if requirements-dev.txt exists)
pip install -r requirements-dev.txt
```

**Step 2: Install in Editable Mode**

```bash
# If setup.py exists
pip install -e .

# Or just use the modules directly
python -m better11.cli list
```

## Post-Installation Setup

### 1. Create Data Directories

Better11 automatically creates directories under `~/.better11/` on first use:

```
C:\Users\YourUsername\.better11\
├── downloads\         # Downloaded installers
└── installed.json     # Installation state
```

You can manually create these directories if desired:

```bash
mkdir %USERPROFILE%\.better11
mkdir %USERPROFILE%\.better11\downloads
```

### 2. Configure Catalog (Optional)

To use a custom application catalog:

1. Copy the default catalog:
   ```bash
   copy better11\apps\catalog.json my-catalog.json
   ```

2. Edit `my-catalog.json` to add your applications

3. Use the custom catalog:
   ```bash
   python -m better11.cli --catalog my-catalog.json list
   ```

### 3. Set Up Environment Variables (Optional)

For easier command-line usage:

**PowerShell**:
```powershell
$env:BETTER11_HOME = "C:\path\to\better11"
$env:PATH += ";$env:BETTER11_HOME"
```

**Command Prompt**:
```cmd
set BETTER11_HOME=C:\path\to\better11
set PATH=%PATH%;%BETTER11_HOME%
```

To make permanent, add to System Environment Variables via:
- Control Panel → System → Advanced System Settings → Environment Variables

### 4. Create Desktop Shortcuts (Optional)

**For GUI**:

1. Right-click on Desktop → New → Shortcut
2. Target: `C:\path\to\python.exe "C:\path\to\better11\better11\gui.py"`
3. Name: "Better11"
4. Click Finish

**For CLI**:

Create a batch file `better11.bat`:

```batch
@echo off
cd C:\path\to\better11
python -m better11.cli %*
```

Add the batch file location to your PATH.

## Verification

### Test Installation

**1. Check Python**:
```bash
python --version
# Should output: Python 3.x.x
```

**2. Test CLI**:
```bash
# Navigate to better11 directory
cd C:\path\to\better11

# List applications
python -m better11.cli list

# Check status
python -m better11.cli status
```

Expected output:
```
demo-appx | Demo AppX Package v1.0.0 | appx
demo-exe | Demo EXE Installer v1.0.0 | exe
demo-app | Demo MSI Installer v1.0.0 | msi
```

**3. Test GUI**:
```bash
python -m better11.gui
```

A window should open showing the application list.

**4. Test System Tools** (requires administrator):

```python
# Test in Python interactive mode
python

>>> from system_tools.safety import ensure_windows
>>> ensure_windows()
>>> # No error means Windows is detected
>>> exit()
```

> **Note:** For CI or local development on non-Windows hosts, Better11's
> system tools can bypass the platform guard by setting the environment
> variable ``BETTER11_ALLOW_NON_WINDOWS=1`` or by passing
> ``allow_non_windows=True`` in tool configuration. Production deployments
> should keep the default enforcement to avoid running Windows-specific
> commands on unsupported platforms.

### Verify Administrator Access

Many features require administrator privileges. To run as administrator:

**PowerShell**:
```powershell
# Right-click PowerShell → "Run as Administrator"
cd C:\path\to\better11
python -m better11.cli list
```

**Command Prompt**:
```cmd
# Right-click Command Prompt → "Run as Administrator"
cd C:\path\to\better11
python -m better11.cli list
```

## Troubleshooting

### Common Issues

#### Python Not Found

**Error**: `'python' is not recognized as an internal or external command`

**Solution**:
1. Reinstall Python with "Add to PATH" option checked
2. Or manually add Python to PATH:
   - Find Python installation (usually `C:\Users\YourUsername\AppData\Local\Programs\Python\Python3x\`)
   - Add to PATH environment variable

#### Module Not Found

**Error**: `No module named 'better11'`

**Solution**:
```bash
# Make sure you're in the better11 directory
cd C:\path\to\better11

# Check if better11 directory exists
dir better11
```

#### Permission Denied

**Error**: `PermissionError: [WinError 5] Access is denied`

**Solution**:
- Run Command Prompt or PowerShell as Administrator
- Right-click the program → "Run as Administrator"

#### Catalog Not Found

**Error**: `FileNotFoundError: catalog.json not found`

**Solution**:
```bash
# Verify catalog exists
dir better11\apps\catalog.json

# Use absolute path
python -m better11.cli --catalog "C:\path\to\better11\better11\apps\catalog.json" list
```

#### GUI Doesn't Start

**Error**: GUI window doesn't appear or crashes

**Solution**:
1. Check Python tkinter support:
   ```bash
   python -c "import tkinter"
   ```
   
2. If tkinter is missing, reinstall Python with tcl/tk option

3. Check for error messages:
   ```bash
   python -m better11.gui 2> error.log
   type error.log
   ```

#### System Tools Don't Work

**Error**: `SafetyError: Windows platform is required`

**Solution**:
- Some system tools only work on Windows
- Ensure you're running on Windows 11
- Run as Administrator

### Getting Help

If you encounter issues:

1. **Check Documentation**: Read [USER_GUIDE.md](USER_GUIDE.md)
2. **Search Issues**: Look for similar issues on GitHub
3. **Create Issue**: Report bugs with detailed information:
   - Python version (`python --version`)
   - Windows version
   - Error message and full traceback
   - Steps to reproduce

## Uninstallation

### Remove Better11

**Method 1: Simple Deletion**

If installed via git clone or ZIP:

```bash
# Delete the directory
rmdir /s C:\path\to\better11
```

**Method 2: Clean Uninstall**

Remove all Better11 files and data:

```bash
# 1. Remove Better11 directory
rmdir /s C:\path\to\better11

# 2. Remove user data (optional)
rmdir /s %USERPROFILE%\.better11

# 3. Remove environment variables (if set)
# Via Control Panel → System → Environment Variables
```

### Uninstall Applications

Before removing Better11, you may want to uninstall managed applications:

```bash
# List installed applications
python -m better11.cli status

# Uninstall each application
python -m better11.cli uninstall app-id-here

# Or manually uninstall via Windows Settings
```

### Revert System Changes

If you used system tools:

1. **Restore Points**: 
   - Control Panel → System → System Protection
   - Select a restore point created before using Better11
   - Click "System Restore"

2. **Registry Backups**:
   - Better11 creates `.reg` backup files
   - Double-click backup file to restore
   - Located in temporary directory or specified backup location

3. **Service Changes**:
   - Manually revert via `services.msc`
   - Or use Better11 to reverse changes before uninstalling

## Next Steps

After installation:

1. **Read User Guide**: See [USER_GUIDE.md](USER_GUIDE.md) for usage instructions
2. **Review Security**: Read [SECURITY.md](SECURITY.md) for security best practices
3. **Test in VM**: Consider testing system modifications in a virtual machine first
4. **Create Backup**: Create a system restore point before making changes

## Advanced Configuration

### Custom Python Path

If using a non-standard Python installation:

```bash
# Use specific Python version
C:\Python39\python.exe -m better11.cli list

# Or create an alias
doskey better11=C:\Python39\python.exe -m better11.cli $*
```

### Multiple Better11 Installations

You can have multiple Better11 installations for different purposes:

```bash
C:\Better11-Production\    # Stable version
C:\Better11-Testing\       # Testing new features
C:\Better11-Custom\        # Custom catalog
```

Each maintains separate state in `~/.better11/` (unless configured differently).

### Network Proxy Configuration

If behind a corporate proxy:

```bash
# Set environment variables
set HTTP_PROXY=http://proxy.company.com:8080
set HTTPS_PROXY=http://proxy.company.com:8080

# Then run Better11
python -m better11.cli list
```

## System Integration

### PowerShell Profile

Add Better11 to PowerShell profile for quick access:

```powershell
# Edit profile
notepad $PROFILE

# Add these lines:
function better11 {
    python C:\path\to\better11\better11\cli.py $args
}
```

### Task Scheduler

Schedule automated tasks:

1. Open Task Scheduler
2. Create Basic Task
3. Name: "Better11 Update Check"
4. Trigger: Daily
5. Action: Start a program
6. Program: `C:\path\to\python.exe`
7. Arguments: `-m better11.cli status`

## Support

For installation help:

- **Documentation**: [USER_GUIDE.md](USER_GUIDE.md)
- **Issues**: [GitHub Issues](https://github.com/owner/better11/issues)
- **Community**: [Discussions](https://github.com/owner/better11/discussions)

---

**Note**: Better11 is under active development. Installation procedures may change. Check the repository for the latest instructions.
