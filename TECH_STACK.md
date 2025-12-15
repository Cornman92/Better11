# Better11 Technology Stack

## Overview

Better11 is built using modern Windows development technologies, leveraging the latest .NET platform, WinUI3 for the user interface, and PowerShell for system automation. This document details all technologies, frameworks, libraries, and tools used in the project.

---

## Core Technologies

### .NET Platform

**Version**: .NET 8.0 (LTS)
**Rationale**: Long-term support, performance improvements, modern C# features

**Key Features Used**:
- C# 12 language features
- Native AOT compilation support (future consideration)
- Improved performance and smaller memory footprint
- Source generators
- File-scoped namespaces
- Global using directives
- Record types and pattern matching

**Configuration**:
```xml
<PropertyGroup>
  <TargetFramework>net8.0-windows10.0.22621.0</TargetFramework>
  <TargetPlatformMinVersion>10.0.19041.0</TargetPlatformMinVersion>
  <LangVersion>12.0</LangVersion>
  <Nullable>enable</Nullable>
</PropertyGroup>
```

---

### WinUI 3 (Windows App SDK)

**Version**: Windows App SDK 1.5+
**Rationale**: Modern Windows UI framework, follows Windows 11 design language

**Features**:
- Native Windows 11 controls
- Fluent Design System
- High DPI support
- Automatic theme switching (Light/Dark)
- Acrylic and Mica materials
- Modern animations and transitions
- Accessibility built-in

**Key Components Used**:
- NavigationView
- CommandBar
- InfoBar
- TeachingTip
- ProgressRing/ProgressBar
- ContentDialog
- MenuFlyout
- ListView/GridView
- TreeView
- TabView

**NuGet Packages**:
```xml
<PackageReference Include="Microsoft.WindowsAppSDK" Version="1.5.*" />
<PackageReference Include="Microsoft.Windows.SDK.BuildTools" Version="10.0.*" />
<PackageReference Include="Microsoft.Graphics.Win2D" Version="1.2.*" />
```

---

### MVVM Framework

**Library**: CommunityToolkit.Mvvm (MVVM Toolkit)
**Version**: 8.2+
**Rationale**: Official Microsoft MVVM toolkit, source generators, high performance

**Features**:
- `ObservableObject` base class
- `RelayCommand` and `AsyncRelayCommand`
- Source generators for boilerplate reduction
- `ObservableProperty` attribute
- `IMessenger` for loose coupling
- `ObservableValidator` for validation

**Example Usage**:
```csharp
[ObservableObject]
public partial class ImageEditorViewModel
{
    [ObservableProperty]
    private string? _imagePath;

    [ObservableProperty]
    private bool _isLoading;

    [RelayCommand]
    private async Task LoadImageAsync()
    {
        IsLoading = true;
        // Load image logic
        IsLoading = false;
    }
}
```

**NuGet Packages**:
```xml
<PackageReference Include="CommunityToolkit.Mvvm" Version="8.2.*" />
```

---

## Windows Integration

### PowerShell Integration

**Technology**: System.Management.Automation
**Version**: 7.4+
**Rationale**: Powerful scripting engine for Windows automation

**Features**:
- Execute PowerShell scripts
- Run PowerShell cmdlets programmatically
- Access PowerShell modules
- Capture output and errors
- Async execution
- Runspace pooling

**Example**:
```csharp
using System.Management.Automation;

public async Task<PSObject[]> ExecuteScriptAsync(string script)
{
    using var ps = PowerShell.Create();
    ps.AddScript(script);
    var results = await Task.Run(() => ps.Invoke());
    return results.ToArray();
}
```

**NuGet Packages**:
```xml
<PackageReference Include="Microsoft.PowerShell.SDK" Version="7.4.*" />
<PackageReference Include="System.Management.Automation" Version="7.4.*" />
```

---

### Windows API Access

**Technology**: Windows API (P/Invoke, CsWin32)
**Rationale**: Direct access to native Windows functionality

