# Build Steps - Better11 C# & WinUI 3

Quick reference guide for building and running the Better11 solution.

## Prerequisites

1. **Windows 11** (required for WinUI 3)
2. **Visual Studio 2022** (17.3+) with:
   - .NET 8.0 SDK
   - Windows App SDK
   - WinUI 3 workload
   - C# development tools

## Quick Start

### Option 1: Visual Studio (Recommended)

```powershell
# Open solution
cd /workspace/csharp
start Better11.sln

# In Visual Studio:
# 1. Set "Better11.WinUI" as startup project
# 2. Build → Build Solution (Ctrl+Shift+B)
# 3. Debug → Start Debugging (F5)
```

### Option 2: Command Line

```powershell
cd /workspace/csharp

# Restore packages
dotnet restore

# Build solution
dotnet build

# Run tests
dotnet test

# Run WinUI app (requires VS or Windows App SDK)
# Note: WinUI apps typically need to be packaged
```

## Project Structure

```
Better11.sln
├── Better11.Core/              # Core library (services, interfaces, models)
│   ├── Models/                 # Data models
│   ├── Interfaces/             # Service interfaces
│   ├── Services/               # Service implementations
│   └── PowerShell/             # PowerShell executor
├── Better11.WinUI/             # WinUI 3 application
│   ├── Views/                  # XAML pages
│   ├── ViewModels/             # MVVM view models
│   └── App.xaml                # Application entry
└── Better11.Tests/             # xUnit tests
    └── Services/               # Service tests
```

## Build Configurations

### Debug Build
- Includes debug symbols
- No optimizations
- Detailed logging

```powershell
dotnet build -c Debug
```

### Release Build
- Optimized code
- Minimal logging
- Production-ready

```powershell
dotnet build -c Release
```

## Running Tests

### All Tests
```powershell
dotnet test
```

### Specific Test Project
```powershell
dotnet test Better11.Tests/Better11.Tests.csproj
```

### With Detailed Output
```powershell
dotnet test --logger "console;verbosity=detailed"
```

## Common Issues

### 1. PowerShell Module Not Found

**Error**: "Better11 module not found"

**Solution**: Ensure PowerShell module is in the right location:
```powershell
# Check module path
$env:PSModulePath -split ';'

# Copy module to user modules
Copy-Item -Recurse -Force `
  /workspace/powershell/Better11 `
  "$env:USERPROFILE\Documents\PowerShell\Modules\"
```

### 2. Administrator Privileges Required

**Error**: "This application requires administrator privileges"

**Solution**: Run Visual Studio or your terminal as Administrator

### 3. WinUI 3 Build Errors

**Error**: "Windows App SDK not found"

**Solution**: Install Windows App SDK:
```powershell
# Download from: https://learn.microsoft.com/windows/apps/windows-app-sdk/downloads
# Or use Visual Studio Installer to add WinUI 3 workload
```

### 4. NuGet Package Restore Fails

**Solution**:
```powershell
# Clear NuGet cache
dotnet nuget locals all --clear

# Restore packages
dotnet restore
```

## Deployment

### 1. Create MSIX Package (Recommended)

**In Visual Studio**:
1. Right-click `Better11.WinUI` project
2. Select "Publish" → "Create App Packages"
3. Follow wizard to create MSIX package

### 2. Standalone Deployment

```powershell
# Publish as self-contained
dotnet publish Better11.WinUI/Better11.WinUI.csproj `
  -c Release `
  -r win10-x64 `
  --self-contained true `
  -o ./publish
```

### 3. Framework-Dependent Deployment

```powershell
# Requires .NET 8 runtime on target machine
dotnet publish Better11.WinUI/Better11.WinUI.csproj `
  -c Release `
  -r win10-x64 `
  --self-contained false `
  -o ./publish
```

## Development Workflow

### 1. Adding a New Feature

```bash
# 1. Create interface in Better11.Core/Interfaces/
# 2. Implement service in Better11.Core/Services/
# 3. Create models in Better11.Core/Models/
# 4. Add tests in Better11.Tests/
# 5. Create ViewModel in Better11.WinUI/ViewModels/
# 6. Create View in Better11.WinUI/Views/
# 7. Register in App.xaml.cs
```

### 2. Running PowerShell Commands

```csharp
// In any service
var result = await _psExecutor.ExecuteCommandAsync(
    "Get-Better11Apps");

if (!result.HadErrors)
{
    foreach (var item in result.Output)
    {
        // Process results
    }
}
```

### 3. Adding Dependencies

```powershell
# Add NuGet package
dotnet add Better11.Core package PackageName

# Update all packages
dotnet list package --outdated
dotnet add package PackageName
```

## Performance Tips

1. **Use Release builds** for performance testing
2. **Enable parallel build** in Visual Studio
3. **Minimize PowerShell calls** - batch operations when possible
4. **Use async/await** throughout the application
5. **Implement cancellation tokens** for long-running operations

## Debugging

### Debug PowerShell Execution

```csharp
// Enable verbose logging in PowerShellExecutor
var result = await _psExecutor.ExecuteScriptAsync(
    script, 
    captureOutput: true);

_logger.LogDebug("PS Output: {Output}", result.Output);
_logger.LogDebug("PS Errors: {Errors}", result.Errors);
```

### Debug View Bindings

```xml
<!-- Enable data binding debugging in XAML -->
<Page xmlns:diag="using:Microsoft.UI.Xaml.Diagnostics">
    <!-- Your content -->
</Page>
```

### Attach to Running Process

1. Debug → Attach to Process (Ctrl+Alt+P)
2. Select "Better11.WinUI.exe"
3. Set breakpoints and continue

## Additional Resources

- [WinUI 3 Documentation](https://learn.microsoft.com/windows/apps/winui/winui3/)
- [.NET 8 Documentation](https://learn.microsoft.com/dotnet/core/whats-new/dotnet-8)
- [MVVM Toolkit](https://learn.microsoft.com/windows/communitytoolkit/mvvm/introduction)
- [PowerShell SDK](https://learn.microsoft.com/powershell/scripting/developer/hosting/windows-powershell-host-quickstart)

## Support

For issues or questions:
1. Check `BUILD_AND_RUN.md` for comprehensive guide
2. Review `FINAL_DELIVERABLES.md` for architecture details
3. See PowerShell documentation in `/workspace/powershell/README.md`
