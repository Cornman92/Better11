# Better11 C# CLI Guide

**Version**: 0.3.0  
**Platform**: .NET 8.0  
**Status**: Active

---

## Overview

The Better11 C# CLI provides a modern, cross-platform command-line interface for managing Windows 11 enhancements. It replaces the Python CLI with improved performance and native Windows integration.

## Installation

### Prerequisites

- .NET 8.0 SDK or later
- Windows 11 (build 22621/22H2 or newer)
- PowerShell 5.1+ or PowerShell 7
- Administrator privileges for system modifications

### Building from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/better11.git
cd better11/csharp

# Restore dependencies
dotnet restore

# Build the CLI
dotnet build Better11.CLI

# Run the CLI
dotnet run --project Better11.CLI -- --help
```

### Publishing a Standalone Executable

```bash
# Windows x64
dotnet publish Better11.CLI -c Release -r win-x64 --self-contained

# The executable will be in: Better11.CLI/bin/Release/net8.0/win-x64/publish/Better11.CLI.exe
```

---

## Usage

### Basic Syntax

```bash
better11 <command> <subcommand> [options]
```

Or when running from source:

```bash
dotnet run --project Better11.CLI -- <command> <subcommand> [options]
```

---

## Commands

### Application Management

#### List Applications

```bash
# List all available applications
better11 app list
```

Output displays:
- App ID
- Name
- Version
- Type (MSI, EXE, APPX)
- Status (Installed/Available)

#### Install Application

```bash
# Install an application
better11 app install <app-id>

# Install with forced confirmation
better11 app install <app-id> --force

# Examples
better11 app install vscode
better11 app install chrome --force
```

#### Uninstall Application

```bash
# Uninstall an application
better11 app uninstall <app-id>

# Force uninstall
better11 app uninstall <app-id> --force
```

#### Application Status

```bash
# Show status of all installed applications
better11 app status

# Show status of specific application
better11 app status <app-id>
```

---

### System Tools

#### Disk Management

```bash
# Show disk space information for all drives
better11 system disk
```

Displays:
- Drive letter
- Label
- Total space (GB)
- Used space (GB)
- Free space (GB)
- Usage percentage (color-coded)

#### Cleanup Temporary Files

```bash
# Clean files older than 7 days (default)
better11 system cleanup

# Clean files older than 30 days
better11 system cleanup --days 30
```

#### Create Restore Point

```bash
# Create a system restore point
better11 system restore-point "Before Better11 changes"
```

---

### Privacy Settings

#### Telemetry Management

```bash
# Get current telemetry level
better11 privacy telemetry get

# Set telemetry level
better11 privacy telemetry set Security
better11 privacy telemetry set Basic
better11 privacy telemetry set Enhanced
better11 privacy telemetry set Full
```

Available telemetry levels:
- **Security**: Minimal data collection
- **Basic**: Basic diagnostic data
- **Enhanced**: Enhanced diagnostic data
- **Full**: Full diagnostic and usage data

#### Cortana Management

```bash
# Disable Cortana
better11 privacy cortana disable
```

---

### Startup Programs

#### List Startup Items

```bash
# List all startup programs
better11 startup list
```

Displays:
- Program name
- Command
- Location (Registry/StartupFolder/TaskScheduler)
- Status (Enabled/Disabled)

#### Disable Startup Item

```bash
# Disable a startup program
better11 startup disable "Program Name"
```

#### Enable Startup Item

```bash
# Enable a startup program
better11 startup enable "Program Name"
```

---

## Examples

### Complete Workflow Example

```bash
# 1. Check disk space
better11 system disk

# 2. Clean temporary files
better11 system cleanup --days 7

# 3. Create restore point
better11 system restore-point "Before installing apps"

# 4. List available applications
better11 app list

# 5. Install applications
better11 app install vscode --force
better11 app install chrome --force

# 6. Set privacy settings
better11 privacy telemetry set Security
better11 privacy cortana disable

# 7. Manage startup programs
better11 startup list
better11 startup disable "Unnecessary Program"