**CsWin32**: Source generator for Windows API
```xml
<PackageReference Include="Microsoft.Windows.CsWin32" Version="0.3.*">
  <PrivateAssets>all</PrivateAssets>
</PackageReference>
```

**NativeMethods.txt**:
```
GetVersionEx
RegOpenKeyEx
RegQueryValueEx
CreateProcess
```

**Common APIs Used**:
- Registry manipulation
- Process management
- Service control
- File system operations
- Elevation/UAC
- System information

---

### DISM (Deployment Image Servicing and Management)

**Technology**: DISM API / PowerShell DISM module
**Rationale**: Official Windows image manipulation API

**Access Methods**:
1. **PowerShell DISM Module** (Primary)
   - Easy to use
   - Rich functionality
   - Microsoft supported

2. **DISM.exe** (Fallback)
   - Command-line interface
   - Process execution
   - Output parsing

**Common Operations**:
```powershell
# Mount image
Mount-WindowsImage -ImagePath "C:\install.wim" -Index 1 -Path "C:\mount"

# Add driver
Add-WindowsDriver -Path "C:\mount" -Driver "C:\drivers"

# Enable feature
Enable-WindowsOptionalFeature -Path "C:\mount" -FeatureName "NetFx3"

# Unmount and commit
Dismount-WindowsImage -Path "C:\mount" -Save
```

---

## Data & Persistence

### SQLite

**Library**: Microsoft.Data.Sqlite
**Version**: 8.0+
**Rationale**: Lightweight, serverless, embedded database

**Use Cases**:
- Application history
- User settings
- Installation profiles
- Activity logs
- Cache storage

**Schema Example**:
```sql
CREATE TABLE ActivityLog (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    ActivityType TEXT NOT NULL,
    Description TEXT,
    Success BOOLEAN,
    Details TEXT
);

CREATE TABLE InstallationProfiles (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Description TEXT,
    Created DATETIME DEFAULT CURRENT_TIMESTAMP,
    ProfileData TEXT -- JSON
);
```

**NuGet Packages**:
```xml
<PackageReference Include="Microsoft.Data.Sqlite" Version="8.0.*" />
<PackageReference Include="Microsoft.Data.Sqlite.Core" Version="8.0.*" />
```

---

### JSON Configuration

**Library**: System.Text.Json
**Rationale**: High performance, built-in, modern JSON handling

**Configuration Files**:
- `appsettings.json` - Application settings
- `appsettings.user.json` - User-specific settings
- Installation profiles
- Export/import data

**Example**:
```csharp
var options = new JsonSerializerOptions
{
    WriteIndented = true,
    PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
    Converters = { new JsonStringEnumConverter() }
};

var json = JsonSerializer.Serialize(profile, options);
```

---

## Package Management Integration

### Winget Integration

**Technology**: winget CLI
**Access**: Process execution, JSON output parsing

**Commands Used**:
```bash
winget search <query> --accept-source-agreements
winget show <package-id>
winget install <package-id> --silent --accept-source-agreements
winget list
winget upgrade
```

**JSON Output**:
```csharp
var result = await ExecuteProcessAsync("winget", "search query --output json");
var packages = JsonSerializer.Deserialize<WingetSearchResult>(result.Output);
```

---

### Chocolatey Integration

**Technology**: choco CLI
**Access**: Process execution, output parsing

**Commands Used**:
```bash
choco search <query>
choco info <package-id>
choco install <package-id> -y
choco list --local-only
choco upgrade all -y
```

---

## Logging & Diagnostics

### Serilog

**Version**: 3.1+
**Rationale**: Structured logging, multiple sinks, high performance

**Configuration**:
```csharp
Log.Logger = new LoggerConfiguration()
    .MinimumLevel.Debug()
    .MinimumLevel.Override("Microsoft", LogEventLevel.Information)
    .Enrich.FromLogContext()
    .Enrich.WithThreadId()
    .Enrich.WithMachineName()
    .WriteTo.Console(
        outputTemplate: "[{Timestamp:HH:mm:ss} {Level:u3}] {Message:lj}{NewLine}{Exception}")
    .WriteTo.File(
        path: "logs/better11-.log",
        rollingInterval: RollingInterval.Day,
        retainedFileCountLimit: 30,
        outputTemplate: "{Timestamp:yyyy-MM-dd HH:mm:ss.fff zzz} [{Level:u3}] {Message:lj}{NewLine}{Exception}")
    .WriteTo.Debug()
    .CreateLogger();
```

