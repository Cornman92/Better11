# Better11 - PowerShell Backend + C# Frontend + WinUI 3 GUI

This repository now contains **three implementations** of Better11:

1. **Python** (Original) - `python/` directory
2. **PowerShell Backend** (New) - `powershell/` directory  
3. **C# + WinUI 3 Frontend** (New) - `csharp/` directory

## 🎯 Quick Start

### PowerShell Backend

```powershell
# Import the PowerShell module
cd powershell/Better11
Import-Module .\Better11.psd1

# Use PowerShell commands
Get-Better11Apps
Install-Better11App -AppId "demo-app"
```

### C# + WinUI 3 GUI

```bash
# Open in Visual Studio 2022
cd csharp
start Better11.sln

# Or run directly
dotnet run --project Better11.WinUI/Better11.WinUI.csproj
```

### Python (Original)

```bash
# Install Python dependencies
cd python
pip install -r requirements.txt

# Run CLI
python -m better11.cli list

# Run GUI
python -m better11.gui
```

## 📊 Feature Comparison

| Feature | Python | PowerShell | C# + WinUI 3 |
|---------|--------|------------|--------------|
| Application Management | ✅ | ✅ | ✅ |
| System Tools | ✅ | ✅ | ✅ |
| Security Verification | ✅ | ✅ | ✅ |
| CLI Interface | ✅ | ✅ | ⚠️ Planned |
| GUI Interface | ✅ Tkinter | ❌ | ✅ WinUI 3 |
| Native Windows Integration | ⚠️ Via ctypes | ✅ Full | ✅ Full |
| Performance | Good | Excellent | Excellent |
| Windows 11 UI | Basic | N/A | ✅ Modern |

## 🏗️ Architecture

### PowerShell Backend

Native PowerShell modules for system operations:

```
powershell/Better11/
├── Modules/
│   ├── AppManager/      # App installation
│   ├── SystemTools/     # Registry, bloatware, services
│   ├── Security/        # Code signing, hash verification
│   ├── Common/          # Shared utilities
│   └── Updates/         # Windows Update management
└── Data/
    └── catalog.json     # Application catalog
```

### C# Frontend

Modern C# services calling PowerShell backend:

```
csharp/
├── Better11.Core/          # Core library
│   ├── Models/            # Data models
│   ├── Services/          # Business logic
│   ├── PowerShell/        # PS executor
│   └── Interfaces/        # Service contracts
└── Better11.WinUI/        # WinUI 3 GUI
    ├── Views/             # XAML pages
    ├── ViewModels/        # MVVM view models
    └── Controls/          # Custom controls
```

## 🔄 Interoperability

The C# frontend communicates with the PowerShell backend seamlessly:

```csharp
// C# calls PowerShell functions
var apps = await _appManager.ListAvailableAppsAsync();
// Internally calls: Get-Better11Apps

var result = await _appManager.InstallAppAsync("vscode");
// Internally calls: Install-Better11App -AppId "vscode"
```

## 🎨 WinUI 3 Features

The new GUI provides:

- **Modern Windows 11 UI** - Fluent Design System
- **Dark/Light Themes** - System theme support
- **MVVM Architecture** - Clean, testable code
- **Async Operations** - Non-blocking UI
- **Rich Controls** - NavigationView, InfoBar, etc.
- **Accessibility** - Full keyboard and screen reader support

## 🚀 Installation & Usage

### For End Users

**Option 1: WinUI 3 Application (Recommended)**
```bash
# Install from Microsoft Store (Coming Soon)
winget install Better11

# Or download standalone installer
# https://github.com/yourusername/better11/releases
```

**Option 2: PowerShell Module**
```powershell
# Install from PowerShell Gallery (Coming Soon)
Install-Module -Name Better11

# Or manual install
git clone https://github.com/yourusername/better11.git
Import-Module ./powershell/Better11/Better11.psd1
```

**Option 3: Python (Legacy)**
```bash
git clone https://github.com/yourusername/better11.git
cd better11/python
pip install -r requirements.txt
python -m better11.gui
```

### For Developers

```bash
# Clone repository
git clone https://github.com/yourusername/better11.git
cd better11

# PowerShell development
cd powershell
Import-Module .\Better11\Better11.psd1

# C# development
cd csharp
dotnet build Better11.sln
dotnet run --project Better11.WinUI

# Python development
cd python
pip install -r requirements.txt -e .
pytest
```

## 📚 Documentation

- **[Migration Plan](MIGRATION_PLAN_POWERSHELL_CSHARP_WINUI3.md)** - Complete migration guide
- **[PowerShell API](powershell/README.md)** - PowerShell module documentation
- **[C# API](csharp/README.md)** - C# frontend documentation
- **[Python API](python/API_REFERENCE.md)** - Original Python documentation

## 🧪 Testing

### PowerShell
```powershell
Invoke-Pester -Path .\powershell\Better11\Tests\
```

### C#
```bash
dotnet test csharp/Better11.sln
```

### Python
```bash
cd python
pytest
```

## 🤝 Contributing

We welcome contributions to all three implementations!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 📝 License

MIT License - See [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Original Python implementation preserved and maintained
- PowerShell backend built on Windows PowerShell best practices
- WinUI 3 GUI using Microsoft's modern UI framework
- MVVM Toolkit from .NET Community Toolkit

## 📧 Support

- 📖 [Documentation](docs/)
- 🐛 [Issue Tracker](https://github.com/yourusername/better11/issues)
- 💬 [Discussions](https://github.com/yourusername/better11/discussions)

---

**Note**: All three implementations are fully functional and maintained. Choose based on your needs:

- **WinUI 3** - Best user experience, modern Windows 11 UI
- **PowerShell** - Maximum flexibility, scripting, automation
- **Python** - Cross-platform development, original implementation
