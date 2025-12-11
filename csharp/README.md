# Better11 C# Frontend & WinUI 3 GUI

Modern C# frontend and WinUI 3 graphical interface for Better11.

## 🏗️ Architecture

The C# frontend consists of three main projects:

- **Better11.Core**: Core library with models, services, and PowerShell integration
- **Better11.WinUI**: WinUI 3 GUI application with MVVM architecture
- **Better11.Tests**: Unit and integration tests

## 🚀 Getting Started

### Prerequisites

- Visual Studio 2022 (17.8 or higher) with:
  - .NET 8.0 SDK
  - Windows App SDK
  - WinUI 3 tools
- Windows 11 SDK (10.0.22621.0)

### Building the Solution

```bash
# Open solution in Visual Studio
start Better11.sln

# Or build from command line
dotnet build Better11.sln

# Run the WinUI app
dotnet run --project Better11.WinUI\Better11.WinUI.csproj
```

## 📁 Project Structure

### Better11.Core

Core library providing services and PowerShell integration:

```
Better11.Core/
├── Models/             # Data models (AppMetadata, AppStatus, etc.)
├── Interfaces/         # Service interfaces (IAppManager, etc.)
├── Services/           # Service implementations
├── PowerShell/         # PowerShell executor
└── Utilities/          # Helper classes
```

### Better11.WinUI

WinUI 3 GUI with MVVM pattern:

```
Better11.WinUI/
├── Views/              # XAML pages
│   ├── MainWindow.xaml
│   ├── ApplicationsPage.xaml
│   ├── SystemToolsPage.xaml
│   └── SettingsPage.xaml
├── ViewModels/         # View models
│   ├── MainViewModel.cs
│   ├── ApplicationsViewModel.cs
│   ├── SystemToolsViewModel.cs
│   └── SettingsViewModel.cs
├── Controls/           # Custom controls
├── Converters/         # Value converters
└── Assets/             # Images and resources
```

## 🎨 WinUI 3 Features

- **Modern UI**: Fluent Design with Windows 11 styling
- **MVVM Architecture**: Clean separation of concerns
- **Dependency Injection**: Built-in DI with Microsoft.Extensions
- **Async/Await**: Responsive UI with async operations
- **Navigation**: Multi-page navigation with NavigationView
- **Data Binding**: Two-way binding with MVVM Toolkit

## 🔌 PowerShell Integration

The C# frontend communicates with the PowerShell backend using the `PowerShellExecutor` class:

```csharp
// Example: Using AppManagerService
public class ApplicationsViewModel
{
    private readonly IAppManager _appManager;
    
    public async Task LoadAppsAsync()
    {
        var apps = await _appManager.ListAvailableAppsAsync();
        // Update UI
    }
    
    public async Task InstallAppAsync(string appId)
    {
        var result = await _appManager.InstallAppAsync(appId);
        // Handle result
    }
}
```

## 📦 NuGet Packages

### Better11.Core
- System.Management.Automation (PowerShell integration)
- Microsoft.Extensions.Logging
- System.Text.Json

### Better11.WinUI
- Microsoft.WindowsAppSDK
- CommunityToolkit.Mvvm
- CommunityToolkit.WinUI.UI.Controls
- Microsoft.Extensions.Hosting

## 🧪 Testing

```bash
# Run all tests
dotnet test

# Run with coverage
dotnet test --collect:"XPlat Code Coverage"
```

## 🚢 Deployment

### MSIX Package (Microsoft Store)

```bash
# Build MSIX package
msbuild Better11.WinUI\Better11.WinUI.csproj /t:Publish /p:Configuration=Release
```

### Standalone Installer

Build as self-contained deployment:

```bash
dotnet publish Better11.WinUI -c Release -r win-x64 --self-contained
```

## 📖 Documentation

- [API Reference](../API_REFERENCE.md)
- [Migration Plan](../MIGRATION_PLAN_POWERSHELL_CSHARP_WINUI3.md)
- [WinUI 3 Documentation](https://docs.microsoft.com/windows/apps/winui/winui3/)

## 🤝 Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for development guidelines.

## 📝 License

MIT License - See [LICENSE](../LICENSE) file for details.