**NuGet Packages**:
```xml
<PackageReference Include="Serilog" Version="3.1.*" />
<PackageReference Include="Serilog.Sinks.Console" Version="5.0.*" />
<PackageReference Include="Serilog.Sinks.File" Version="5.0.*" />
<PackageReference Include="Serilog.Sinks.Debug" Version="2.0.*" />
<PackageReference Include="Serilog.Extensions.Logging" Version="8.0.*" />
```

---

## Dependency Injection

### Microsoft.Extensions.DependencyInjection

**Version**: 8.0+
**Rationale**: Standard .NET DI container, well integrated

**Service Registration**:
```csharp
public static class ServiceConfiguration
{
    public static IServiceCollection ConfigureServices(this IServiceCollection services)
    {
        // Infrastructure
        services.AddSingleton<IConfiguration>(LoadConfiguration());
        services.AddLogging(builder => builder.AddSerilog());

        // Services - Singleton
        services.AddSingleton<INavigationService, NavigationService>();
        services.AddSingleton<IDialogService, DialogService>();
        services.AddSingleton<ISecurityService, SecurityService>();
        services.AddSingleton<IConfigurationService, ConfigurationService>();

        // Services - Scoped
        services.AddScoped<IImageService, ImageService>();
        services.AddScoped<IAppService, AppService>();
        services.AddScoped<IFileService, FileService>();

        // ViewModels
        services.AddTransient<DashboardViewModel>();
        services.AddTransient<ImageEditorViewModel>();
        services.AddTransient<AppManagerViewModel>();

        return services;
    }
}
```

**NuGet Packages**:
```xml
<PackageReference Include="Microsoft.Extensions.DependencyInjection" Version="8.0.*" />
<PackageReference Include="Microsoft.Extensions.Configuration" Version="8.0.*" />
<PackageReference Include="Microsoft.Extensions.Configuration.Json" Version="8.0.*" />
<PackageReference Include="Microsoft.Extensions.Logging" Version="8.0.*" />
```

---

## Testing

### Unit Testing

**Framework**: xUnit
**Version**: 2.6+
**Rationale**: Modern, extensible, widely adopted

```csharp
public class ImageServiceTests
{
    private readonly IImageService _imageService;
    private readonly Mock<IWimManager> _mockWimManager;

    public ImageServiceTests()
    {
        _mockWimManager = new Mock<IWimManager>();
        _imageService = new ImageService(_mockWimManager.Object);
    }

    [Fact]
    public async Task LoadImage_ValidPath_ReturnsImage()
    {
        // Arrange
        var path = "test.wim";
        _mockWimManager.Setup(x => x.GetWimInfoAsync(path))
            .ReturnsAsync(new WimInfo());

        // Act
        var result = await _imageService.LoadImageAsync(path);

        // Assert
        Assert.NotNull(result);
    }
}
```

**NuGet Packages**:
```xml
<PackageReference Include="xunit" Version="2.6.*" />
<PackageReference Include="xunit.runner.visualstudio" Version="2.5.*" />
<PackageReference Include="Moq" Version="4.20.*" />
<PackageReference Include="FluentAssertions" Version="6.12.*" />
<PackageReference Include="coverlet.collector" Version="6.0.*" />
```

---

### Integration Testing

**Framework**: MSTest / xUnit
**Tools**: WinAppDriver (UI automation)

```csharp
[TestMethod]
public async Task InstallApplication_ValidPackage_Success()
{
    // Arrange
    var appService = ServiceProvider.GetRequiredService<IAppService>();
    var package = new AppPackage { Id = "Git.Git" };

    // Act
    var result = await appService.InstallAppAsync(package, new InstallOptions());

    // Assert
    Assert.IsTrue(result);
}
```

