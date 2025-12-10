# Better11 Technical Architecture

## Overview

Better11 follows a clean, layered architecture using MVVM (Model-View-ViewModel) pattern with WinUI3. The application is designed to be modular, testable, and maintainable while providing high performance and excellent user experience.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Presentation Layer                       │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │   Views    │  │  Controls  │  │   Themes   │            │
│  │  (XAML)    │  │  (WinUI3)  │  │   (CSS)    │            │
│  └────────────┘  └────────────┘  └────────────┘            │
└─────────────────────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   ViewModel Layer                            │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │ ViewModels │  │  Commands  │  │ Converters │            │
│  │   (MVVM)   │  │ (ICommand) │  │  (Value)   │            │
│  └────────────┘  └────────────┘  └────────────┘            │
└─────────────────────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Service Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │    Image     │  │     App      │  │     File     │      │
│  │   Service    │  │   Service    │  │   Service    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Deploy     │  │   System     │  │   Backup     │      │
│  │   Service    │  │   Service    │  │   Service    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Core Layer                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Windows    │  │  PowerShell  │  │   Package    │      │
│  │     API      │  │   Engine     │  │   Manager    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │     File     │  │   Registry   │  │     WIM      │      │
│  │   System     │  │   Manager    │  │   Manager    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                Infrastructure Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Logging    │  │   Config     │  │     Data     │      │
│  │  (Serilog)   │  │   Manager    │  │   Storage    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │     DI       │  │   Caching    │  │   Security   │      │
│  │  Container   │  │   Service    │  │   Service    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```
Better11/
├── src/
│   ├── Better11.App/                    # WinUI3 Application
│   │   ├── Views/                       # XAML Views
│   │   ├── ViewModels/                  # ViewModels
│   │   ├── Controls/                    # Custom Controls
│   │   ├── Converters/                  # Value Converters
│   │   ├── Themes/                      # Application Themes
│   │   ├── Assets/                      # Images, Icons, etc.
│   │   └── App.xaml.cs                  # Application Entry Point
│   │
│   ├── Better11.Core/                   # Core Business Logic
│   │   ├── Interfaces/                  # Core Interfaces
│   │   ├── Models/                      # Domain Models
│   │   ├── Enums/                       # Enumerations
│   │   ├── Exceptions/                  # Custom Exceptions
│   │   └── Constants/                   # Application Constants
│   │
│   ├── Better11.Services/               # Service Implementations
│   │   ├── ImageService/                # Windows Image Management
│   │   ├── AppService/                  # Application Management
│   │   ├── FileService/                 # File Operations
│   │   ├── DeployService/               # Deployment Services
│   │   ├── SystemService/               # System Optimization
│   │   ├── BackupService/               # Backup & Restore
│   │   └── PluginService/               # Plugin Management
│   │
│   ├── Better11.Infrastructure/         # Cross-cutting Concerns
│   │   ├── Logging/                     # Logging Implementation
│   │   ├── Configuration/               # Configuration Management
│   │   ├── Data/                        # Data Access
│   │   ├── Security/                    # Security Services
│   │   ├── DependencyInjection/         # DI Setup
│   │   └── Caching/                     # Caching Services
│   │
│   ├── Better11.PowerShell/             # PowerShell Integration
│   │   ├── Cmdlets/                     # PowerShell Cmdlets
│   │   ├── Scripts/                     # Reusable Scripts
│   │   └── Modules/                     # PowerShell Modules
│   │
│   ├── Better11.CLI/                    # Command Line Interface
│   │   ├── Commands/                    # CLI Commands
│   │   └── Program.cs                   # CLI Entry Point
│   │
│   └── Better11.Plugin.SDK/             # Plugin Development Kit
│       ├── Interfaces/                  # Plugin Interfaces
│       ├── Base/                        # Base Plugin Classes
│       └── Helpers/                     # Helper Utilities
│
├── tests/
│   ├── Better11.UnitTests/              # Unit Tests
│   ├── Better11.IntegrationTests/       # Integration Tests
│   └── Better11.E2ETests/               # End-to-End Tests
│
├── docs/
│   ├── user-guide/                      # User Documentation
│   ├── developer-guide/                 # Developer Documentation
│   └── api/                             # API Documentation
│
├── scripts/                             # Build and Deployment Scripts
├── samples/                             # Sample Plugins and Scripts
└── tools/                               # Development Tools
```

## Layer Details

### 1. Presentation Layer (Better11.App)

