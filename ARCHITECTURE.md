# Architecture Documentation

Comprehensive architecture and design documentation for Better11.

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Module Design](#module-design)
4. [Data Flow](#data-flow)
5. [Security Architecture](#security-architecture)
6. [Design Patterns](#design-patterns)
7. [Extension Points](#extension-points)
8. [Future Architecture](#future-architecture)

## Overview

### Project Structure

```
better11/
├── better11/                    # Main application package
│   ├── apps/                   # Application management subsystem
│   │   ├── catalog.py          # Catalog loading and management
│   │   ├── catalog.json        # Application catalog data
│   │   ├── download.py         # Download orchestration
│   │   ├── manager.py          # Main coordinator
│   │   ├── models.py           # Data models
│   │   ├── runner.py           # Installer execution
│   │   ├── samples/            # Sample installers for testing
│   │   ├── state_store.py      # State persistence
│   │   └── verification.py     # Security verification
│   ├── cli.py                  # Command-line interface
│   └── gui.py                  # Graphical user interface
├── src/
│   └── better11/
│       └── application_manager.py  # Media download utility
├── system_tools/               # System enhancement tools
│   ├── bloatware.py            # Bloatware removal
│   ├── performance.py          # Performance presets
│   ├── registry.py             # Registry management
│   ├── safety.py               # Safety utilities
│   ├── services.py             # Service management
│   └── winreg_compat.py        # Windows Registry compatibility
├── tests/                      # Test suite
│   ├── test_application_manager.py
│   ├── test_manager.py
│   └── test_system_tools.py
└── docs/                       # Documentation (you are here)
```

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interfaces                          │
│  ┌──────────────────────┐          ┌──────────────────────┐     │
│  │   CLI (cli.py)       │          │   GUI (gui.py)       │     │
│  │  - argparse          │          │  - Tkinter           │     │
│  │  - commands          │          │  - async operations  │     │
│  └──────────┬───────────┘          └──────────┬───────────┘     │
└─────────────┼──────────────────────────────────┼─────────────────┘
              │                                  │
              └──────────────┬───────────────────┘
                             │
┌─────────────────────────────┼─────────────────────────────────────┐
│                    Core Application Logic                         │
│             ┌───────────────▼──────────────┐                      │
│             │   AppManager (manager.py)    │                      │
│             │  - Orchestration             │                      │
│             │  - Dependency resolution     │                      │
│             └───────┬──────────────────────┘                      │
│                     │                                             │
│      ┌──────────────┼──────────────┬──────────────┐              │
│      │              │              │              │              │
│  ┌───▼────┐   ┌────▼────┐   ┌────▼────┐   ┌─────▼─────┐        │
│  │Catalog │   │Download │   │Verify   │   │ Runner    │        │
│  │        │   │         │   │         │   │           │        │
│  └────────┘   └─────────┘   └─────────┘   └───────────┘        │
│                                                                   │
│             ┌─────────────────────────────┐                      │
│             │  StateStore (state_store.py)│                      │
│             │  - Persistence              │                      │
│             └─────────────────────────────┘                      │
└───────────────────────────────────────────────────────────────────┘
              │
┌─────────────┼─────────────────────────────────────────────────────┐
│        System Tools Layer                                          │
│   ┌─────────▼──────┐  ┌─────────┐  ┌─────────┐  ┌──────────┐     │
│   │  Registry      │  │Bloatware│  │Services │  │Performance│    │
│   │  - Tweaks      │  │- Removal│  │- Control│  │- Presets  │    │
│   └────────┬───────┘  └────┬────┘  └────┬────┘  └─────┬─────┘    │
│            └────────────────┼────────────┼─────────────┘          │
│                        ┌────▼────────────▼──┐                     │
│                        │   Safety Module    │                     │
│                        │ - Backups          │                     │
│                        │ - Restore points   │                     │
│                        │ - Confirmations    │                     │
│                        └────────────────────┘                     │
└───────────────────────────────────────────────────────────────────┘
              │
┌─────────────┼─────────────────────────────────────────────────────┐
│        Windows OS Layer                                            │
│   ┌─────────▼──────┐  ┌─────────┐  ┌─────────┐  ┌──────────┐     │
│   │  winreg        │  │PowerShell│  │sc.exe  │  │msiexec   │    │
│   │  (Registry)    │  │(AppX)    │  │(Service)│  │(Install) │    │
│   └────────────────┘  └──────────┘  └─────────┘  └──────────┘     │
└───────────────────────────────────────────────────────────────────┘
```

## System Architecture

### Layered Architecture

Better11 follows a layered architecture pattern:

1. **Presentation Layer** - User interfaces (CLI, GUI)
2. **Application Layer** - Business logic (AppManager, coordination)
3. **Domain Layer** - Core models and operations
4. **Infrastructure Layer** - System interactions (Windows APIs)

### Component Overview

#### Application Manager Subsystem

**Purpose**: Secure application installation and management

**Components**:
- **AppCatalog**: Loads and validates catalog data
- **AppDownloader**: Downloads installers with domain vetting
- **DownloadVerifier**: Verifies integrity (hash + signature)
- **InstallerRunner**: Executes installers with proper arguments
- **InstallationStateStore**: Persists installation state
- **AppManager**: Orchestrates all components

**Key Design Decisions**:
- Immutable `AppMetadata` dataclass for safety
- Dependency injection for testability
- Recursive dependency resolution
- State persistence in JSON format
- Dry-run mode for cross-platform development

#### System Tools Subsystem

**Purpose**: Safe Windows system modifications

**Components**:
- **Registry Module**: Apply registry tweaks with backups
- **Bloatware Module**: Remove AppX packages
- **Services Module**: Control Windows services
- **Performance Module**: Apply optimization presets
- **Safety Module**: Common safety utilities

**Key Design Decisions**:
- All operations require explicit confirmation
- Automatic restore point creation
- Registry key backups before modifications
- Logging of all operations
- Windows platform validation

## Module Design

### Application Manager Design

#### Catalog System

```python
# Catalog loads applications from JSON
catalog = AppCatalog.from_file(Path("catalog.json"))

# Catalog provides lookup and validation
app = catalog.get("app-id")  # KeyError if not found
if "app-id" in catalog:
    # exists
```

**Design Rationale**:
- JSON format for human readability and easy editing
- Immutable AppMetadata for thread safety
- Uniqueness validation at load time
- Support for file:// and https:// URIs

#### Download System

```python
# Downloader handles both HTTP and file URIs
downloader = AppDownloader(download_dir, catalog_base)
path = downloader.download(app_metadata)
```

**Design Rationale**:
- Domain vetting prevents untrusted sources
- File-based URIs support local testing
- Relative paths resolved against catalog location
- Downloads to consistent directory structure

#### Verification System

```python
# Two-stage verification: hash + optional signature
verifier = DownloadVerifier()
verifier.verify_hash(file_path, expected_hash)
verifier.verify_signature(file_path, signature, key)
```

**Design Rationale**:
- SHA-256 for integrity (always required)
- HMAC-SHA256 for authenticity (optional)
- Constant-time comparison prevents timing attacks
- Streaming reads for memory efficiency

#### Installation System

```python
# Runner abstracts installer differences
runner = InstallerRunner(dry_run=False)
result = runner.install(app, installer_path)
```

**Design Rationale**:
- Supports MSI, EXE, and AppX installers
- Silent installation by default
- Dry-run mode for testing
- Captures stdout/stderr for debugging
- Flexible uninstall command configuration

#### State Management

```python
# State store provides persistent tracking
store = InstallationStateStore(state_file)
status = store.mark_installed(app_id, version, path)
```

**Design Rationale**:
- JSON format for human readability
- Tracks installation status and dependencies
- Prevents uninstalling required dependencies
- User directory storage (~/.better11/)

### System Tools Design

#### Registry Management

```python
# Declarative registry tweaks
tweak = RegistryTweak(hive, path, name, value, value_type)
apply_tweaks([tweak], confirm=True, create_backup=True)
```

**Design Rationale**:
- Dataclass for type safety
- Automatic backup before changes
- Restore point creation
- User confirmation required
- Full path logging

#### Safety-First Design

All system tools follow safety patterns:

1. **Platform Check**: Verify Windows before operations
2. **User Confirmation**: Prompt before destructive actions
3. **Restore Points**: Create before system modifications
4. **Backups**: Export registry keys before changes
5. **Error Handling**: Wrap operations in try/except
6. **Logging**: Record all operations

```python
def safe_operation():
    ensure_windows()  # Platform check
    create_restore_point("Operation")  # Safety
    if not confirm_action("Proceed?"):  # Confirmation
        raise SafetyError("Cancelled")
    backup_registry_key(key_path)  # Backup
    try:
        # Actual operation
        pass
    except Exception as e:
        logger.error("Failed: %s", e)
        raise SafetyError("...") from e
```

## Data Flow

### Application Installation Flow

```
User Request (CLI/GUI)
        ↓
    AppManager.install(app_id)
        ↓
    Check if already installed
        ↓ (not installed)
    Resolve dependencies (recursive)
        ↓
    AppCatalog.get(app_id)
        ↓
    AppDownloader.download(app)
        ↓ (validates domain)
    Download to ~/.better11/downloads/
        ↓
    DownloadVerifier.verify(app, path)
        ↓ (hash + signature)
    InstallerRunner.install(app, path)
        ↓ (silent install)
    InstallationStateStore.mark_installed(...)
        ↓
    Return (AppStatus, InstallerResult)
```

### Registry Tweak Flow

```
User provides RegistryTweak list
        ↓
    apply_tweaks(tweaks)
        ↓
    ensure_windows()
        ↓
    create_restore_point()
        ↓
    confirm_action("Apply tweaks?")
        ↓ (user confirms)
    For each tweak:
        ↓
        backup_registry_key(full_path)
        ↓
        apply_tweak(tweak)
            ↓
            Open/Create registry key
            ↓
            Set value with winreg
            ↓
        Log success/failure
```

## Security Architecture

### Defense in Depth

Better11 implements multiple security layers:

#### Layer 1: Download Security

- **Domain Vetting**: Only download from pre-approved domains
- **HTTPS Enforcement**: Require secure transport for remote downloads
- **URL Validation**: Validate URIs before download

#### Layer 2: Integrity Verification

- **SHA-256 Hashing**: Verify file integrity
- **HMAC Signatures**: Optional cryptographic signatures
- **Constant-Time Comparison**: Prevent timing attacks

#### Layer 3: Execution Safety

- **Silent Installation**: No user interaction required
- **Argument Validation**: Validate installer arguments
- **Dry-Run Mode**: Test without execution
- **Error Capture**: Capture and log errors

#### Layer 4: System Safety

- **Administrator Check**: Require proper privileges
- **Restore Points**: Create before modifications
- **Registry Backups**: Export before changes
- **User Confirmation**: Prompt before destructive actions

### Trust Model

```
┌─────────────────────────────────────────┐
│         Trusted Components              │
│  ┌───────────────────────────────────┐  │
│  │      Catalog Maintainer           │  │
│  │  - Vets applications              │  │
│  │  - Computes hashes                │  │
│  │  - Signs with HMAC (optional)     │  │
│  └───────────┬───────────────────────┘  │
│              │                           │
│              │ catalog.json              │
│              ↓                           │
│  ┌───────────────────────────────────┐  │
│  │        Better11                   │  │
│  │  - Validates catalog              │  │
│  │  - Verifies downloads             │  │
│  │  - Executes safely                │  │
│  └───────────┬───────────────────────┘  │
└──────────────┼───────────────────────────┘
               │
               │ Verified installer
               ↓
    ┌──────────────────────┐
    │   User's System      │
    │  - Receives verified │
    │    installer         │
    └──────────────────────┘
```

**Trust Assumptions**:
1. Catalog maintainer is trusted
2. HTTPS provides transport security
3. SHA-256 is collision-resistant
4. HMAC-SHA256 is unforgeable
5. Windows APIs are trusted

## Design Patterns

### Patterns Used

#### 1. Dependency Injection

```python
class AppManager:
    def __init__(
        self,
        catalog_path: Path,
        downloader: Optional[AppDownloader] = None,
        verifier: Optional[DownloadVerifier] = None,
        runner: Optional[InstallerRunner] = None,
    ):
        self.downloader = downloader or AppDownloader(...)
        self.verifier = verifier or DownloadVerifier()
        self.runner = runner or InstallerRunner()
```

**Benefits**:
- Testability: Inject mocks for testing
- Flexibility: Swap implementations
- Loose coupling: Components independent

#### 2. Strategy Pattern

```python
class InstallerRunner:
    def _install_command(self, app: AppMetadata, path: Path) -> List[str]:
        if app.installer_type == InstallerType.MSI:
            return ["msiexec", "/i", str(path), "/qn"]
        elif app.installer_type == InstallerType.EXE:
            return [str(path)] + app.silent_args
        elif app.installer_type == InstallerType.APPX:
            return ["powershell", "-Command", f"Add-AppxPackage {path}"]
```

**Benefits**:
- Different install strategies per type
- Easy to add new installer types
- Encapsulates algorithm selection

#### 3. Repository Pattern

```python
class InstallationStateStore:
    def mark_installed(self, ...): pass
    def mark_uninstalled(self, ...): pass
    def get(self, app_id): pass
    def list(self): pass
```

**Benefits**:
- Abstracts persistence
- Can swap storage backend
- Centralizes state management

#### 4. Facade Pattern

```python
class AppManager:
    """Facade coordinating multiple subsystems"""
    def install(self, app_id: str):
        app = self.catalog.get(app_id)           # Catalog
        path = self.downloader.download(app)      # Download
        self.verifier.verify(app, path)           # Verification
        result = self.runner.install(app, path)   # Execution
        status = self.state_store.mark_installed(...) # State
        return status, result
```

**Benefits**:
- Simplified interface
- Hides complexity
- Coordinates subsystems

#### 5. Template Method Pattern

```python
def apply_tweaks(tweaks, confirm=True, create_backup=True, create_restore=True):
    # Template method defining algorithm structure
    if create_restore:
        create_restore_point(...)
    if confirm:
        confirm_action(...)
    for tweak in tweaks:
        if create_backup:
            backup_registry_key(...)
        apply_tweak(tweak)  # Actual work
```

**Benefits**:
- Consistent operation flow
- Customizable steps
- Enforces safety practices

## Extension Points

### Adding New Installer Types

1. Add enum value to `InstallerType`
2. Implement install command in `InstallerRunner._install_command()`
3. Implement uninstall command in `InstallerRunner._uninstall_command()`
4. Add test cases

### Adding New System Tools

1. Create new module in `system_tools/`
2. Follow safety pattern:
   - `ensure_windows()`
   - `create_restore_point()`
   - `confirm_action()`
3. Add to `__all__` export
4. Document in API reference

### Custom Verification

```python
class CustomVerifier(DownloadVerifier):
    def verify(self, metadata: AppMetadata, file_path: Path) -> None:
        super().verify(metadata, file_path)
        # Add custom verification
        self.verify_digital_signature(file_path)

manager = AppManager(
    catalog_path,
    verifier=CustomVerifier()
)
```

### Custom State Storage

```python
class DatabaseStateStore(InstallationStateStore):
    def __init__(self, connection_string: str):
        self.db = connect(connection_string)
    
    def mark_installed(self, ...):
        # Store in database
        pass

manager = AppManager(
    catalog_path,
    state_store=DatabaseStateStore("...")
)
```

## Future Architecture

### Planned Enhancements

#### 1. Plugin System

```python
# Future: Plugin architecture
class Better11Plugin:
    def on_install_start(self, app_id): pass
    def on_install_complete(self, app_id): pass
    def on_verify(self, file_path): pass

manager.register_plugin(MyPlugin())
```

#### 2. Async/Await Support

```python
# Future: Async operations
async def install_async(self, app_id: str):
    app = await self.catalog.get_async(app_id)
    path = await self.downloader.download_async(app)
    await self.verifier.verify_async(app, path)
    result = await self.runner.install_async(app, path)
    return result
```

#### 3. Configuration System

```python
# Future: Configuration management
config = Better11Config.load("~/.better11/config.toml")
manager = AppManager.from_config(config)
```

#### 4. Update System

```python
# Future: Application updates
manager.check_updates()  # Check for new versions
manager.update("app-id")  # Update to latest version
manager.auto_update()     # Update all outdated apps
```

#### 5. Rollback System

```python
# Future: Transaction-like rollback
with manager.transaction():
    manager.install("app1")
    manager.install("app2")
    # Automatic rollback on exception
```

### Scalability Considerations

1. **Parallel Downloads**: Download multiple installers concurrently
2. **Caching**: Cache catalog and verification results
3. **Lazy Loading**: Load catalog entries on-demand
4. **Streaming**: Stream large installers without full buffering

## Performance Considerations

### Current Implementation

- **Download**: Streaming to disk (memory efficient)
- **Hashing**: Chunked reading (1MB chunks)
- **State**: JSON file (sufficient for hundreds of apps)
- **Catalog**: Full load (acceptable for small catalogs)

### Optimization Opportunities

1. **Catalog**: Switch to SQLite for large catalogs (1000+ apps)
2. **Downloads**: Parallel downloads for multiple apps
3. **Verification**: Parallel hash computation for multi-file packages
4. **State**: Incremental updates instead of full rewrites

## Testing Architecture

### Test Categories

1. **Unit Tests**: Individual components in isolation
2. **Integration Tests**: Component interactions
3. **System Tests**: End-to-end workflows
4. **Platform Tests**: Windows-specific functionality

### Test Patterns

```python
# Unit test with mocking
@patch('subprocess.run')
def test_install_msi(mock_run):
    runner = InstallerRunner(dry_run=False)
    mock_run.return_value = MagicMock(returncode=0)
    result = runner.install(app, path)
    assert mock_run.called

# Integration test
def test_install_flow():
    manager = AppManager(test_catalog_path)
    status, result = manager.install("test-app")
    assert status.installed
    assert result.returncode == 0
```

## Documentation Architecture

### Documentation Structure

```
docs/
├── README.md              # Project overview
├── INSTALL.md             # Installation guide
├── USER_GUIDE.md          # Usage documentation
├── API_REFERENCE.md       # API documentation
├── ARCHITECTURE.md        # This document
├── CONTRIBUTING.md        # Development guide
├── SECURITY.md            # Security policies
└── CHANGELOG.md           # Version history
```

### Documentation Principles

1. **Layered**: From high-level to detailed
2. **Example-Driven**: Show, don't just tell
3. **Maintained**: Keep in sync with code
4. **Searchable**: Good structure and ToC
5. **Accessible**: Clear language, good formatting

## Conclusion

Better11's architecture emphasizes:

- **Security**: Multiple verification layers
- **Safety**: Backups and confirmation prompts
- **Modularity**: Loosely coupled components
- **Testability**: Dependency injection and mocking
- **Extensibility**: Clear extension points
- **Maintainability**: Clean separation of concerns

The architecture supports the current feature set while providing foundation for future enhancements.

## Related Documents

- [API Reference](API_REFERENCE.md) - Detailed API documentation
- [User Guide](USER_GUIDE.md) - Usage examples and best practices
- [Contributing](CONTRIBUTING.md) - Development guidelines
- [Security](SECURITY.md) - Security policies and practices

---

**Document Version:** 1.0  
**Last Updated:** December 2025