---

### UI Testing

**Technology**: WinAppDriver + Appium
**Rationale**: Automated UI testing for WinUI3 apps

**Example**:
```csharp
[TestClass]
public class DashboardUITests
{
    private WindowsDriver<WindowsElement> _session;

    [TestInitialize]
    public void Setup()
    {
        var options = new AppiumOptions();
        options.AddAdditionalCapability("app", "Better11.exe");
        _session = new WindowsDriver<WindowsElement>(
            new Uri("http://127.0.0.1:4723"), options);
    }

    [TestMethod]
    public void Dashboard_LoadsSuccessfully()
    {
        var dashboard = _session.FindElementByAccessibilityId("DashboardView");
        Assert.IsNotNull(dashboard);
    }
}
```

---

## Build & Deployment

### MSBuild

**Version**: 17.8+ (Visual Studio 2022)
**Features**:
- Multi-targeting
- Package references
- Custom build tasks
- XAML compilation
- Resource management

**Key Configurations**:
```xml
<PropertyGroup Condition="'$(Configuration)' == 'Release'">
  <Optimize>true</Optimize>
  <TrimMode>partial</TrimMode>
  <PublishTrimmed>true</PublishTrimmed>
  <SelfContained>true</SelfContained>
</PropertyGroup>
```

---

### CI/CD Pipeline

**Platform**: GitHub Actions
**Triggers**: Push, Pull Request, Manual

**Workflow**:
```yaml
name: Build and Test

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: '8.0.x'

      - name: Restore dependencies
        run: dotnet restore

      - name: Build
        run: dotnet build --no-restore --configuration Release

      - name: Test
        run: dotnet test --no-build --verbosity normal --configuration Release

      - name: Publish
        run: dotnet publish --configuration Release --output ./publish
```

---

### Packaging

**MSIX Packaging**
- Microsoft Store distribution
- Automatic updates
- Isolated storage
- Clean uninstall

**Configuration**:
```xml
<PropertyGroup>
  <AppxPackage>true</AppxPackage>
  <AppxPackageDir>$(OutDir)AppPackages\</AppxPackageDir>
  <GenerateAppInstallerFile>true</GenerateAppInstallerFile>
</PropertyGroup>
```

**Traditional Installer**
- Inno Setup or WiX Toolset
- Custom installation options
- Registry integration
- Start menu shortcuts

---

## Development Tools

### Required Tools

1. **Visual Studio 2022** (v17.8+)
   - Workloads:
     - .NET Desktop Development
     - Universal Windows Platform Development
   - Extensions:
     - XAML Styler
     - ReSharper (optional)
     - CodeMaid (optional)

2. **Windows 11 SDK** (10.0.22621.0+)
   - Required for WinUI3 development
   - DISM API access

3. **PowerShell 7.4+**
   - Script development
   - Testing PowerShell integration

4. **Git**
   - Version control
   - GitHub integration

### Recommended Tools

1. **Windows Terminal**
   - Modern terminal experience
   - PowerShell integration

2. **Visual Studio Code**
   - Markdown editing
   - JSON editing
   - PowerShell script development

3. **WinDbg Preview**
   - Debugging crashes
   - Memory dump analysis

4. **Process Monitor (Sysinternals)**
   - Monitor file/registry operations
   - Debugging

5. **Fiddler / Wireshark**
   - Network traffic inspection
   - Package download debugging

---

## Performance & Optimization

### Profiling Tools

1. **Visual Studio Profiler**
   - CPU profiling
   - Memory profiling
   - UI responsiveness

2. **PerfView**
   - ETW trace collection
   - Performance investigation

3. **dotMemory** (JetBrains)
   - Memory leak detection
   - Allocation tracking

### Optimization Strategies

1. **Async/Await**
   - Non-blocking operations
   - Responsive UI

2. **Object Pooling**
   - Reduce allocations
   - Reuse expensive objects

3. **Lazy Loading**
   - Load on demand
   - Reduce startup time

4. **Caching**
   - Memory cache for frequent data
   - Disk cache for large datasets

