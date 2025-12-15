# Migration Plan: Python Frontend to C# Frontend

## Overview
This document outlines the comprehensive plan to migrate Better11 from Python frontend to C# frontend while maintaining all existing functionality.

## Current State Analysis

### Python Frontend Components
1. **CLI** (`better11/cli.py`) - Command-line interface with subcommands:
   - `list` - List available applications
   - `download` - Download application
   - `install` - Install application
   - `uninstall` - Uninstall application
   - `status` - Show installation status
   - `deploy unattend` - Generate Windows unattend.xml

2. **GUI** (`better11/gui.py`) - Tkinter-based graphical interface

3. **TUI** (`better11/tui.py`) - Textual-based terminal UI

4. **Application Management** (`better11/apps/`):
   - `catalog.py` - Catalog loading and management
   - `download.py` - Download functionality
   - `manager.py` - Main app manager with dependency resolution
   - `models.py` - Data models (AppMetadata, AppStatus, InstallerType)
   - `runner.py` - Installer execution (MSI, EXE, APPX)
   - `state_store.py` - Installation state tracking
   - `verification.py` - Hash and signature verification
   - `code_signing.py` - Authenticode signature verification

5. **Unattend** (`better11/unattend.py`) - Windows unattend.xml generation

6. **Configuration** (`better11/config.py`) - Configuration management

7. **Interfaces** (`better11/interfaces.py`) - Common interfaces

### C# Backend Components (Already Exist)
- `Better11.Core` - Core services (Disk, Power, Network)
- PowerShell modules for system operations

## Migration Strategy

### Phase 1: Create C# Projects Structure
1. Create `Better11.CLI` project (Console Application)
2. Create `Better11.GUI` project (WPF Application for Windows)
3. Update solution file with new projects

### Phase 2: Migrate Core Application Management
1. Create `Better11.Core.Apps` namespace with:
   - `AppCatalog` - Catalog loading from JSON
   - `AppDownloader` - HTTP/local file download
   - `AppManager` - Main application manager
   - `InstallerRunner` - Execute installers
   - `DownloadVerifier` - Hash and signature verification
   - `CodeSigningVerifier` - Authenticode verification
   - `InstallationStateStore` - State persistence

2. Create models:
   - `AppMetadata`
   - `AppStatus`
   - `InstallerType` (enum)
   - `InstallerResult`
   - `SignatureInfo`, `CertificateInfo`, `SignatureStatus`

### Phase 3: Migrate CLI
1. Use `System.CommandLine` for command parsing
2. Implement all CLI commands:
   - List, download, install, uninstall, status
   - Deploy unattend command

### Phase 4: Migrate Unattend Generation
1. Create `Better11.Core.Deployment` namespace
2. Implement `UnattendBuilder` class
3. XML generation using `System.Xml`

### Phase 5: Migrate Configuration
1. Create `Better11.Core.Configuration` namespace
2. Use `Microsoft.Extensions.Configuration` for config management
3. Support JSON/TOML configuration files

### Phase 6: Create GUI
1. WPF application with MVVM pattern
2. Main window with application list
3. Install/uninstall buttons
4. Status display

### Phase 7: Remove Python Frontend
1. Delete Python frontend files:
   - `better11/cli.py`
   - `better11/gui.py`
   - `better11/tui.py`
   - `better11/unattend.py`
   - `better11/config.py`
   - `better11/interfaces.py`
   - `better11/application_manager.py`
   - `better11/apps/` directory (keep catalog.json)
   - `better11/media_cli.py` (if exists)

2. Update documentation

## Implementation Details

### Project Structure
```
csharp/
├── Better11.Core/
│   ├── Apps/          # Application management
│   ├── Deployment/    # Unattend generation
│   ├── Configuration/ # Configuration management
│   └── Services/      # Existing services
├── Better11.CLI/      # Command-line interface
└── Better11.GUI/      # WPF GUI
```

### Dependencies
- `System.CommandLine` - CLI parsing
- `System.Text.Json` - JSON handling
- `System.Net.Http` - HTTP downloads
- `System.Security.Cryptography` - Hash/signature verification
- `System.Xml` - XML generation
- `Microsoft.Extensions.Configuration` - Configuration
- `Microsoft.Extensions.Logging` - Logging
- `System.Management.Automation` - PowerShell integration (already used)

### Key Considerations
1. **Backward Compatibility**: Maintain JSON catalog format
2. **State File**: Keep same location (~/.better11/installed.json)
3. **PowerShell Integration**: Continue using PowerShell for system operations
4. **Error Handling**: Comprehensive error handling and logging
5. **Testing**: Unit tests for all components

## Timeline
1. Phase 1-2: Core application management (2-3 hours)
2. Phase 3: CLI implementation (1-2 hours)
3. Phase 4: Unattend generation (1 hour)
4. Phase 5: Configuration (1 hour)
5. Phase 6: GUI (2-3 hours)
6. Phase 7: Cleanup and documentation (1 hour)

**Total Estimated Time**: 8-12 hours

## Success Criteria
- [ ] All CLI commands work identically to Python version
- [ ] GUI provides same functionality as Python GUI
- [ ] Application management fully functional
- [ ] Unattend generation produces identical XML
- [ ] Configuration management works
- [ ] All Python frontend files removed
- [ ] Documentation updated
- [ ] No breaking changes to catalog format or state files
