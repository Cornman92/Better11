# Better11

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform: Windows 11](https://img.shields.io/badge/platform-Windows%2011-blue.svg)](https://www.microsoft.com/windows)

An all-around Windows 11 system enhancement toolkit providing secure application management and system optimization tools.

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

```bash
# Clone the repository
git clone https://github.com/yourusername/better11.git
cd better11

# Install dependencies (if any)
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

- **[Installation Guide](INSTALL.md)** - Detailed setup instructions
- **[User Guide](USER_GUIDE.md)** - Comprehensive usage documentation
- **[API Reference](API_REFERENCE.md)** - Complete API documentation
- **[Architecture](ARCHITECTURE.md)** - System design and architecture
- **[Contributing](CONTRIBUTING.md)** - Development guidelines
- **[Security](SECURITY.md)** - Security policies and reporting
- **[Changelog](CHANGELOG.md)** - Version history and changes

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

- **Operating System**: Windows 11 (some features may work on Windows 10)
- **Python**: 3.8 or higher
- **Privileges**: Administrator rights required for system modifications

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

## Disclaimer

⚠️ **Important**: Better11 modifies system settings and installs software. While safety features are built-in:
- Always create backups before using
- Test in a virtual machine first
- Review all operations before confirming
- Use at your own risk

## Support

- 📖 [Documentation](docs/)
- 🐛 [Issue Tracker](https://github.com/yourusername/better11/issues)
- 💬 [Discussions](https://github.com/yourusername/better11/discussions)

## Acknowledgments

Better11 was created to simplify Windows 11 customization and application management while maintaining security and safety standards.