# 8. Check installed applications
better11 app status
```

### Batch Operations

```powershell
# Install multiple applications
$apps = @("vscode", "chrome", "firefox")
foreach ($app in $apps) {
    better11 app install $app --force
}

# Disable multiple startup programs
$startupItems = @("Program1", "Program2", "Program3")
foreach ($item in $startupItems) {
    better11 startup disable $item
}
```

---

## Output Formatting

The CLI uses Spectre.Console for rich terminal output:

- **Tables**: Structured data display with columns and borders
- **Status Indicators**: Spinning indicators during long operations
- **Color Coding**: 
  - Green: Success, healthy state
  - Yellow: Warnings, available items
  - Red: Errors, critical state
- **Progress Bars**: Visual progress for operations
- **Panels**: Grouped information display

---

## Error Handling

The CLI provides clear error messages with context:

```bash
# Application not found
❌ Error: Application 'invalid-app' not found

# Permission denied
❌ Error: Administrator privileges required for this operation

# PowerShell module error
❌ Error: Failed to execute PowerShell command: Get-Better11Apps
```

---

## Advanced Usage

### Running with Elevated Privileges

Many operations require administrator privileges:

```powershell
# Windows Terminal (Admin)
better11 app install vscode

# Or explicitly run as admin
Start-Process better11 -ArgumentList "app install vscode" -Verb RunAs
```

### Logging and Debugging

```bash
# Set logging level via environment variable
$env:DOTNET_LOGGING__LOGLEVEL__DEFAULT="Debug"
better11 app list
```

---

## Comparison with Python CLI

| Feature | Python CLI | C# CLI |
|---------|-----------|--------|
| Performance | Good | Excellent |
| Startup Time | ~1-2s | ~0.5s |
| Memory Usage | ~50MB | ~30MB |
| Output Format | Basic | Rich (Spectre.Console) |
| Error Messages | Basic | Detailed with context |
| PowerShell Integration | subprocess | Native .NET integration |
| Cross-platform | Yes | Windows-focused |

---

## Troubleshooting

### CLI Not Found

```bash
# If running from source
cd /workspace/csharp
dotnet run --project Better11.CLI -- --help

# If using published executable, add to PATH
$env:PATH += ";C:\path\to\better11\publish"
```

### PowerShell Module Not Loaded

Ensure PowerShell modules are in the correct location:

```powershell
# Check module path
$modulePath = "C:\workspace\powershell\Better11\Better11.psd1"
Test-Path $modulePath

# Import manually if needed
Import-Module $modulePath
```

### .NET Runtime Missing

Install .NET 8.0 Runtime or SDK:

```powershell
# Check .NET version
dotnet --version

# Install .NET 8.0 if needed
winget install Microsoft.DotNet.SDK.8
```

---

## Development

### Adding New Commands

1. Create a new command class in `Better11.CLI/Commands/`
2. Implement command structure using System.CommandLine
3. Register in `Program.cs`
4. Build and test

Example:

```csharp
public class NetworkCommands
{
    private readonly IServiceProvider _services;

    public NetworkCommands(IServiceProvider services)
    {
        _services = services;
    }

    public Command CreateCommand()
    {
        var networkCommand = new Command("network", "Network tools");
        
        var flushDnsCommand = new Command("flush-dns", "Flush DNS cache");
        flushDnsCommand.SetHandler(async () => await FlushDnsAsync());
        networkCommand.AddCommand(flushDnsCommand);

        return networkCommand;
    }

    private async Task FlushDnsAsync()
    {
        var networkService = _services.GetRequiredService<INetworkService>();
        // Implementation...
    }
}
```

### Running Tests

```bash
cd csharp
dotnet test
```

---

## Resources

- [.NET CLI Documentation](https://docs.microsoft.com/en-us/dotnet/core/tools/)
- [System.CommandLine](https://github.com/dotnet/command-line-api)
- [Spectre.Console](https://spectreconsole.net/)
- [Better11 API Reference](API_REFERENCE.md)

---

## Support

For issues or questions:
- GitHub Issues: https://github.com/yourusername/better11/issues
- Documentation: /workspace/docs/

---

*Last Updated: December 14, 2025*