**Responsibilities:**
- User interface rendering
- User input handling
- Visual state management
- Navigation

**Key Components:**

#### Views
- `MainWindow.xaml` - Main application window
- `DashboardView.xaml` - Dashboard overview
- `ImageEditorView.xaml` - Windows image editing
- `AppManagerView.xaml` - Application management
- `FileOperationsView.xaml` - File operations
- `SystemOptimizerView.xaml` - System optimization
- `SettingsView.xaml` - Application settings

#### ViewModels
- Follow MVVM pattern
- Implement `INotifyPropertyChanged`
- Use `RelayCommand` or `AsyncRelayCommand`
- Handle navigation through navigation service
- Communicate with services through dependency injection

**Example ViewModel:**
```csharp
public class ImageEditorViewModel : ViewModelBase
{
    private readonly IImageService _imageService;
    private readonly IDialogService _dialogService;

    public ImageEditorViewModel(IImageService imageService, IDialogService dialogService)
    {
        _imageService = imageService;
        _dialogService = dialogService;

        LoadImageCommand = new AsyncRelayCommand(LoadImageAsync);
        MountImageCommand = new AsyncRelayCommand(MountImageAsync, CanMountImage);
    }

    public IAsyncRelayCommand LoadImageCommand { get; }
    public IAsyncRelayCommand MountImageCommand { get; }

    private async Task LoadImageAsync()
    {
        // Implementation
    }
}
```

### 2. ViewModel Layer

**Responsibilities:**
- Expose data and commands to views
- Handle user interactions
- Coordinate between views and services
- Manage view state

**Patterns Used:**
- **Command Pattern**: For user actions
- **Observer Pattern**: For property changes
- **Messenger Pattern**: For loose coupling between ViewModels

**Base Classes:**
```csharp
public abstract class ViewModelBase : INotifyPropertyChanged
{
    protected INavigationService NavigationService { get; }
    protected IMessenger Messenger { get; }

    protected virtual Task OnNavigatedToAsync(object parameter) => Task.CompletedTask;
    protected virtual Task OnNavigatedFromAsync() => Task.CompletedTask;
}
```

### 3. Service Layer (Better11.Services)

**Responsibilities:**
- Business logic implementation
- Data orchestration
- External system integration
- Transaction management

**Key Services:**

#### ImageService
```csharp
public interface IImageService
{
    Task<WindowsImage> LoadImageAsync(string path, CancellationToken ct = default);
    Task MountImageAsync(WindowsImage image, string mountPath, CancellationToken ct = default);
    Task UnmountImageAsync(string mountPath, bool commit, CancellationToken ct = default);
    Task<IEnumerable<Driver>> GetDriversAsync(WindowsImage image, CancellationToken ct = default);
    Task AddDriverAsync(WindowsImage image, string driverPath, CancellationToken ct = default);
    Task<IEnumerable<WindowsFeature>> GetFeaturesAsync(WindowsImage image, CancellationToken ct = default);
    Task EnableFeatureAsync(WindowsImage image, string featureName, CancellationToken ct = default);
}
```

#### AppService
```csharp
public interface IAppService
{
    Task<IEnumerable<AppPackage>> SearchAppsAsync(string query, CancellationToken ct = default);
    Task<AppPackage> GetAppDetailsAsync(string packageId, CancellationToken ct = default);
    Task<bool> InstallAppAsync(AppPackage package, InstallOptions options, IProgress<InstallProgress> progress, CancellationToken ct = default);
    Task<bool> UninstallAppAsync(string packageId, CancellationToken ct = default);
    Task<IEnumerable<InstalledApp>> GetInstalledAppsAsync(CancellationToken ct = default);
    Task<IEnumerable<AppUpdate>> CheckUpdatesAsync(CancellationToken ct = default);
}
```

#### FileService
```csharp
public interface IFileService
{
    Task<IEnumerable<DuplicateFileGroup>> FindDuplicatesAsync(string path, DuplicateSearchOptions options, CancellationToken ct = default);
    Task<IEnumerable<FileItem>> SearchFilesAsync(FileSearchCriteria criteria, CancellationToken ct = default);
    Task OrganizeFilesAsync(string path, OrganizationRule[] rules, CancellationToken ct = default);
    Task<FileOperationResult> BulkOperationAsync(FileOperation operation, CancellationToken ct = default);
}
```

### 4. Core Layer (Better11.Core)

**Responsibilities:**
- Low-level Windows API interaction
- PowerShell execution
- Package management
- Registry operations
- WIM file handling

