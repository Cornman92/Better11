# Better11 Source Code

This directory will contain all source code for the Better11 application.

## Planned Structure

```
src/
├── Better11.App/                    # WinUI3 Application
│   ├── Views/                       # XAML Views
│   ├── ViewModels/                  # ViewModels
│   ├── Controls/                    # Custom Controls
│   ├── Converters/                  # Value Converters
│   ├── Themes/                      # Application Themes
│   ├── Assets/                      # Images, Icons, etc.
│   └── App.xaml.cs                  # Application Entry Point
│
├── Better11.Core/                   # Core Business Logic
│   ├── Interfaces/                  # Core Interfaces
│   ├── Models/                      # Domain Models
│   ├── Enums/                       # Enumerations
│   ├── Exceptions/                  # Custom Exceptions
│   └── Constants/                   # Application Constants
│
├── Better11.Services/               # Service Implementations
│   ├── ImageService/                # Windows Image Management
│   ├── AppService/                  # Application Management
│   ├── FileService/                 # File Operations
│   ├── DeployService/               # Deployment Services
│   ├── SystemService/               # System Optimization
│   ├── BackupService/               # Backup & Restore
│   └── PluginService/               # Plugin Management
│
├── Better11.Infrastructure/         # Cross-cutting Concerns
│   ├── Logging/                     # Logging Implementation
│   ├── Configuration/               # Configuration Management
│   ├── Data/                        # Data Access
│   ├── Security/                    # Security Services
│   ├── DependencyInjection/         # DI Setup
│   └── Caching/                     # Caching Services
│
├── Better11.PowerShell/             # PowerShell Integration
│   ├── Cmdlets/                     # PowerShell Cmdlets
│   ├── Scripts/                     # Reusable Scripts
│   └── Modules/                     # PowerShell Modules
│
├── Better11.CLI/                    # Command Line Interface
│   ├── Commands/                    # CLI Commands
│   └── Program.cs                   # CLI Entry Point
│
└── Better11.Plugin.SDK/             # Plugin Development Kit
    ├── Interfaces/                  # Plugin Interfaces
    ├── Base/                        # Base Plugin Classes
    └── Helpers/                     # Helper Utilities
```

## Getting Started

### Prerequisites
- Visual Studio 2022 (v17.8+)
- .NET 8.0 SDK
- Windows 11 SDK (10.0.22621.0+)

### Building
```bash
# Restore dependencies
dotnet restore

# Build solution
dotnet build

# Run application
dotnet run --project Better11.App
```

## Architecture

Better11 follows a clean, layered architecture:
- **Presentation Layer**: WinUI3 views and ViewModels (MVVM)
- **Service Layer**: Business logic and orchestration
- **Core Layer**: Domain models and business entities
- **Infrastructure Layer**: Cross-cutting concerns (logging, data access, etc.)

See [ARCHITECTURE.md](../ARCHITECTURE.md) for detailed information.

## Development Guidelines

See [CONTRIBUTING.md](../CONTRIBUTING.md) for:
- Coding standards
- Naming conventions
- Testing requirements
- Pull request process

---

**Status**: Planning Phase - Source code coming soon!
**Last Updated**: 2025-12-10
