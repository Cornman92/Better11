# Better11 PowerShell Backend

PowerShell modules providing system management functionality for Better11.

## 📦 Installation

### From Source

```powershell
# Clone the repository
git clone https://github.com/yourusername/better11.git
cd better11/powershell

# Import the module
Import-Module .\Better11\Better11.psd1

# Verify installation
Get-Module Better11
```

### From PowerShell Gallery (Coming Soon)

```powershell
Install-Module -Name Better11 -Repository PSGallery
```

## 🚀 Quick Start

### Application Management

```powershell
# List available applications
Get-Better11Apps

# Install an application
Install-Better11App -AppId "vscode"

# Uninstall an application
Uninstall-Better11App -AppId "vscode"

# Check installation status
Get-Better11Apps -Installed
```

### System Tools

```powershell
# Apply registry tweaks
$tweaks = @(
    @{Hive='HKCU'; Path='Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced'; Name='HideFileExt'; Value=0; Type='DWord'}
)
Set-Better11RegistryTweak -Tweaks $tweaks

# Remove bloatware
Remove-Better11Bloatware -Preset Moderate

# Apply privacy settings
Set-Better11PrivacySetting -Preset MaximumPrivacy
```

### Security Functions

```powershell
# Verify code signature
Test-Better11CodeSignature -FilePath "C:\installer.exe"

# Verify file hash
Verify-Better11FileHash -FilePath "C:\file.zip" -ExpectedHash "abc123..."

# Create restore point
New-Better11RestorePoint -Description "Before changes"
```

## 📚 Module Structure

```
Better11/
├── Better11.psd1           # Module manifest
├── Better11.psm1           # Main module
├── Modules/
│   ├── AppManager/         # Application management
│   ├── SystemTools/        # System optimization
│   ├── Security/           # Security & verification
│   ├── Common/             # Common utilities
│   └── Updates/            # Windows Update management
├── Data/
│   └── catalog.json        # Application catalog
└── Tests/                  # Pester tests
```

## 🔧 Requirements

- PowerShell 5.1 or higher
- Windows 11 (build 22000 or higher)
- Administrator privileges for system modifications

## 📖 Documentation

See the [main documentation](../MIGRATION_PLAN_POWERSHELL_CSHARP_WINUI3.md) for complete API reference and examples.

## 🧪 Testing

```powershell
# Run all tests
Invoke-Pester -Path .\Tests\

# Run specific test
Invoke-Pester -Path .\Tests\AppManager.Tests.ps1
```

## 📝 License

MIT License - See [LICENSE](../LICENSE) file for details.
