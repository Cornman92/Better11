# API Reference

Complete API documentation for Better11 modules and functions.

## Table of Contents

- [Application Manager](#application-manager)
  - [better11.apps.manager](#better11appsmanager)
  - [better11.apps.catalog](#better11appscatalog)
  - [better11.apps.models](#better11appsmodels)
  - [better11.apps.download](#better11appsdownload)
  - [better11.apps.verification](#better11appsverification)
  - [better11.apps.runner](#better11appsrunner)
  - [better11.apps.state_store](#better11appsstate_store)
- [System Tools](#system-tools)
  - [system_tools.registry](#system_toolsregistry)
  - [system_tools.bloatware](#system_toolsbloatware)
  - [system_tools.services](#system_toolsservices)
  - [system_tools.performance](#system_toolsperformance)
  - [system_tools.safety](#system_toolssafety)
- [User Interfaces](#user-interfaces)
  - [better11.cli](#better11cli)
  - [better11.gui](#better11gui)

---

## Application Manager

### better11.apps.manager

Main orchestrator for application management.

#### Class: `AppManager`

Coordinates catalog lookup, downloading, verification, and installation.

**Constructor:**

```python
AppManager(
    catalog_path: Path,
    download_dir: Optional[Path] = None,
    state_file: Optional[Path] = None,
    downloader: Optional[AppDownloader] = None,
    verifier: Optional[DownloadVerifier] = None,
    runner: Optional[InstallerRunner] = None
)
```

**Parameters:**
- `catalog_path` (Path): Path to the application catalog JSON file
- `download_dir` (Path, optional): Directory for downloaded installers. Defaults to `~/.better11/downloads`
- `state_file` (Path, optional): Path to installation state file. Defaults to `~/.better11/installed.json`
- `downloader` (AppDownloader, optional): Custom downloader instance
- `verifier` (DownloadVerifier, optional): Custom verifier instance
- `runner` (InstallerRunner, optional): Custom installer runner instance

**Methods:**

##### `list_available() -> List[AppMetadata]`

List all available applications from catalog.

**Returns:** List of AppMetadata objects

**Example:**
```python
manager = AppManager(Path("catalog.json"))
apps = manager.list_available()
for app in apps:
    print(f"{app.app_id}: {app.name} v{app.version}")
```

##### `download(app_id: str) -> Path`

Download an application installer.

**Parameters:**
- `app_id` (str): Application identifier

**Returns:** Path to downloaded installer

**Raises:**
- `KeyError`: If app_id not found in catalog
- `DownloadError`: If download fails

**Example:**
```python
path = manager.download("demo-app")
print(f"Downloaded to {path}")
```

##### `install(app_id: str) -> Tuple[AppStatus, InstallerResult]`

Download, verify, and install an application with dependencies.

**Parameters:**
- `app_id` (str): Application identifier

**Returns:** Tuple of (AppStatus, InstallerResult)

**Raises:**
- `KeyError`: If app_id not found
- `DownloadError`: If download fails
- `VerificationError`: If verification fails
- `DependencyError`: If circular dependency detected

**Example:**
```python
status, result = manager.install("demo-app")
print(f"Installed {status.app_id} v{status.version}")
print(f"Command: {' '.join(result.command)}")
```

##### `uninstall(app_id: str) -> InstallerResult`

Uninstall an installed application.

**Parameters:**
- `app_id` (str): Application identifier

**Returns:** InstallerResult with uninstall details

**Raises:**
- `DependencyError`: If application is required by other installed apps

**Example:**
```python
result = manager.uninstall("demo-app")
print(f"Uninstalled via: {' '.join(result.command)}")
```

##### `status(app_id: Optional[str] = None) -> List[AppStatus]`

Get installation status.

**Parameters:**
- `app_id` (str, optional): Specific application ID, or None for all

**Returns:** List of AppStatus objects

**Example:**
```python
# All applications
all_status = manager.status()

# Specific application
app_status = manager.status("demo-app")
```

##### `summarized_status(app_id: Optional[str] = None) -> List[str]`

Get human-readable status messages.

**Parameters:**
- `app_id` (str, optional): Specific application ID

**Returns:** List of status strings

**Example:**
```python
messages = manager.summarized_status()
for msg in messages:
    print(msg)
```

#### Exception: `DependencyError`

Raised when dependency-related issues occur.

---

### better11.apps.catalog

Application catalog management.

#### Class: `AppCatalog`

Loads and manages application metadata from catalog file.

**Constructor:**

```python
AppCatalog(applications: Iterable[AppMetadata])
```

**Class Methods:**

##### `from_file(path: Path) -> AppCatalog`

Load catalog from JSON file.

**Parameters:**
- `path` (Path): Path to catalog JSON file

**Returns:** AppCatalog instance

**Example:**
```python
catalog = AppCatalog.from_file(Path("catalog.json"))
```

**Methods:**

##### `list_all() -> List[AppMetadata]`

List all applications in catalog.

**Returns:** List of AppMetadata objects

##### `get(app_id: str) -> AppMetadata`

Get metadata for specific application.

**Parameters:**
- `app_id` (str): Application identifier

**Returns:** AppMetadata object

**Raises:**
- `KeyError`: If app_id not found

##### `__contains__(app_id: str) -> bool`

Check if application exists in catalog.

**Parameters:**
- `app_id` (str): Application identifier

**Returns:** True if exists, False otherwise

**Example:**
```python
if "demo-app" in catalog:
    metadata = catalog.get("demo-app")
```

---

### better11.apps.models

Data models for application management.

#### Enum: `InstallerType`

Supported installer types.

**Values:**
- `MSI` - Microsoft Installer (.msi)
- `EXE` - Executable installer (.exe)
- `APPX` - Windows Store App (.appx)

**Class Methods:**

##### `from_filename(filename: str) -> InstallerType`

Determine installer type from filename.

**Parameters:**
- `filename` (str): Installer filename

**Returns:** InstallerType

**Raises:**
- `ValueError`: If unsupported file type

**Example:**
```python
installer_type = InstallerType.from_filename("installer.msi")
# Returns InstallerType.MSI
```

#### Dataclass: `AppMetadata`

Application metadata with verification details.

**Attributes:**
- `app_id` (str): Unique application identifier
- `name` (str): Human-readable application name
- `version` (str): Application version
- `uri` (str): Download URI (HTTP/HTTPS or file://)
- `sha256` (str): SHA-256 hash for verification
- `installer_type` (InstallerType): Type of installer
- `vetted_domains` (List[str]): Approved download domains
- `signature` (str, optional): HMAC-SHA256 signature (base64)
- `signature_key` (str, optional): HMAC key (base64)
- `dependencies` (List[str]): Required application IDs
- `silent_args` (List[str]): Silent installation arguments
- `uninstall_command` (str, optional): Uninstall command

**Methods:**

##### `domain_is_vetted(hostname: str) -> bool`

Check if domain is vetted for downloads.

**Parameters:**
- `hostname` (str): Domain hostname

**Returns:** True if vetted, False otherwise

##### `requires_signature_verification() -> bool`

Check if HMAC signature verification is required.

**Returns:** True if signature and key are present

**Example:**
```python
app = AppMetadata(
    app_id="demo",
    name="Demo App",
    version="1.0",
    uri="https://example.com/demo.msi",
    sha256="abc123...",
    installer_type=InstallerType.MSI,
    vetted_domains=["example.com"]
)

if app.domain_is_vetted("example.com"):
    print("Domain is vetted")
```

#### Dataclass: `AppStatus`

Installation status tracking.

**Attributes:**
- `app_id` (str): Application identifier
- `version` (str): Installed version
- `installer_path` (str): Path to installer file
- `installed` (bool): Installation status
- `dependencies_installed` (List[str]): Installed dependency IDs

---

### better11.apps.download

Application download functionality.

#### Class: `AppDownloader`

Downloads application installers with domain vetting.

**Constructor:**

```python
AppDownloader(
    download_dir: Path,
    catalog_base_dir: Path
)
```

**Parameters:**
- `download_dir` (Path): Directory for downloaded files
- `catalog_base_dir` (Path): Base directory for resolving relative file:// URIs

**Methods:**

##### `download(app: AppMetadata) -> Path`

Download application installer.

**Parameters:**
- `app` (AppMetadata): Application metadata

**Returns:** Path to downloaded installer

**Raises:**
- `DownloadError`: If download fails or domain not vetted

**Example:**
```python
downloader = AppDownloader(
    Path.home() / ".better11" / "downloads",
    Path(".")
)
path = downloader.download(app_metadata)
```

#### Exception: `DownloadError`

Raised when download operations fail.

---

### better11.apps.verification

Download integrity and signature verification.

#### Class: `DownloadVerifier`

Verifies download integrity and HMAC signatures.

**Methods:**

##### `verify_hash(file_path: Path, expected_sha256: str) -> str`

Verify SHA-256 hash of file.

**Parameters:**
- `file_path` (Path): Path to file
- `expected_sha256` (str): Expected hash (hex string)

**Returns:** Actual hash (hex string)

**Raises:**
- `VerificationError`: If hash mismatch

**Example:**
```python
verifier = DownloadVerifier()
actual_hash = verifier.verify_hash(
    Path("installer.msi"),
    "abc123..."
)
```

##### `verify_signature(file_path: Path, signature_b64: str, key_b64: str) -> None`

Verify HMAC-SHA256 signature.

**Parameters:**
- `file_path` (Path): Path to file
- `signature_b64` (str): Base64-encoded HMAC signature
- `key_b64` (str): Base64-encoded HMAC key

**Raises:**
- `VerificationError`: If signature verification fails

##### `verify(metadata: AppMetadata, file_path: Path) -> None`

Verify hash and signature (if required).

**Parameters:**
- `metadata` (AppMetadata): Application metadata
- `file_path` (Path): Path to downloaded file

**Raises:**
- `VerificationError`: If verification fails

**Example:**
```python
verifier = DownloadVerifier()
verifier.verify(app_metadata, Path("installer.msi"))
```

#### Exception: `VerificationError`

Raised when verification fails.

---

### better11.apps.runner

Installer execution with dry-run support.

#### Class: `InstallerRunner`

Executes Windows installers.

**Constructor:**

```python
InstallerRunner(dry_run: bool | None = None)
```

**Parameters:**
- `dry_run` (bool, optional): Enable dry-run mode. Defaults to True on non-Windows

**Methods:**

##### `install(app: AppMetadata, installer_path: Path) -> InstallerResult`

Execute installer.

**Parameters:**
- `app` (AppMetadata): Application metadata
- `installer_path` (Path): Path to installer file

**Returns:** InstallerResult with execution details

**Raises:**
- `InstallerError`: If installation fails

**Example:**
```python
runner = InstallerRunner(dry_run=False)
result = runner.install(app_metadata, Path("installer.msi"))
print(f"Exit code: {result.returncode}")
```

##### `uninstall(app: AppMetadata, installer_path: Path | None) -> InstallerResult`

Execute uninstaller.

**Parameters:**
- `app` (AppMetadata): Application metadata
- `installer_path` (Path, optional): Path to installer (for MSI)

**Returns:** InstallerResult

**Raises:**
- `InstallerError`: If uninstall fails or command not configured

#### Dataclass: `InstallerResult`

Result of installer execution.

**Attributes:**
- `command` (List[str]): Command executed
- `returncode` (int): Exit code
- `stdout` (str): Standard output
- `stderr` (str): Standard error

#### Exception: `InstallerError`

Raised when installer execution fails.

---

### better11.apps.state_store

Installation state persistence.

#### Class: `InstallationStateStore`

Manages persistent installation state.

**Constructor:**

```python
InstallationStateStore(state_file: Path)
```

**Parameters:**
- `state_file` (Path): Path to JSON state file

**Methods:**

##### `mark_installed(app_id: str, version: str, installer_path: Path, dependencies: List[str] = []) -> AppStatus`

Mark application as installed.

**Parameters:**
- `app_id` (str): Application identifier
- `version` (str): Version installed
- `installer_path` (Path): Path to installer
- `dependencies` (List[str]): Installed dependencies

**Returns:** AppStatus object

**Example:**
```python
store = InstallationStateStore(Path("installed.json"))
status = store.mark_installed(
    "demo-app",
    "1.0.0",
    Path("installer.msi"),
    dependencies=["dep-app"]
)
```

##### `mark_uninstalled(app_id: str) -> None`

Mark application as uninstalled.

**Parameters:**
- `app_id` (str): Application identifier

##### `get(app_id: str) -> Optional[AppStatus]`

Get installation status for application.

**Parameters:**
- `app_id` (str): Application identifier

**Returns:** AppStatus or None if not found

##### `list() -> List[AppStatus]`

List all tracked applications.

**Returns:** List of AppStatus objects

---

## System Tools

### system_tools.registry

Windows Registry management.

#### Dataclass: `RegistryTweak`

Represents a registry modification.

**Attributes:**
- `hive` (str): Registry hive (e.g., "HKEY_CURRENT_USER")
- `path` (str): Registry key path
- `name` (str): Value name
- `value` (object): Value data
- `value_type` (int): Registry value type (winreg constants)

**Properties:**

##### `full_path -> str`

Get full registry path.

**Example:**
```python
import winreg

tweak = RegistryTweak(
    hive="HKEY_CURRENT_USER",
    path=r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
    name="HideFileExt",
    value=0,
    value_type=winreg.REG_DWORD
)

print(tweak.full_path)
# Output: HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced
```

#### Function: `apply_tweak`

```python
apply_tweak(tweak: RegistryTweak) -> None
```

Apply a single registry tweak.

**Parameters:**
- `tweak` (RegistryTweak): Registry modification to apply

**Raises:**
- `SafetyError`: If operation fails

#### Function: `apply_tweaks`

```python
apply_tweaks(
    tweaks: Iterable[RegistryTweak],
    *,
    confirm: bool = True,
    create_backup: bool = True,
    create_restore: bool = True,
    input_func = input
) -> None
```

Apply multiple registry tweaks with safeguards.

**Parameters:**
- `tweaks` (Iterable[RegistryTweak]): Registry modifications
- `confirm` (bool): Prompt for user confirmation
- `create_backup` (bool): Backup affected keys
- `create_restore` (bool): Create system restore point
- `input_func` (Callable): Input function for testing

**Raises:**
- `SafetyError`: If operation fails or user cancels

**Example:**
```python
from system_tools.registry import RegistryTweak, apply_tweaks
import winreg

tweaks = [
    RegistryTweak("HKEY_CURRENT_USER", r"Software\...", "Key", 0, winreg.REG_DWORD)
]

apply_tweaks(tweaks, confirm=True, create_backup=True)
```

---

### system_tools.bloatware

Windows bloatware removal.

#### Function: `remove_bloatware`

```python
remove_bloatware(
    packages: Iterable[str],
    *,
    confirm: bool = True,
    input_func = input
) -> None
```

Remove AppX packages.

**Parameters:**
- `packages` (Iterable[str]): Package names to remove
- `confirm` (bool): Prompt for user confirmation
- `input_func` (Callable): Input function for testing

**Raises:**
- `SafetyError`: If operation fails or user cancels

**Example:**
```python
from system_tools.bloatware import remove_bloatware

packages = [
    "Microsoft.BingWeather",
    "Microsoft.BingNews"
]

remove_bloatware(packages, confirm=True)
```

---

### system_tools.services

Windows service management.

#### Dataclass: `ServiceAction`

Windows service action definition.

**Attributes:**
- `name` (str): Service name
- `action` (str): Action to perform ("start", "stop", "enable", "disable")

**Methods:**

##### `command() -> list[str]`

Get command for executing the action.

**Returns:** Command as list of strings

**Example:**
```python
action = ServiceAction(name="WSearch", action="disable")
cmd = action.command()
# Returns: ["sc", "config", "WSearch", "start=", "disabled"]
```

#### Function: `apply_service_actions`

```python
apply_service_actions(
    actions: Iterable[ServiceAction],
    *,
    confirm: bool = True,
    create_restore: bool = True,
    input_func = input
) -> None
```

Apply service modifications.

**Parameters:**
- `actions` (Iterable[ServiceAction]): Service actions to apply
- `confirm` (bool): Prompt for user confirmation
- `create_restore` (bool): Create system restore point
- `input_func` (Callable): Input function for testing

**Raises:**
- `SafetyError`: If operation fails or user cancels

**Example:**
```python
from system_tools.services import ServiceAction, apply_service_actions

actions = [
    ServiceAction(name="WSearch", action="stop"),
    ServiceAction(name="WSearch", action="disable")
]

apply_service_actions(actions, confirm=True)
```

---

### system_tools.performance

Performance optimization presets.

#### Dataclass: `PerformancePreset`

Performance optimization configuration.

**Attributes:**
- `name` (str): Preset name
- `registry_tweaks` (List[RegistryTweak]): Registry modifications
- `service_actions` (List[ServiceAction]): Service changes
- `description` (str): Preset description

**Example:**
```python
preset = PerformancePreset(
    name="Gaming",
    description="Optimize for gaming performance",
    registry_tweaks=[...],
    service_actions=[...]
)
```

#### Function: `apply_performance_preset`

```python
apply_performance_preset(
    preset: PerformancePreset,
    *,
    confirm: bool = True,
    input_func = input
) -> None
```

Apply performance preset.

**Parameters:**
- `preset` (PerformancePreset): Preset to apply
- `confirm` (bool): Prompt for user confirmation
- `input_func` (Callable): Input function for testing

**Raises:**
- `SafetyError`: If operation fails or user cancels

**Example:**
```python
from system_tools.performance import PerformancePreset, apply_performance_preset
from system_tools.registry import RegistryTweak
import winreg

preset = PerformancePreset(
    name="Performance",
    registry_tweaks=[
        RegistryTweak("HKEY_CURRENT_USER", r"...", "Key", 0, winreg.REG_DWORD)
    ]
)

apply_performance_preset(preset, confirm=True)
```

---

### system_tools.safety

Safety utilities and checks.

#### Exception: `SafetyError`

Raised when safety precondition fails.

#### Function: `ensure_windows`

```python
ensure_windows(allow_non_windows: bool = False) -> bool
```

Ensure current platform is Windows. When ``allow_non_windows`` is True, the
function logs a warning and returns ``False`` instead of raising an error so
callers can explicitly permit cross-platform dry runs or CI environments.

**Returns:** ``True`` when Windows is detected, ``False`` when bypassing the
platform check.

**Raises:**
- `SafetyError`: If not running on Windows and ``allow_non_windows`` is False

#### Function: `confirm_action`

```python
confirm_action(
    prompt: str,
    input_func: Callable[[str], str] = input
) -> bool
```

Prompt user for action confirmation.

**Parameters:**
- `prompt` (str): Message to display
- `input_func` (Callable): Input function

**Returns:** True if confirmed, False if cancelled

**Example:**
```python
from system_tools.safety import confirm_action

if confirm_action("Apply these changes?"):
    # Proceed
    pass
```

#### Function: `create_restore_point`

```python
create_restore_point(description: str) -> None
```

Create Windows system restore point.

**Parameters:**
- `description` (str): Restore point description

**Raises:**
- `SafetyError`: If restore point creation fails

#### Function: `backup_registry_key`

```python
backup_registry_key(
    key_path: str,
    destination: Optional[Path] = None
) -> Path
```

Export registry key to file.

**Parameters:**
- `key_path` (str): Registry key path
- `destination` (Path, optional): Backup file path

**Returns:** Path to backup file

**Raises:**
- `SafetyError`: If backup fails

**Example:**
```python
from system_tools.safety import backup_registry_key
from pathlib import Path

backup_path = backup_registry_key(
    r"HKCU\Software\Microsoft\Windows",
    destination=Path("backup.reg")
)
```

---

## User Interfaces

### better11.cli

Command-line interface module.

#### Function: `main`

```python
main(argv: list[str] | None = None) -> int
```

Main CLI entry point.

**Parameters:**
- `argv` (list[str], optional): Command-line arguments

**Returns:** Exit code (0 for success, 1 for error)

**Commands:**
- `list` - List available applications
- `download <app_id>` - Download application
- `install <app_id>` - Install application
- `uninstall <app_id>` - Uninstall application
- `status [app_id]` - Show installation status

**Options:**
- `--catalog PATH` - Path to catalog JSON file

**Example:**
```bash
python -m better11.cli list
python -m better11.cli --catalog custom.json install app-id
```

---

### better11.gui

Graphical user interface module.

#### Class: `AppManagerGUI`

Tkinter-based GUI for application management.

**Constructor:**

```python
AppManagerGUI(manager: AppManager)
```

**Parameters:**
- `manager` (AppManager): AppManager instance

#### Function: `launch_gui`

```python
launch_gui(catalog_path: Path | None = None) -> None
```

Launch the GUI application.

**Parameters:**
- `catalog_path` (Path, optional): Path to catalog file

**Example:**
```python
from better11.gui import launch_gui
from pathlib import Path

launch_gui(Path("catalog.json"))
```

---

## Type Aliases and Constants

### Registry Value Types

From `winreg` module:
- `REG_SZ` - String value
- `REG_DWORD` - 32-bit integer
- `REG_QWORD` - 64-bit integer
- `REG_BINARY` - Binary data
- `REG_MULTI_SZ` - Multiple strings
- `REG_EXPAND_SZ` - Expandable string

### Registry Hives

Common hive names:
- `HKEY_CURRENT_USER` (HKCU)
- `HKEY_LOCAL_MACHINE` (HKLM)
- `HKEY_CLASSES_ROOT` (HKCR)
- `HKEY_USERS` (HKU)
- `HKEY_CURRENT_CONFIG` (HKCC)

---

## Usage Examples

### Complete Application Installation

```python
from pathlib import Path
from better11.apps.manager import AppManager

# Initialize manager
catalog_path = Path("better11/apps/catalog.json")
manager = AppManager(catalog_path)

# List applications
apps = manager.list_available()
print(f"Found {len(apps)} applications")

# Install application
app_id = "demo-app"
status, result = manager.install(app_id)
print(f"Installed: {status.app_id} v{status.version}")

# Check status
app_status = manager.status(app_id)
if app_status[0].installed:
    print("Installation confirmed")

# Uninstall
result = manager.uninstall(app_id)
print(f"Uninstalled successfully")
```

### Complete System Optimization

```python
from system_tools.registry import RegistryTweak, apply_tweaks
from system_tools.services import ServiceAction, apply_service_actions
from system_tools.bloatware import remove_bloatware
import winreg

# Registry tweaks
tweaks = [
    RegistryTweak("HKEY_CURRENT_USER", r"Software\...", "Key", 0, winreg.REG_DWORD)
]
apply_tweaks(tweaks)

# Service management
actions = [
    ServiceAction("WSearch", "disable")
]
apply_service_actions(actions)

# Bloatware removal
packages = ["Microsoft.BingWeather"]
remove_bloatware(packages)

print("System optimized!")
```

---

## Notes

- All system modification functions require Windows and administrator privileges
- File paths should use `pathlib.Path` objects when possible
- Functions that modify the system create automatic backups and restore points
- User confirmation prompts can be disabled for scripting (set `confirm=False`)
- Dry-run mode available for testing (see `InstallerRunner`)

## See Also

- [User Guide](USER_GUIDE.md) - Practical usage examples
- [Architecture](ARCHITECTURE.md) - System design documentation
- [Contributing](CONTRIBUTING.md) - Development guidelines

---

**Last Updated:** December 2025