**Key Components:**

#### Windows API Wrapper
```csharp
public interface IWindowsApiService
{
    Task<ProcessResult> RunElevatedAsync(string command, string arguments);
    Task<RegistryValue> ReadRegistryAsync(string hive, string key, string value);
    Task WriteRegistryAsync(string hive, string key, string value, object data);
    Task<ServiceInfo> GetServiceInfoAsync(string serviceName);
}
```

#### PowerShell Engine
```csharp
public interface IPowerShellEngine
{
    Task<PowerShellResult> ExecuteScriptAsync(string script, CancellationToken ct = default);
    Task<PowerShellResult> ExecuteCommandAsync(string command, Dictionary<string, object> parameters, CancellationToken ct = default);
    Task<T> ExecuteScriptAsync<T>(string script, CancellationToken ct = default);
}
```

#### WIM Manager
```csharp
public interface IWimManager
{
    Task<WimInfo> GetWimInfoAsync(string wimPath);
    Task<IEnumerable<WimImageInfo>> GetImagesAsync(string wimPath);
    Task MountWimAsync(string wimPath, int imageIndex, string mountPath, bool readOnly = false);
    Task UnmountWimAsync(string mountPath, bool commit = false);
    Task<bool> CommitWimAsync(string mountPath);
}
```

### 5. Infrastructure Layer (Better11.Infrastructure)

**Responsibilities:**
- Logging
- Configuration
- Data persistence
- Caching
- Security
- Dependency injection setup

**Key Components:**

#### Logging Configuration
```csharp
public static class LoggingConfiguration
{
    public static void ConfigureLogging(IServiceCollection services)
    {
        Log.Logger = new LoggerConfiguration()
            .MinimumLevel.Debug()
            .WriteTo.File("logs/better11-.log", rollingInterval: RollingInterval.Day)
            .WriteTo.Console()
            .CreateLogger();

        services.AddLogging(builder => builder.AddSerilog());
    }
}
```

#### Data Storage
```csharp
public interface IDataStore
{
    Task<T> GetAsync<T>(string key) where T : class;
    Task SetAsync<T>(string key, T value) where T : class;
    Task DeleteAsync(string key);
    Task<IEnumerable<T>> QueryAsync<T>(Expression<Func<T, bool>> predicate) where T : class;
}
```

#### Security Service
```csharp
public interface ISecurityService
{
    Task<bool> IsAdministratorAsync();
    Task<bool> RequestElevationAsync();
    string EncryptString(string plainText);
    string DecryptString(string cipherText);
    Task<bool> ValidateIntegrityAsync(string filePath);
}
```

## Design Patterns

### 1. MVVM (Model-View-ViewModel)
- **Views**: XAML UI components
- **ViewModels**: Presentation logic and state
- **Models**: Business entities

### 2. Dependency Injection
- Constructor injection throughout the application
- Service registration in `ServiceConfiguration.cs`
- Scoped, transient, and singleton lifetimes

### 3. Repository Pattern
- Abstraction over data access
- Supports multiple data sources
- Enables unit testing

### 4. Factory Pattern
- Service factories for complex object creation
- Plugin factories for dynamic loading

### 5. Strategy Pattern
- Different installation strategies (winget, chocolatey, custom)
- File organization strategies
- Backup strategies

### 6. Observer Pattern
- Property change notifications
- Event aggregation with messenger

### 7. Command Pattern
- All user actions as commands
- Supports undo/redo
- Command validation

## Data Flow

### Example: Installing an Application

```
User clicks "Install" button
    ↓
AppManagerViewModel.InstallCommand executes
    ↓
ViewModel calls IAppService.InstallAppAsync()
    ↓
AppService determines package source (winget/chocolatey)
    ↓
Appropriate IPackageProvider is selected via Strategy Pattern
    ↓
PackageProvider downloads and installs application
    ↓
Progress updates sent back through IProgress<T>
    ↓
ViewModel updates UI properties
    ↓
View reflects changes through data binding
    ↓
Success/failure logged via ILogger
    ↓
Activity recorded in IDataStore
```

## Threading Model

### UI Thread
- All WinUI3 UI updates
- ViewModel property changes
- Command execution initiation

### Background Threads
- All service operations
- File I/O
- Network operations
- PowerShell execution
- Image manipulation

