# Building and Running Better11

## Prerequisites

### PowerShell Backend
- PowerShell 5.1 or higher
- Windows 11 (build 22000+)
- Administrator privileges

### C# Frontend + WinUI 3
- Visual Studio 2022 (17.8+)
- .NET 8.0 SDK
- Windows App SDK
- Windows 11 SDK (10.0.22621.0)

## Quick Start

### 1. PowerShell Backend

```powershell
# Navigate to PowerShell directory
cd powershell/Better11

# Import module
Import-Module .\Better11.psd1 -Force

# Verify installation
Get-Module Better11
Get-Command -Module Better11

# Test basic functionality
Get-Better11Apps
```

### 2. C# + WinUI 3 GUI

#### Option A: Visual Studio
```bash
# Open solution
cd csharp
start Better11.sln

# Build: Ctrl+Shift+B
# Run: F5 or Ctrl+F5
```

#### Option B: Command Line
```bash
cd csharp

# Restore packages
dotnet restore

# Build solution
dotnet build Better11.sln

# Run WinUI app (requires x64 or ARM64)
dotnet run --project Better11.WinUI/Better11.WinUI.csproj
```

### 3. Python (Original)

```bash
cd python

# Install dependencies
pip install -r requirements.txt

# Run CLI
python -m better11.cli list

# Run GUI
python -m better11.gui
```

## Development Workflow

### PowerShell Development

1. Make changes to .ps1 files
2. Re-import module: `Import-Module .\Better11.psd1 -Force`
3. Test: `Invoke-Pester -Path .\Tests\`

### C# Development

1. Make changes in Visual Studio or VS Code
2. Build: `dotnet build`
3. Run tests: `dotnet test`
4. Run app: F5 in Visual Studio

### Testing

#### PowerShell (Pester)
```powershell
# Install Pester if needed
Install-Module -Name Pester -MinimumVersion 5.0.0 -Force

# Run all tests
cd powershell/Better11
Invoke-Pester -Path .\Tests\

# Run specific test
Invoke-Pester -Path .\Tests\AppManager.Tests.ps1
```

#### C# (xUnit)
```bash
cd csharp

# Run all tests
dotnet test

# Run with coverage
dotnet test --collect:"XPlat Code Coverage"

# Run specific test
dotnet test --filter "FullyQualifiedName~AppManagerServiceTests"
```

## Debugging

### PowerShell
```powershell
# Enable verbose output
$VerbosePreference = 'Continue'
Get-Better11Apps -Verbose

# Enable debug output
$DebugPreference = 'Continue'
Install-Better11App -AppId "demo-app" -Debug

# View logs
Get-Content "$env:USERPROFILE\.better11\logs\better11.log" -Tail 50
```

### C# + WinUI 3
- Set breakpoints in Visual Studio
- Run with F5 (Debug mode)
- View Output window for logs
- Use Debug Console for interactive debugging

## Common Issues

### PowerShell

**Issue**: Module not found
```powershell
# Solution: Check module path
$env:PSModulePath -split ';'
Import-Module .\Better11.psd1 -Force -Verbose
```

**Issue**: Access denied
```powershell
# Solution: Run as administrator
Start-Process powershell -Verb RunAs
```

### C#

**Issue**: Build fails with SDK errors
```bash
# Solution: Clean and restore
dotnet clean
dotnet restore
dotnet build
```

**Issue**: WinUI app won't start
```bash
# Solution: Check platform (must be x64 or ARM64)
dotnet build -r win-x64
```

## Package Structure

### PowerShell Module
```
Better11/
├── Better11.psd1          # Module manifest
├── Better11.psm1          # Main module
├── Modules/               # Sub-modules
│   ├── AppManager/
│   ├── SystemTools/
│   ├── Security/
│   ├── Common/
│   └── Updates/
├── Data/
│   └── catalog.json       # Application catalog
└── Tests/                 # Pester tests
```

### C# Solution
```
Better11.sln
├── Better11.Core/         # Core library
├── Better11.WinUI/        # WinUI 3 app
└── Better11.Tests/        # xUnit tests
```

## Next Steps

1. Review [MIGRATION_PLAN_POWERSHELL_CSHARP_WINUI3.md](MIGRATION_PLAN_POWERSHELL_CSHARP_WINUI3.md)
2. Check [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) for progress
3. See [README_MIGRATION.md](README_MIGRATION.md) for architecture overview
4. Read module-specific READMEs in `powershell/` and `csharp/`

## Support

- PowerShell help: `Get-Help <command> -Full`
- API documentation: See `API_REFERENCE.md`
- Issues: GitHub Issues
