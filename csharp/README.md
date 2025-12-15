# Better11 C# Frontend

This is the C# frontend for Better11, providing a command-line interface (CLI) for all Better11 functionality.

## Project Structure

```
csharp/
├── Better11.sln              # Visual Studio solution
├── Better11.Core/            # Core library with services and models
│   ├── Interfaces/           # Service interfaces
│   ├── Models/               # Data models
│   ├── Services/             # Service implementations
│   └── PowerShell/           # PowerShell integration
├── Better11.CLI/             # Command-line interface application
│   └── Commands/             # CLI command handlers
└── Better11.Tests/           # Unit tests
```

## Prerequisites

- .NET 8.0 SDK
- Windows 10/11 (for PowerShell integration)
- Administrator privileges (for some operations)

## Building

```bash
cd csharp
dotnet restore
dotnet build
```

## Running

```bash
# From the solution directory
dotnet run --project Better11.CLI -- --help

# Or build and run the executable
dotnet publish Better11.CLI -c Release -o publish
./publish/better11 --help
```

## CLI Commands

### Application Management

```bash
# List available applications
better11 apps list

# Download an application
better11 apps download <app-id>

# Install an application
better11 apps install <app-id>

# Uninstall an application
better11 apps uninstall <app-id>

# Check installation status
better11 apps status [app-id]
```

### System Tools

```bash
# List startup items
better11 system startup list

# Disable a startup item
better11 system startup disable <name>

# Analyze disk space
better11 system disk analyze [-d <drive>]

# Cleanup temporary files
better11 system disk cleanup [-a <days>]
```

### Privacy Settings

```bash
# Show privacy status
better11 privacy status

# Get/set telemetry level
better11 privacy telemetry get
better11 privacy telemetry set <level>

# Enable/disable Cortana
better11 privacy cortana enable
better11 privacy cortana disable

# Apply recommended privacy settings
better11 privacy apply-recommended
```

### Network Management

```bash
# List network adapters
better11 network list

# Flush DNS cache
better11 network flush-dns

# Reset TCP/IP or Winsock
better11 network reset tcpip
better11 network reset winsock

# Set DNS servers
better11 network dns set <adapter> -p google|cloudflare|quad9|opendns
better11 network dns set <adapter> --primary 1.1.1.1 --secondary 1.0.0.1

# Test connectivity
better11 network test [-h <host>]
```

### Power Management

```bash
# List power plans
better11 power list

# Set active power plan
better11 power set <name>

# Enable/disable hibernation
better11 power hibernate enable
better11 power hibernate disable

# Generate battery report
better11 power battery-report [-o <output>]
```

### Backup & Restore

```bash
# List restore points
better11 backup restore-points list

# Create restore point
better11 backup restore-points create <description>

# Export settings
better11 backup export <output-file>

# Import settings
better11 backup import <input-file>
```

### Deployment

```bash
# Generate Windows unattend file
better11 deploy unattend \
  --product-key XXXXX-XXXXX-XXXXX-XXXXX-XXXXX \
  --output unattend.xml \
  --admin-user Administrator \
  --admin-password SecretPassword \
  --auto-logon

# Use templates
better11 deploy unattend \
  --template workstation \
  --product-key XXXXX-XXXXX-XXXXX-XXXXX-XXXXX \
  --output unattend.xml

better11 deploy unattend \
  --template lab \
  --product-key XXXXX-XXXXX-XXXXX-XXXXX-XXXXX \
  --output unattend.xml
```

## Testing

```bash
cd csharp
dotnet test
```

## Architecture

The C# frontend is built with:

- **System.CommandLine** - Modern CLI framework with auto-generated help
- **Spectre.Console** - Rich terminal output with tables and progress indicators
- **Microsoft.Extensions.Hosting** - Dependency injection and logging
- **PowerShell SDK** - Integration with existing PowerShell modules

### Core Services

| Service | Description |
|---------|-------------|
| `IAppService` | Application catalog and installation management |
| `IDiskService` | Disk space analysis and cleanup |
| `INetworkService` | Network adapter and DNS management |
| `IPowerService` | Power plans and hibernation |
| `IPrivacyService` | Privacy and telemetry settings |
| `IStartupService` | Startup program management |
| `IBackupService` | Restore points and settings backup |
| `IUnattendService` | Windows unattend file generation |

## Migration from Python

The previous Python frontend (cli.py, gui.py, tui.py) has been replaced by this C# implementation. The Python backend modules (apps, system_tools, unattend) remain available for direct use.

Key improvements:
- Native Windows integration via PowerShell SDK
- Modern CLI with auto-completion and rich help
- Better performance with ahead-of-time compilation
- Single executable deployment option