5. **Parallel Processing**
   - PLINQ for data processing
   - Parallel.ForEach for operations

---

## Security

### Security Libraries

**Windows Credential Manager**
- Store sensitive data securely
- System-level encryption

**Data Protection API (DPAPI)**
```csharp
using System.Security.Cryptography;

public string EncryptString(string plainText)
{
    var data = Encoding.UTF8.GetBytes(plainText);
    var encrypted = ProtectedData.Protect(data, null, DataProtectionScope.CurrentUser);
    return Convert.ToBase64String(encrypted);
}
```

### Code Signing

**SignTool**
- Sign executables and installers
- Verify code integrity
- Prevent tampering

---

## Documentation

### Code Documentation

**DocFX** or **XML Documentation Comments**
```csharp
/// <summary>
/// Loads a Windows image from the specified path.
/// </summary>
/// <param name="path">The path to the WIM file.</param>
/// <param name="ct">Cancellation token.</param>
/// <returns>The loaded Windows image.</returns>
/// <exception cref="ImageNotFoundException">Thrown when the image file is not found.</exception>
public async Task<WindowsImage> LoadImageAsync(string path, CancellationToken ct = default)
{
    // Implementation
}
```

### User Documentation

**Platform**: GitHub Pages or dedicated website
**Format**: Markdown, HTML
**Tools**:
- Jekyll or Hugo for static site generation
- MkDocs for documentation

---

## Third-Party Libraries Summary

### Essential NuGet Packages

```xml
<ItemGroup>
  <!-- UI Framework -->
  <PackageReference Include="Microsoft.WindowsAppSDK" Version="1.5.*" />
  <PackageReference Include="Microsoft.Windows.SDK.BuildTools" Version="10.0.*" />
  <PackageReference Include="CommunityToolkit.Mvvm" Version="8.2.*" />
  <PackageReference Include="CommunityToolkit.WinUI.UI.Controls" Version="7.1.*" />

  <!-- Infrastructure -->
  <PackageReference Include="Microsoft.Extensions.DependencyInjection" Version="8.0.*" />
  <PackageReference Include="Microsoft.Extensions.Configuration.Json" Version="8.0.*" />
  <PackageReference Include="Serilog.Extensions.Logging" Version="8.0.*" />

  <!-- Data -->
  <PackageReference Include="Microsoft.Data.Sqlite" Version="8.0.*" />

  <!-- Windows Integration -->
  <PackageReference Include="Microsoft.PowerShell.SDK" Version="7.4.*" />
  <PackageReference Include="Microsoft.Windows.CsWin32" Version="0.3.*" />

  <!-- Logging -->
  <PackageReference Include="Serilog" Version="3.1.*" />
  <PackageReference Include="Serilog.Sinks.Console" Version="5.0.*" />
  <PackageReference Include="Serilog.Sinks.File" Version="5.0.*" />

  <!-- Testing -->
  <PackageReference Include="xunit" Version="2.6.*" />
  <PackageReference Include="Moq" Version="4.20.*" />
  <PackageReference Include="FluentAssertions" Version="6.12.*" />
</ItemGroup>
```

---

## Version Requirements

### Minimum System Requirements

- **OS**: Windows 11 (Build 22000+)
- **Runtime**: .NET 8.0 Runtime
- **Memory**: 4 GB RAM
- **Disk**: 500 MB free space
- **Display**: 1280x720 resolution

### Recommended System Requirements

- **OS**: Windows 11 (Build 22621+)
- **Runtime**: .NET 8.0 Runtime
- **Memory**: 8 GB RAM
- **Disk**: 2 GB free space (more for image operations)
- **Display**: 1920x1080 resolution

### Development Requirements

- **OS**: Windows 11 (Build 22621+)
- **IDE**: Visual Studio 2022 (v17.8+)
- **SDK**: .NET 8.0 SDK
- **PowerShell**: 7.4+
- **Memory**: 16 GB RAM
- **Disk**: 50 GB free space

---

**Document Version**: 1.0
**Last Updated**: 2025-12-10
**Status**: Planning Phase