### Synchronization
```csharp
// Ensure UI updates happen on UI thread
await DispatcherQueue.EnqueueAsync(() =>
{
    StatusMessage = "Operation completed";
});

// Long-running operations with cancellation
public async Task LongRunningOperationAsync(CancellationToken ct)
{
    await Task.Run(async () =>
    {
        // Work with cancellation support
        ct.ThrowIfCancellationRequested();
    }, ct);
}
```

## Error Handling Strategy

### Exception Hierarchy
```
Better11Exception (base)
├── ImageException
│   ├── ImageNotFoundException
│   ├── ImageMountException
│   └── ImageCorruptedException
├── AppException
│   ├── AppInstallException
│   ├── AppNotFoundException
│   └── DependencyException
├── FileException
│   ├── AccessDeniedException
│   └── FileOperationException
└── DeployException
    ├── NetworkException
    └── ProvisionException
```

### Error Handling Pattern
```csharp
public async Task<Result<T>> OperationAsync()
{
    try
    {
        // Operation logic
        return Result<T>.Success(data);
    }
    catch (Better11Exception ex)
    {
        _logger.LogError(ex, "Operation failed");
        return Result<T>.Failure(ex.Message);
    }
    catch (Exception ex)
    {
        _logger.LogCritical(ex, "Unexpected error");
        return Result<T>.Failure("An unexpected error occurred");
    }
}
```

## Configuration Management

### Configuration Sources (Priority Order)
1. Command-line arguments
2. Environment variables
3. User settings file (`appsettings.user.json`)
4. Application settings file (`appsettings.json`)
5. Default values

### Configuration Structure
```json
{
  "App": {
    "Theme": "Dark",
    "Language": "en-US",
    "CheckUpdates": true
  },
  "Paths": {
    "Downloads": "%USERPROFILE%\\Downloads\\Better11",
    "Temp": "%TEMP%\\Better11",
    "Logs": "%APPDATA%\\Better11\\Logs"
  },
  "ImageEditor": {
    "DefaultMountPath": "C:\\Better11\\Mount",
    "AutoCommit": false,
    "MaxConcurrentMounts": 3
  },
  "AppManager": {
    "PreferredSource": "winget",
    "AutoUpdate": false,
    "ParallelDownloads": 3
  }
}
```

## Security Considerations

### 1. Elevation
- Detect required elevation
- Request UAC elevation when needed
- Operate with least privilege

### 2. Credential Management
- Use Windows Credential Manager
- Never store credentials in plain text
- Encrypt sensitive configuration data

### 3. Code Signing
- Sign all executables
- Verify downloaded packages
- Validate PowerShell scripts

### 4. Input Validation
- Sanitize all user inputs
- Validate file paths
- Prevent command injection

### 5. Secure Communication
- HTTPS for all network requests
- Certificate validation
- TLS 1.2+

## Performance Optimization

### 1. Lazy Loading
- Load heavy components on-demand
- Virtual scrolling for large lists
- Deferred initialization

### 2. Caching
- Cache expensive queries
- In-memory cache for frequent data
- Disk cache for large datasets

### 3. Async/Await
- Non-blocking operations
- Parallel operations where possible
- Cancellation token support

### 4. Resource Management
- Proper disposal of resources
- Connection pooling
- Memory-mapped files for large files

## Testing Strategy

### Unit Tests
- Test ViewModels in isolation
- Mock service dependencies
- Test business logic

### Integration Tests
- Test service integration
- Test data access
- Test Windows API interaction

### E2E Tests
- Test complete workflows
- UI automation tests
- Performance tests

## Extensibility

### Plugin System

```csharp
public interface IPlugin
{
    string Name { get; }
    string Version { get; }
    string Description { get; }

    Task InitializeAsync(IPluginContext context);
    Task<PluginResult> ExecuteAsync(PluginParameters parameters);
    Task ShutdownAsync();
}

public interface IPluginContext
{
    IServiceProvider Services { get; }
    ILogger Logger { get; }
    IConfiguration Configuration { get; }
    string PluginDirectory { get; }
}
```

### Plugin Discovery
- Scan plugin directories
- Load assemblies dynamically
- Validate plugin compatibility
- Dependency resolution

## Deployment

### Application Packaging
- MSIX package for Microsoft Store
- Traditional installer for direct download
- Portable version (xcopy deployment)

### Update Mechanism
- Check for updates on startup (optional)
- Download updates in background
- Apply updates on next launch
- Rollback capability

---

**Document Version**: 1.0
**Last Updated**: 2025-12-10
**Status**: Planning Phase
